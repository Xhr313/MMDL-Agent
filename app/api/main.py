from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config.settings import settings
from app.core.agent import build_graph
from app.exceptions.base import AppError
from app.memory.state import DetectionState
from app.schemas.detection import DetectionResult, DetectionTask
from app.utils.logging import TRACE_ID_HEADER, new_trace_id, set_trace_id, setup_logger

app = FastAPI(title=settings.app_name)

# CORS: allow local frontend to call backend APIs.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger = setup_logger(level=settings.log_level)

@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    """为请求/响应附加 trace_id，并绑定到日志上下文。"""
    trace_id = request.headers.get(TRACE_ID_HEADER) or new_trace_id()
    request.state.trace_id = trace_id
    set_trace_id(trace_id)
    response = await call_next(request)
    response.headers[TRACE_ID_HEADER] = trace_id
    return response

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    """将 AppError 统一转换为标准 JSON 响应，它捕获自定义的 AppError。
    当 Agent 运行出错时，它能保证返回给前端的是格式统一的 JSON(包含错误码、消息和trace_id)"""
    logger.error(f"{exc.code}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message, "trace_id": request.state.trace_id},
    )

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/")
async def root():
    """根路由：返回应用信息与文档链接。"""
    return {
        "app": settings.app_name,
        "version": "0.1.0",
        "message": "后端服务器已经启动成功",
        "docs": "/docs",
        "openapi_schema": "/openapi.json",
    }

@app.post("/v1/detect", response_model=DetectionResult)
async def detect(task: DetectionTask):
    """运行 LangGraph 工作流并返回 DetectionResult。"""
    graph = build_graph()
    state = DetectionState(task=task)
    result_state = await graph.ainvoke(state)

    if isinstance(result_state, dict):
        result = result_state.get("result")
    else:
        result = getattr(result_state, "result", None)

    if result:
        return result

    return DetectionResult(task_id=task.task_id, status="failed", anomalies=[])
