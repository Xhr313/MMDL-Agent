from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate


SUMMARIZE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "你是一名工业设备异常检测专家，需要根据异常检测结果为运维工程师生成诊断建议。\n"
                "请使用专业但易懂的中文，结构清晰，包含：\n"
                "1. 异常类型和严重程度\n"
                "2. 可能的原因分析\n"
                "3. 建议的排查和处理措施\n"
            ),
        ),
        (
            "user",
            (
                "检测任务 ID: {task_id}\n"
                "资产 ID: {asset_id}\n"
                "时间范围: {start_time} 至 {end_time}\n\n"
                "检测到的异常数据（JSON）：\n"
                "{anomalies}\n\n"
                "请基于以上信息生成一段诊断建议。"
            ),
        ),
    ]
)

