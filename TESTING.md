# MMDL-Agent 测试文档

本文档提供完整的测试指南，包括测试框架、运行方法、覆盖率目标与最佳实践。

---

## 📦 测试环境准备

### 前置要求

- Python 3.11+
- pytest 与相关插件
- FastAPI 测试工具

### 安装测试依赖

```bash
# 安装基础测试框架
pip install pytest pytest-asyncio pytest-cov

# 安装 HTTP 测试客户端
pip install httpx

# 安装代码质量检查工具（可选）
pip install ruff mypy pytest-xdist
```

或直接安装项目开发依赖：

```bash
pip install -e ".[dev]"
```

---

## 📁 测试目录结构

```
MMDL-Agent/
├── tests/                        # 测试套件根目录
│   ├── __init__.py              # 包标记
│   ├── conftest.py              # pytest 全局配置与 fixtures
│   ├── test_exceptions.py       # 异常系统测试
│   ├── test_api.py              # API 路由与中间件测试
│   ├── test_agent.py            # Agent 核心与工作流测试
│   ├── test_memory.py           # 记忆与状态管理测试
│   └── integration/             # 集成测试目录（可选）
│       ├── __init__.py
│       └── test_workflow.py     # 端到端工作流测试
└── TESTING.md                    # 本文档
```

---

## 🧪 测试文件说明

### 1. `test_exceptions.py` - 异常系统测试

**覆盖范围：** `app/exceptions/base.py`

**测试类：**
- `TestAppError`: 基础异常与错误码
- `TestModelError`: 模型调用错误
- `TestToolError`: 工具系列错误（包括 ToolNotFoundError、ToolExecutionError）
- `TestContextError`: 上下文错误
- `TestTokenLimitError`: Token 限制检测
- `TestMaxTurnsError`: 执行轮次超限
- `TestResponseParseError`: 响应解析失败
- `TestConfigurationError`: 配置错误
- `TestStreamError`: 流式处理错误
- `TestCreateErrorWithContext`: 上下文错误创建工具

**关键测试场景：**
- 异常创建与字段验证
- 异常链传递（original_error）
- 详情字典与响应转换
- 字符串表示与日志输出

### 2. `test_api.py` - API 路由测试

**覆盖范围：** `app/api/main.py`

**测试类：**
- `TestRootEndpoint`: 根路由 (`GET /`)
- `TestHealthCheckEndpoint`: 健康检查 (`GET /health`)
- `TestMiddleware`: 中间件功能（trace_id、日志绑定）
- `TestDetectionEndpoint`: 异常检测端点 (`POST /v1/detect`)
- `TestExceptionHandling`: 全局异常转换
- `TestContentNegotiation`: 内容协商
- `TestRouteNotFound`: 404 处理
- `TestHttpMethods`: HTTP 方法验证

**关键测试场景：**
- 端点可访问性与响应格式
- 请求验证（缺失字段、类型错误）
- 异常转换为 JSON 响应
- HTTP 状态码正确性
- 中间件链执行

### 3. `test_agent.py` - Agent 核心测试

**覆盖范围：** `app/core/agent.py`、`app/core/graph.py`、`app/schemas/detection.py`

**测试类：**
- `TestBuildGraph`: 工作流图构建
- `TestDetectionTask`: 检测任务数据模型
- `TestDetectionState`: 执行状态管理
- `TestAgentWorkflow`: 工作流集成
- `TestTaskValidation`: 任务验证与约束

**关键测试场景：**
- 图对象创建与方法可用性
- 任务参数验证
- 状态初始化与字段完整性
- 异步工作流调用
- 数据传递与变换

### 4. `test_memory.py` - 记忆模块测试

**覆盖范围：** `app/memory/state.py`、`app/memory/checkpoint.py`

**测试类：**
- `TestDetectionState`: 状态初始化与持久化
- `TestDetectionResult`: 结果数据模型
- `TestMemoryCheckpoint`: 检查点保存与恢复
- `TestStateTransitions`: 状态转换流程
- `TestMemoryOptimization`: 内存管理

**关键测试场景：**
- 状态与任务关联
- 结果生成与异常信息存储
- 检查点序列化与反序列化
- 状态生命周期管理
- 大型数据处理与内存效率

---

## 🚀 运行测试

### 1. 运行所有测试

```bash
# 基础运行（不输出详情）
pytest

# 显示详细信息
pytest -v

# 显示打印语句与日志
pytest -s

# 显示最慢的 10 个测试
pytest --durations=10
```

### 2. 运行特定测试文件

```bash
# 仅测试异常系统
pytest tests/test_exceptions.py -v

# 仅测试 API
pytest tests/test_api.py -v

# 仅测试 Agent
pytest tests/test_agent.py -v

# 仅测试记忆模块
pytest tests/test_memory.py -v
```

### 3. 运行特定测试类或函数

```bash
# 运行单个测试类
pytest tests/test_exceptions.py::TestAppError -v

# 运行单个测试函数
pytest tests/test_exceptions.py::TestAppError::test_app_error_creation_with_message -v

# 运行所有包含 "error" 的测试
pytest tests/ -k "error" -v

# 运行所有包含 "token" 的测试
pytest tests/ -k "token" -v
```

### 4. 生成覆盖率报告

```bash
# 生成覆盖率并显示总结
pytest --cov=app --cov-report=term-missing

# 生成 HTML 覆盖率报告
pytest --cov=app --cov-report=html

# 查看报告（使用浏览器打开）
# htmlcov/index.html
```

### 5. 并行运行测试（加速）

