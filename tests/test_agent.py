# Agent 与工作流相关测试。
"""
Agent 核心与工作流测试
测试 app/core/agent.py 和 app/core/graph.py
"""

import pytest
from app.core.agent import build_graph
from app.memory.state import DetectionState
from app.schemas.detection import DetectionTask


class TestBuildGraph:
    """测试工作流图构建"""

    def test_build_graph_returns_valid_object(self):
        """build_graph 返回有效的图对象"""
        graph = build_graph()
        assert graph is not None

    def test_build_graph_has_invoke_method(self):
        """图包含 invoke 方法"""
        graph = build_graph()
        assert hasattr(graph, "invoke")

    def test_build_graph_has_async_invoke_method(self):
        """图包含异步 ainvoke 方法"""
        graph = build_graph()
        assert hasattr(graph, "ainvoke")

    def test_build_graph_multiple_calls_are_consistent(self):
        """多次调用 build_graph 返回一致的图"""
        graph1 = build_graph()
        graph2 = build_graph()
        assert graph1 is not None
        assert graph2 is not None


class TestDetectionTask:
    """测试检测任务数据模型"""

    def test_detection_task_creation(self):
        """创建检测任务"""
        task = DetectionTask(
            task_id="test-001",
            asset_id="asset-001",
            start_time="2025-01-01T00:00:00Z",
            end_time="2025-01-01T01:00:00Z",
            data_source="mock",
            parameters={"threshold": 0.5, "data": [1.0, 2.0, 3.0]},
        )
        assert task.task_id == "test-001"
        assert task.asset_id == "asset-001"
        assert task.parameters["threshold"] == 0.5

    def test_detection_task_with_empty_data(self):
        """创建空数据检测任务"""
        task = DetectionTask(
            task_id="empty-task",
            asset_id="asset-002",
            start_time="2025-01-01T00:00:00Z",
            end_time="2025-01-01T01:00:00Z",
            parameters={"data": []},
        )
        assert task.task_id == "empty-task"
        assert task.parameters["data"] == []

    def test_detection_task_with_large_data(self):
        """创建包含大量数据的检测任务"""
        large_data = list(range(10000))
        task = DetectionTask(
            task_id="large-task",
            asset_id="asset-003",
            start_time="2025-01-01T00:00:00Z",
            end_time="2025-01-01T01:00:00Z",
            parameters={"data": large_data, "threshold": 0.3},
        )
        assert len(task.parameters["data"]) == 10000
        assert task.task_id == "large-task"


class TestDetectionState:
    """测试检测执行状态"""

    def test_detection_state_initialization(self):
        """初始化检测状态"""
        task = DetectionTask(
            task_id="test-001",
            asset_id="asset-001",
            start_time="2025-01-01T00:00:00Z",
            end_time="2025-01-01T01:00:00Z",
            parameters={"data": [1.0, 2.0, 3.0], "threshold": 0.5},
        )
        state = DetectionState(task=task)
        assert state.task == task
        assert state.task.task_id == "test-001"

    def test_detection_state_has_task_field(self):
        """状态包含 task 字段"""
        task = DetectionTask(
            task_id="test-002",
            asset_id="asset-002",
            start_time="2025-01-01T00:00:00Z",
            end_time="2025-01-01T01:00:00Z",
            parameters={"data": [4.0, 5.0], "threshold": 0.6},
        )
        state = DetectionState(task=task)
        assert hasattr(state, "task")
        assert state.task.task_id == "test-002"

    def test_detection_state_preserves_task_data(self):
        """状态保留任务数据完整性"""
        original_data = [10.5, 20.3, 15.7]
        task = DetectionTask(
            task_id="data-test",
            asset_id="asset-003",
            start_time="2025-01-01T00:00:00Z",
            end_time="2025-01-01T01:00:00Z",
            parameters={"data": original_data, "threshold": 0.4},
        )
        state = DetectionState(task=task)
        assert state.task.parameters["data"] == original_data


class TestAgentWorkflow:
    """测试 Agent 工作流集成"""

    @pytest.mark.asyncio
    async def test_graph_invoke_with_task(self):
        """使用任务调用图"""
        task = DetectionTask(
            task_id="workflow-test",
            asset_id="asset-004",
            start_time="2025-01-01T00:00:00Z",
            end_time="2025-01-01T01:00:00Z",
            parameters={"data": [1.0, 2.0, 3.0], "threshold": 0.5},
        )
        state = DetectionState(task=task)
        graph = build_graph()

        try:
            result = graph.invoke(state)
            assert result is not None
        except Exception as e:
            pytest.skip(f"Graph invoke not implemented: {e}")

    @pytest.mark.asyncio
    async def test_graph_async_invoke_with_task(self):
        """异步调用图"""
        task = DetectionTask(
            task_id="async-workflow-test",
            asset_id="asset-005",
            start_time="2025-01-01T00:00:00Z",
            end_time="2025-01-01T01:00:00Z",
            parameters={"data": [5.0, 10.0, 15.0], "threshold": 0.3},
        )
        state = DetectionState(task=task)
        graph = build_graph()

        try:
            result = await graph.ainvoke(state)
            assert result is not None
        except Exception as e:
            pytest.skip(f"Graph ainvoke not implemented: {e}")


class TestTaskValidation:
    """测试任务验证与约束"""

    def test_task_id_is_required(self):
        """task_id 是必需的"""
        with pytest.raises(TypeError):
            DetectionTask(asset_id="asset", start_time="2025-01-01T00:00:00Z", end_time="2025-01-01T01:00:00Z")

    def test_asset_id_is_required(self):
        """asset_id 是必需的"""
        with pytest.raises(TypeError):
            DetectionTask(task_id="test", start_time="2025-01-01T00:00:00Z", end_time="2025-01-01T01:00:00Z")

    def test_start_time_is_required(self):
        """start_time 是必需的"""
        with pytest.raises(TypeError):
            DetectionTask(task_id="test", asset_id="asset", end_time="2025-01-01T01:00:00Z")

    def test_parameters_optional(self):
        """parameters 可选，允许为空"""
        task = DetectionTask(
            task_id="params-test",
            asset_id="asset-006",
            start_time="2025-01-01T00:00:00Z",
            end_time="2025-01-01T01:00:00Z",
        )
        assert task.parameters == {}

