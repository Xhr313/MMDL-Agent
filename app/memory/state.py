# 短期记忆，决定了 Agent 脑子里能装多少东西
# LangGraph 状态模型定义

from __future__ import annotations

from typing import Annotated, Any, Dict, List, Optional
from operator import add

from pydantic import BaseModel, Field

from app.schemas.detection import DetectionResult, DetectionTask


def merge_context(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """用于 LangGraph 的上下文字段合并函数。

    LangGraph 在多步更新同一字段时会调用此函数，将状态合并。
    对于 dict 类型，这里采用「后写覆盖前写」的简单策略。
    """
    merged = dict(left or {})
    merged.update(right or {})
    return merged


class DetectionState(BaseModel):
    """LangGraph 状态模型，贯穿整个检测流程。"""

    task: DetectionTask

    # context 使用自定义 merge_context 做字典合并
    context: Annotated[Dict[str, Any], merge_context] = Field(default_factory=dict)
    # logs / errors 使用列表相加（append 累积）
    logs: Annotated[List[str], add] = Field(default_factory=list)
    errors: Annotated[List[str], add] = Field(default_factory=list)

    result: Optional[DetectionResult] = None

    # TODO 记录当前执行到了第几步，防止死循环，未设计中断死循环 if
    current_step: int = 0

