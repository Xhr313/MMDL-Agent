# 异常检测工具接口与 Mock 实现。
from __future__ import annotations

from typing import Optional
from app.schemas.detection import DetectionTask, DetectionResult, ToolResponse
from app.exceptions.base import ExternalServiceError

class BaseTool:
    name: str = "base_tool"

    async def run(self, task: DetectionTask) -> ToolResponse:
        """执行工具逻辑并返回标签 ToolResponse"""
        raise NotImplementedError

class MockAnomalyDetectionTool(BaseTool):
    name = "mock_anomaly_detection"

    async def run(self, task: DetectionTask) -> ToolResponse:
        """Mock 异常检测实现，用于联调与测试"""
        result = DetectionResult(
            task_id=task.task_id,
            status="success",
            anomalies=[{"timestamp": task.start_time, "score": 0.82, "type": "spike"}],
            summary=None,
            metadata={"mock": True},
        )
        return ToolResponse(tool_name=self.name, success=True, result=result)

class HttpAnomalyDetectionTool(BaseTool):
    name = "http_anomaly_detection"

    async def run(self, task: DetectionTask) -> ToolResponse:
        # TODO: 通过 httpx 对接外部 HTTP/RPC 服务（禁止直接使用 requests）
        raise ExternalServiceError(message="HTTP anomaly detection service is not available")