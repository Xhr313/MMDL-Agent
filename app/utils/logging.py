# 日志与 trace_id 工具，支持链路追踪。
from __future__ import annotations

import logging
import uuid
from contextvars import ContextVar
from typing import Optional

TRACE_ID_HEADER = "X-Trace-Id"
_trace_id_ctx: ContextVar[Optional[str]] = ContextVar("trace_id", default=None) #确保async环境下，每个并发请求的trace_id都是独立的

class TraceIdFilter(logging.Filter):
    def __init__(self, trace_id: Optional[str] = None) -> None:
        super().__init__()
        self.trace_id = trace_id

    def filter(self, record: logging.LogRecord) -> bool:
        # 将 trace_id 注入日志记录，优先使用上下文中的值      
        ctx_trace_id = _trace_id_ctx.get()
        record.trace_id = ctx_trace_id or self.trace_id or "-"
        return True


def new_trace_id() -> str:
    """生成新的 trace_id"""
    return uuid.uuid4().hex


def setup_logger(name: str = "app", level: str = "INFO", trace_id: Optional[str] = None) -> logging.Logger:
    """创建带 trace_id 的标准日志器（如已存在则复用）"""
    #TODO 待验证，实际输出应为：2025-10-27 10:00:00 INFO [trace_id=f7a1b2c3] app: 开始进行工业振动数据分析...
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s [trace_id=%(trace_id)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        handler.addFilter(TraceIdFilter(trace_id))
        logger.addHandler(handler)
    return logger


def set_trace_id(trace_id: Optional[str]) -> None:
    """设置当前上下文的 trace_id"""
    _trace_id_ctx.set(trace_id)

