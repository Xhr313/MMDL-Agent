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


@pytest.fixture(autouse=True)
def mock_llm(monkeypatch):
    """测试环境 Mock LLM，避免访问真实网络/消耗额度。"""
    from types import SimpleNamespace

    from app.config.settings import settings
    import app.core.graph as graph_module

    class DummyChatOpenAI:
        def __init__(self, *args, **kwargs):
            pass

        async def ainvoke(self, messages):
            return SimpleNamespace(content="(test) summary")

    old_api_key = settings.openai_api_key
    old_base_url = settings.llm_base_url

    settings.openai_api_key = "test-key"
    settings.llm_base_url = "http://test.local/v1"

    monkeypatch.setattr(graph_module, "ChatOpenAI", DummyChatOpenAI)

    yield

    settings.openai_api_key = old_api_key
    settings.llm_base_url = old_base_url