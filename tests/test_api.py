# API 路由、中间件与异常转换测试。
"""
API 路由测试
测试 app/api/main.py 中的 HTTP 端点、中间件与异常转换
"""

import pytest
from fastapi.testclient import TestClient
from app.api.main import app
from app.exceptions.base import AppError


@pytest.fixture
def client():
    """FastAPI 测试客户端"""
    return TestClient(app)


class TestHealthCheckEndpoint:
    """测试健康检查端点 GET /health"""

    def test_health_check_returns_ok_status(self, client):
        """GET /health 返回成功状态"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_health_check_always_succeeds(self, client):
        """健康检查总是成功"""
        for _ in range(3):
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "ok"


class TestMiddleware:
    """测试中间件功能"""

    def test_trace_id_header_added_to_response(self, client):
        """验证 trace_id 被添加到响应头"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "X-Trace-Id" in response.headers

    def test_trace_id_is_unique_per_request(self, client):
        """未提供 trace_id 时应为每次请求生成新的值"""
        response_1 = client.get("/health")
        response_2 = client.get("/health")

        assert response_1.status_code == 200
        assert response_2.status_code == 200
        assert response_1.headers.get("X-Trace-Id")
        assert response_2.headers.get("X-Trace-Id")
        assert response_1.headers["X-Trace-Id"] != response_2.headers["X-Trace-Id"]

    def test_trace_id_echoes_request_header(self, client):
        """客户端提供 trace_id 时应原样回传"""
        response = client.get("/health", headers={"X-Trace-Id": "trace-test-001"})
        assert response.status_code == 200
        assert response.headers.get("X-Trace-Id") == "trace-test-001"


class TestDetectionEndpoint:
    """测试异常检测端点 POST /v1/detect"""

    def test_detection_request_validation_missing_fields(self, client):
        """缺少必需字段导致验证失败"""
        response = client.post("/v1/detect", json={})
        assert response.status_code == 422

    def test_detection_request_validation_invalid_type(self, client):
        """字段类型不匹配"""
        payload = {
            "task_id": "test-001",
            "asset_id": "asset-001",
            "start_time": "2025-01-01T00:00:00Z",
            "end_time": "2025-01-01T01:00:00Z",
            "parameters": "not-a-dict",
        }
        response = client.post("/v1/detect", json=payload)
        assert response.status_code == 422

    def test_detection_request_with_valid_payload(self, client):
        """发送有效的检测请求"""
        payload = {
            "task_id": "test-001",
            "asset_id": "asset-001",
            "start_time": "2025-01-01T00:00:00Z",
            "end_time": "2025-01-01T01:00:00Z",
            "data_source": "mock",
            "parameters": {"threshold": 0.5, "data": [1.0, 2.0, 3.0]},
        }
        response = client.post("/v1/detect", json=payload)
        assert response.status_code == 200

    def test_detection_response_contains_required_fields(self, client):
        """验证响应包含必需字段"""
        payload = {
            "task_id": "test-002",
            "asset_id": "asset-002",
            "start_time": "2025-01-01T00:00:00Z",
            "end_time": "2025-01-01T01:00:00Z",
            "parameters": {"threshold": 0.5, "data": [1.0, 2.0]},
        }
        response = client.post("/v1/detect", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert "status" in data
        assert data["status"] in ["success", "failed"]


class TestExceptionHandling:
    """测试全局异常处理"""

    def test_app_error_conversion_to_json_response(self, client):
        """AppError 被转换为 JSON 响应"""
        app.add_api_route("/test-error", lambda: (_ for _ in ()).throw(AppError("Test error")), methods=["GET"])

        response = client.get("/test-error")
        assert response.status_code == 500
        data = response.json()
        assert data["code"] == "app_error"
        assert data["message"] == "Test error"
        assert "trace_id" in data


class TestContentNegotiation:
    """测试内容协商"""

    def test_health_check_json_format(self, client):
        """健康检查返回 JSON"""
        response = client.get("/health")
        data = response.json()
        assert isinstance(data, dict)


class TestRouteNotFound:
    """测试不存在的路由"""

    def test_404_for_undefined_route(self, client):
        """访问未定义的路由返回 404"""
        response = client.get("/undefined-route")
        assert response.status_code == 404


class TestHttpMethods:
    """测试 HTTP 方法"""

    def test_post_to_health_endpoint_not_allowed(self, client):
        """健康检查端点不支持 POST"""
        response = client.post("/health")
        assert response.status_code == 405

