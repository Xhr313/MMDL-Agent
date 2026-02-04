# 文件说明：pytest 全局配置与通用 fixtures。
"""
pytest 配置与全局 fixtures
"""

import pytest
from fastapi.testclient import TestClient
from app.api.main import app


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环（用于异步测试）"""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """FastAPI 测试客户端"""
    return TestClient(app)


@pytest.fixture
def mock_settings():
    """模拟应用设置"""
    from app.config.settings import settings
    return settings