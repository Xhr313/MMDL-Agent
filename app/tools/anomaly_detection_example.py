# 异常检测工具实现示例
# 这个文件展示了如何实现真实的 HTTP 工具，可以作为参考

from __future__ import annotations

import httpx
from typing import Optional
from app.schemas.detection import DetectionTask, DetectionResult, ToolResponse
from app.exceptions.base import ExternalServiceError, ToolExecutionError, ConfigurationError
from app.config.settings import settings
from app.tools.anomaly_detection import BaseTool
from app.utils.logging import setup_logger

logger = setup_logger(__name__)


class HttpAnomalyDetectionTool(BaseTool):
    """
    通过 HTTP 调用外部异常检测服务的完整实现示例
    
    使用方法：
    1. 在 .env 文件中设置：APP_ANOMALY_DETECTION_URL=http://your-service:8080/api
    2. 在 graph.py 的 anomaly_detect_node 中实例化并使用
    """
    
    name = "http_anomaly_detection"
    
    def __init__(self, service_url: Optional[str] = None, timeout: float = 30.0):
        """
        初始化 HTTP 工具
        
        参数:
        - service_url: 外部服务 URL（优先使用参数，其次从 settings 读取）
        - timeout: 请求超时时间（秒）
        """
        self.service_url = service_url or getattr(settings, 'anomaly_detection_url', None)
        if not self.service_url:
            raise ConfigurationError(
                message="anomaly_detection_url not configured",
                config_key="APP_ANOMALY_DETECTION_URL"
            )
        self.timeout = timeout
        logger.info(f"Initialized {self.name} with URL: {self.service_url}")
    
    async def run(self, task: DetectionTask) -> ToolResponse:
        """
        调用外部 HTTP 服务执行异常检测
        
        参数:
        - task: 检测任务对象
        
        返回:
        - ToolResponse: 统一的工具响应格式
        """
        try:
            # 构造请求体
            payload = {
                "task_id": task.task_id,
                "asset_id": task.asset_id,
                "start_time": task.start_time,
                "end_time": task.end_time,
                "data_source": task.data_source,
                "data": task.parameters.get("data", []),  # 从 parameters 中提取数据
                "threshold": task.parameters.get("threshold", 0.5),
                "parameters": task.parameters  # 传递所有额外参数
            }
            
            logger.info(f"Calling {self.name} for task {task.task_id}")
            
            # 使用 httpx 发送异步 HTTP 请求
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.service_url}/detect",
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "MMDL-Agent/0.1.0"
                    }
                )
                
                # 检查 HTTP 状态码
                response.raise_for_status()
                
                # 解析 JSON 响应
                result_data = response.json()
                
                # 构造 DetectionResult
                result = DetectionResult(
                    task_id=result_data.get("task_id", task.task_id),
                    status=result_data.get("status", "success"),
                    anomalies=result_data.get("anomalies", []),
                    summary=result_data.get("summary"),
                    metadata={
                        **result_data.get("metadata", {}),
                        "tool": self.name,
                        "service_url": self.service_url
                    }
                )
                
                logger.info(f"{self.name} completed successfully for task {task.task_id}")
                
                return ToolResponse(
                    tool_name=self.name,
                    success=True,
                    result=result
                )
                
        except httpx.HTTPStatusError as e:
            # HTTP 状态码错误（4xx, 5xx）
            error_msg = f"HTTP service returned {e.response.status_code}"
            logger.error(f"{self.name} failed: {error_msg}", extra={
                "task_id": task.task_id,
                "status_code": e.response.status_code,
                "response_body": e.response.text[:500]  # 限制日志长度
            })
            
            raise ExternalServiceError(
                message=error_msg,
                details={
                    "url": self.service_url,
                    "status_code": e.response.status_code,
                    "response_preview": e.response.text[:200]
                },
                original_error=e
            )
            
        except httpx.TimeoutException as e:
            # 请求超时
            error_msg = f"Request timeout after {self.timeout}s"
            logger.error(f"{self.name} timeout: {error_msg}", extra={"task_id": task.task_id})
            
            raise ExternalServiceError(
                message=error_msg,
                details={"url": self.service_url, "timeout": self.timeout},
                original_error=e
            )
            
        except httpx.RequestError as e:
            # 网络连接错误
            error_msg = f"Failed to connect to detection service"
            logger.error(f"{self.name} connection error: {error_msg}", extra={
                "task_id": task.task_id,
                "error": str(e)
            })
            
            raise ExternalServiceError(
                message=error_msg,
                details={"url": self.service_url},
                original_error=e
            )
            
        except Exception as e:
            # 其他未预期的错误
            error_msg = f"Unexpected error in {self.name}"
            logger.exception(f"{self.name} unexpected error", extra={"task_id": task.task_id})
            
            raise ToolExecutionError(
                tool_name=self.name,
                arguments={"task_id": task.task_id, "asset_id": task.asset_id},
                error=e
            )


# 使用示例（在 graph.py 中）：
"""
from app.tools.anomaly_detection_example import HttpAnomalyDetectionTool

async def anomaly_detect_node(state: DetectionState) -> DetectionState:
    # 根据配置选择工具
    tool_type = state.task.parameters.get("tool_type", "mock")
    
    if tool_type == "http":
        try:
            tool = HttpAnomalyDetectionTool()
        except ConfigurationError:
            # 如果未配置 URL，回退到 Mock 工具
            logger.warning("HTTP tool not configured, using mock")
            tool = MockAnomalyDetectionTool()
    else:
        tool = MockAnomalyDetectionTool()
    
    response = await tool.run(state.task)
    if response.success and response.result:
        state.result = response.result
        state.logs.append(f"Anomaly detection completed using {tool.name}")
    else:
        state.errors.append(response.error or "Unknown tool error")
    return state
"""
