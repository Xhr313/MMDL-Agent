# LangChain LLM 集成示例
# 这个文件展示了如何在 summarize_node 中集成 LangChain 调用 LLM

from __future__ import annotations

from app.memory.state import DetectionState
from app.exceptions.base import ModelError, ConfigurationError
from app.config.settings import settings
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

# ============================================================================
# 方式 1: 使用 LangChain OpenAI（推荐）
# ============================================================================

try:
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("langchain-openai not installed, LLM features disabled")


async def summarize_node_with_langchain(state: DetectionState) -> DetectionState:
    """
    使用 LangChain 调用 LLM 生成诊断建议
    
    前置要求：
    1. pip install langchain-openai
    2. 在 .env 中设置：APP_OPENAI_API_KEY=your-api-key
    3. 在 settings.py 中添加 LLM 配置
    """
    if not LANGCHAIN_AVAILABLE:
        logger.warning("LangChain not available, using mock summary")
        return summarize_node_mock(state)
    
    if not state.result:
        state.logs.append("No result to summarize")
        return state
    
    # 检查配置
    api_key = getattr(settings, 'openai_api_key', None)
    if not api_key:
        raise ConfigurationError(
            message="openai_api_key not configured",
            config_key="APP_OPENAI_API_KEY"
        )
    
    try:
        # 初始化 LLM
        llm = ChatOpenAI(
            model=getattr(settings, 'llm_model', 'gpt-4o-mini'),
            temperature=getattr(settings, 'llm_temperature', 0.3),
            api_key=api_key,
            timeout=30.0  # 30秒超时
        )
        
        # 构造 Prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个工业异常检测专家。请根据检测到的异常数据，
生成一段通俗易懂的诊断建议，包括：
1. 异常类型和严重程度
2. 可能的原因分析
3. 建议的处理措施

使用中文回答，语言要专业但易懂。如果未检测到异常，请说明系统运行正常。"""),
            ("user", """检测任务 ID: {task_id}
资产 ID: {asset_id}
时间范围: {start_time} 至 {end_time}

检测到的异常：
{anomalies}

请生成诊断建议。""")
        ])
        
        # 格式化 Prompt
        formatted_prompt = prompt.format_messages(
            task_id=state.task.task_id,
            asset_id=state.task.asset_id,
            start_time=state.task.start_time,
            end_time=state.task.end_time,
            anomalies=str(state.result.anomalies) if state.result.anomalies else "无异常"
        )
        
        logger.info(f"Calling LLM for task {state.task.task_id}")
        
        # 调用 LLM（异步）
        response = await llm.ainvoke(formatted_prompt)
        
        # 更新结果
        state.result.summary = response.content
        state.logs.append("LLM summary generated")
        logger.info(f"LLM summary generated for task {state.task.task_id}")
        
    except Exception as e:
        logger.exception(f"LLM call failed for task {state.task.task_id}")
        raise ModelError(
            message="Failed to generate summary with LLM",
            model_name=getattr(settings, 'llm_model', 'unknown'),
            original_error=e
        )
    
    return state


# ============================================================================
# 方式 2: 直接调用 OpenAI API（不使用 LangChain）
# ============================================================================

try:
    import httpx
    OPENAI_DIRECT_AVAILABLE = True
except ImportError:
    OPENAI_DIRECT_AVAILABLE = False


async def summarize_node_direct_openai(state: DetectionState) -> DetectionState:
    """
    直接调用 OpenAI API（不使用 LangChain）
    
    适用于不想引入 LangChain 依赖的场景
    """
    if not OPENAI_DIRECT_AVAILABLE:
        return summarize_node_mock(state)
    
    if not state.result:
        state.logs.append("No result to summarize")
        return state
    
    api_key = getattr(settings, 'openai_api_key', None)
    if not api_key:
        raise ConfigurationError(
            message="openai_api_key not configured",
            config_key="APP_OPENAI_API_KEY"
        )
    
    try:
        model = getattr(settings, 'llm_model', 'gpt-4o-mini')
        
        # 构造请求
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个工业异常检测专家。请根据检测到的异常数据，生成一段通俗易懂的诊断建议。"
                },
                {
                    "role": "user",
                    "content": f"""检测任务 ID: {state.task.task_id}
资产 ID: {state.task.asset_id}
时间范围: {state.task.start_time} 至 {state.task.end_time}

检测到的异常：
{state.result.anomalies if state.result.anomalies else '无异常'}

请生成诊断建议。"""
                }
            ],
            "temperature": getattr(settings, 'llm_temperature', 0.3),
            "max_tokens": 500
        }
        
        # 调用 OpenAI API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            
            result = response.json()
            summary = result["choices"][0]["message"]["content"]
            
            state.result.summary = summary
            state.logs.append("OpenAI summary generated")
            
    except Exception as e:
        logger.exception(f"OpenAI API call failed")
        raise ModelError(
            message="Failed to generate summary with OpenAI API",
            model_name=model,
            original_error=e
        )
    
    return state


# ============================================================================
# 方式 3: Mock 实现（当前使用的）
# ============================================================================

async def summarize_node_mock(state: DetectionState) -> DetectionState:
    """Mock 实现，用于开发和测试"""
    if state.result:
        if state.result.anomalies:
            state.result.summary = f"检测到 {len(state.result.anomalies)} 个异常点（Mock 总结）"
        else:
            state.result.summary = "未检测到异常（Mock 总结）"
    state.logs.append("Mock summary generated")
    return state


# ============================================================================
# 当前使用的实现（在 graph.py 中）
# ============================================================================

# 在 app/core/graph.py 中，将 summarize_node 替换为：
# from app.core.graph_example import summarize_node_with_langchain as summarize_node
