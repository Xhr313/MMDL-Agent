from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.config.settings import settings
from app.schemas.detection import DetectionTask, DetectionResult
from app.core.agent import build_graph
from app.memory.state import DetectionState
from app.exceptions.base import AppError
from app.utils.logging import setup_logger, new_trace_id, TRACE_ID_HEADER
from app.utils.logging import set_trace_id

app = FastAPI(title=settings.app_name)

# 基础日志器；trace_id 会在中间件中注入 
logger = setup_logger(level=settings.log_level)

@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    """为请求/响应附加 trace_id，并绑定到日志上下文。"""
    trace_id = request.headers.get(TRACE_ID_HEADER) or new_trace_id()  
    request.state.trace_id = trace_id    #将trace_id保存到request.state中，方便后续异常处理读取
    set_trace_id(trace_id)
    response = await call_next(request)  #程序在这里暂停，把控制权交给下游（可能是下一个中间件，或者是业务代码）
    response.headers[TRACE_ID_HEADER] = trace_id    #下游处理完拿到了 response。在这里给成品盖个章（加上 Header）
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

#TODO 以下均需要根据实际调用情况修改接口
@app.get("/")
async def root():
    """根路由：返回应用信息与文档链接。"""
    return {
        "app": settings.app_name,
        "version": "0.1.0",
        "message": "Welcome to MMDL-Agent",
        "docs": "/docs",
        "openapi_schema": "/openapi.json",
    }

@app.get("/health")
async def health():
    """轻量健康检查接口。"""
    return {"status": "ok"}

@app.post("/v1/detect", response_model=DetectionResult)
async def detect(task: DetectionTask):
    """运行 LangGraph 工作流并返回 DetectionResult。"""
    graph = build_graph()
    state = DetectionState(task=task)
    result_state = await graph.ainvoke(state)
    if result_state.result:
        return result_state.result
    return DetectionResult(task_id=task.task_id, status="failed", anomalies=[])
