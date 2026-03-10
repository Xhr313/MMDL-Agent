# 工作流节点实现：数据加载、异常检测与总结
from __future__ import annotations

import logging

from langchain_openai import ChatOpenAI

from app.config.settings import settings
from app.exceptions.base import ConfigurationError, DataMissingError, ModelError
from app.memory.state import DetectionState
from app.prompts.summarize import SUMMARIZE_PROMPT
from app.tools.anomaly_detection import HttpAnomalyDetectionTool, MockAnomalyDetectionTool

# 创建logger实例
logger = logging.getLogger(__name__)

async def load_data_node(state: DetectionState) -> DetectionState:
    """前置校验，检查任务是否存在。"""
    if not state.task:
        raise DataMissingError("DetectionTask missing")
    state.context["loaded"] = True
    state.logs.append("Data loaded")
    return state

async def anomaly_detect_node(state: DetectionState) -> DetectionState:
    """Todo 选择合适的异常检测工具并执行检测逻辑。"""
    tool_type = state.task.parameters.get("tool_type", "mock")

    if tool_type == "http":
        tool = HttpAnomalyDetectionTool()
    else:
        tool = MockAnomalyDetectionTool()

    response = await tool.run(state.task)
    if response.success and response.result:
        state.result = response.result
        state.logs.append(f"Anomaly detection completed using {tool.name}")
    else:
        state.errors.append(response.error or "Unknown tool error")
    return state

async def summarize_node(state: DetectionState) -> DetectionState:
    """对检测结果进行自然语言总结。

    - 通过 LangChain + qwen生成诊断建议。
    """
    if not state.result:
        state.logs.append("No result to summarize")
        return state

    if not settings.openai_api_key:
        raise ConfigurationError(
            "openai_api_key not configured",
            config_key="APP_OPENAI_API_KEY",
        )

    try:
        llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            api_key=settings.openai_api_key,
            timeout=settings.llm_timeout,
            max_tokens=settings.llm_max_tokens,
            base_url=settings.llm_base_url,
            extra_body={"enable_thinking": False}
            
    )

        messages = SUMMARIZE_PROMPT.format_messages(
            task_id=state.task.task_id,
            asset_id=state.task.asset_id,
            start_time=state.task.start_time,
            end_time=state.task.end_time,
            anomalies=state.result.anomalies,
        )

        response = await llm.ainvoke(messages)
        
        # LangChain 返回的是一个 ChatMessage
        state.result.summary = getattr(response, "content", str(response))
        state.logs.append("LLM summary generated")

    except Exception as e:
        logger.error(f"LLM invocation failed: {str(e)}")  
        raise ModelError(
            message=f"Failed to generate summary: {str(e)}",  # 传递原始错误信息
            model_name=settings.llm_model,
            original_error=e,
        )

    return state