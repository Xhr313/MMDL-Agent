# TODO检测任务与结果的 Pydantic 数据模型，定义了检测任务的输入和输出格式（非常重要）
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class DetectionTask(BaseModel):
    """检测任务输入模型"""
    task_id: str = Field(..., description="任务唯一标识符，用于追踪和识别特定的检测任务")
    asset_id: str = Field(..., description="资产或设备标识符，指明要检测的目标资产")
    start_time: str = Field(..., description="开始时间，采用 ISO8601 时间格式，定义检测的时间范围起始点")
    end_time: str = Field(..., description="结束时间，采用 ISO8601 时间格式，定义检测的时间范围结束点")
    data_source: Optional[str] = Field(None, description="数据源名称，可选项，指定用于检测的数据来源")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="参数字典，包含检测任务所需的配置参数和其他自定义参数")

class DetectionResult(BaseModel):
    """检测任务输出模型"""
    task_id: str = Field(..., description="任务ID, 与对应的检测任务关联")
    status: str = Field(..., description="检测状态, 表示任务执行成功('success')或失败('failed')")
    anomalies: List[Dict[str, Any]] = Field(default_factory=list, description="异常列表，包含检测到的所有异常记录，每个异常为字典格式")
    summary: Optional[str] = Field(None, description="检测摘要，可选项，提供检测结果的概要信息")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据字典，包含附加的检测相关信息")

class ToolResponse(BaseModel):
    """工具统一响应模型"""
    tool_name: str = Field(..., description="工具名称，标识执行检测的工具")
    success: bool = Field(..., description="执行成功标志，表示工具是否成功执行")
    result: Optional[DetectionResult] = Field(None, description="检测结果，可选项，包含具体的检测结果数据")
    error: Optional[str] = Field(None, "错误信息，可选项，当执行失败时包含错误描述")

