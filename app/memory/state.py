# LangGraph 状态模型定义
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.detection import DetectionTask, DetectionResult

class DetectionState(BaseModel):
    """LangGraph 状态模型，贯穿整个检测流程"""
    task: DetectionTask
    context: dict = Field(default_factory=dict)
    result: Optional[DetectionResult] = None
    errors: List[str] = Field(default_factory=list)
    logs: List[str] = Field(default_factory=list)

