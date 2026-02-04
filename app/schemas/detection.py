# TODO检测任务与结果的 Pydantic 数据模型，定义了检测任务的输入和输出格式（非常重要）
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class DetectionTask(BaseModel):
    """检测任务输入模型"""
    task_id: str = Field(..., description="Unique task identifier")
    asset_id: str = Field(..., description="Asset or equipment identifier")
    start_time: str = Field(..., description="ISO8601 start time")
    end_time: str = Field(..., description="ISO8601 end time")
    data_source: Optional[str] = Field(None, description="Data source name")
    parameters: Dict[str, Any] = Field(default_factory=dict)

class DetectionResult(BaseModel):
    """检测任务输出模型"""
    task_id: str
    status: str = Field(..., description="success|failed")
    anomalies: List[Dict[str, Any]] = Field(default_factory=list)
    summary: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ToolResponse(BaseModel):
    """工具统一响应模型"""
    tool_name: str
    success: bool
    result: Optional[DetectionResult] = None
    error: Optional[str] = None

