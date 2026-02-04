# 短期记忆，决定了 Agent 脑子里能装多少东西
# LangGraph 状态模型定义

from __future__ import annotations

from typing import Annotated, List, Optional, Dict, Any
from pydantic import BaseModel, Field
from operator import add
from app.schemas.detection import DetectionTask, DetectionResult


class DetectionState(BaseModel):
    """LangGraph 状态模型，贯穿整个检测流程"""
    task: DetectionTask
    
    # 使用 Annotated[..., add] 使得多步骤的输出可以累加
    context: Annotated[Dict[str, Any], add] = Field(default_factory=dict)
    logs: Annotated[List[str], add] = Field(default_factory=list)
    errors: Annotated[List[str], add] = Field(default_factory=list)
    
    result: Optional[DetectionResult] = None
    
    # TODO 记录当前执行到了第几步，防止死循环，未设计中断死循环if
    current_step: int = 0