```bash
# 需要先安装 pytest-xdist
pip install pytest-xdist

# 使用 4 个 worker 并行执行
pytest -n 4

# 自动检测 CPU 核数
pytest -n auto
```

### 6. 运行异步测试

```bash
# 仅运行异步测试
pytest tests/ -m asyncio -v

# 显示异步测试详情
pytest tests/test_agent.py -v -s
```

### 7. 调试模式

```bash
# 遇到失败时进入 pdb 调试器
pytest --pdb tests/test_exceptions.py

# 进入调试器后的常用命令
# n: 执行下一行
# c: 继续执行
# l: 显示代码
# p <var>: 打印变量值
```

---

## ✅ 测试清单

### 异常系统测试

- [x] AppError 基础创建与字段验证
- [x] 异常链传递（original_error）
- [x] ModelError 创建与模型名存储
- [x] ToolError 与工具参数记录
- [x] ToolNotFoundError 与 ToolExecutionError
- [x] ContextError 与 TokenLimitError
- [x] MaxTurnsError 轮次检测
- [x] ResponseParseError 与响应截断
- [x] ConfigurationError 配置键管理
- [x] StreamError 流式处理错误
- [x] create_error_with_context 工具函数

### API 路由测试

- [x] 根路由返回欢迎信息
- [x] 健康检查端点响应
- [x] Trace ID 中间件注入
- [x] 异常转换为 JSON 响应
- [x] 请求验证（缺失字段、类型错误）
- [x] 检测端点功能
- [x] 404 处理
- [x] HTTP 方法验证

### Agent 工作流测试

- [x] 工作流图构建
- [x] 图的 invoke/ainvoke 方法可用性
- [x] DetectionTask 创建与验证
- [x] DetectionState 初始化与持久化
- [x] 大型数据处理
- [x] 异步工作流调用

### 记忆模块测试

- [x] 状态初始化与任务关联
- [x] 结果生成与存储
- [x] 检查点保存与恢复
- [x] 状态转换（pending → completed/failed）
- [x] 大型数据处理与内存效率

---

## 🔧 持续集成（CI/CD）

### GitHub Actions 工作流示例

创建 `.github/workflows/test.yml`：

```yaml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      
      - name: Run tests with coverage
        run: |
          pytest --cov=app --cov-report=xml --cov-report=term-missing
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          fail_ci_if_error: true
```

---

## 🐛 调试与故障排除

### 常见问题

| 问题 | 解决方案 |
|------|--------|
| `ModuleNotFoundError: No module named 'pytest'` | 运行 `pip install pytest` |
| `RuntimeError: Event loop is closed` | 使用 `@pytest.mark.asyncio` 标记异步测试 |
| 测试找不到 app 模块 | 确保在项目根目录运行测试，或设置 `PYTHONPATH` |
| 异步测试超时 | 增加超时时间或检查 fixture 配置 |
| 测试相互影响 | 使用 fixture 进行隔离，确保状态独立 |

### 使用 pytest 调试技巧

```bash
# 1. 进入调试器（遇到失败时）
pytest --pdb tests/test_exceptions.py

# 2. 显示所有打印和日志
pytest -s -v tests/test_api.py

# 3. 显示慢速测试
pytest --durations=10

# 4. 只运行前 3 个失败的测试后停止
pytest -x --maxfail=3

# 5. 重新运行上次失败的测试
pytest --lf

# 6. 显示局部变量（进阶）
pytest --pdb --pdbcls=IPython.terminal.debugger:TerminalPdb
```

---

## 📚 最佳实践

### 1. 编写有效的测试

```python
# ✓ 好的测试
def test_app_error_with_details():
    """创建异常并验证详情"""
    error = AppError("test", details={"key": "value"})
    assert error.details["key"] == "value"

# ✗ 不好的测试
def test_error():
    """测试错误"""
    error = AppError("test")
    assert error is not None  # 太宽泛
```

### 2. 使用清晰的测试名称

```python
# ✓ 清晰
def test_token_limit_error_shows_current_and_max_tokens():
    pass

# ✗ 不清晰
def test_token():
    pass
```

### 3. 使用 Fixtures 进行隔离

```python
@pytest.fixture
def sample_task():
    """提供示例任务"""
    return DetectionTask(
        task_id="test-001",
        data=[1.0, 2.0],
        threshold=0.5
    )

def test_with_fixture(sample_task):
    state = DetectionState(task=sample_task)
    assert state.task.task_id == "test-001"
```

### 4. 参数化测试

```python
@pytest.mark.parametrize("status", ["completed", "failed", "pending"])
def test_result_status(status):
    result = DetectionResult(
        task_id="test",
        status=status,
        anomalies=[]
    )
    assert result.status == status
```

---

## 📖 参考资源

- [pytest 官方文档](https://docs.pytest.org/)
- [FastAPI 测试指南](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [pytest-asyncio 文档](https://github.com/pytest-dev/pytest-asyncio)
- [pytest-cov 文档](https://pytest-cov.readthedocs.io/)
- [Coverage.py 文档](https://coverage.readthedocs.io/)

---

## 🎯 后续步骤

1. **运行初始测试：** `pytest tests/test_exceptions.py -v` 验证环境
2. **生成覆盖率报告：** `pytest --cov=app --cov-report=html`
3. **修补失败测试：** 根据实现调整测试代码
4. **设置 CI/CD：** 在版本控制中集成测试流程
5. **持续改进：** 随着功能增加，不断补充测试

---

**Happy Testing! 🚀**
