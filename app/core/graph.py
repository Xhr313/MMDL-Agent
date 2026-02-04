# 工作流节点实现：数据加载、异常检测与总结
from __future__ import annotations

from app.memory.state import DetectionState
from app.tools.anomaly_detection import MockAnomalyDetectionTool
from app.exceptions.base import DataMissingError

# 前置校验，检查任务是否存在
async def load_data_node(state: DetectionState) -> DetectionState:
    # 模拟数据加载
    if not state.task:
        raise DataMissingError("DetectionTask missing")
    state.context["loaded"] = True
    state.logs.append("Data loaded")
    return state

# 实例化调用工具Tool，执行工具逻辑，并返回结果
async def anomaly_detect_node(state: DetectionState) -> DetectionState:
    tool = MockAnomalyDetectionTool()
    response = await tool.run(state.task)
    if response.success and response.result:
        state.result = response.result
        state.logs.append("Anomaly detection completed")
    else:
        state.errors.append(response.error or "Unknown tool error")
    return state

# TODO 对结果进行润色，调用LLM，根据异常点的数据写一段通俗易懂的诊断建议
async def summarize_node(state: DetectionState) -> DetectionState:
    # 模拟 LLM 总结
    if state.result:
        state.result.summary = "No critical anomalies detected (mock summary)."
    state.logs.append("Summary generated")
    return state

