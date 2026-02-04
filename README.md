# MMDL-Agent

一个用于构建多模态/多步骤智能代理（Agent）的框架，集成 LangChain + LangGraph，提供工业级异常处理、记忆管理与工具调用能力。

---

<a id="architecture"></a>

## 🏗️ 项目架构

```
MMDL-Agent/
├── main.py                       # FastAPI 启动入口
├── pyproject.toml                # 项目依赖与构建配置
├── README.md                     # 项目说明文档
├── TESTING.md                    # 测试与 CI 说明
├── tests/                        # 自动化测试用例
│   ├── test_api.py               # API 层测试
│   ├── test_agent.py             # Agent 与工作流测试
│   ├── test_memory.py            # 记忆与检查点测试
│   └── test_exceptions.py        # 异常体系测试
├── web/                          # 前端 Web 界面
│   ├── index.html                # 仪表板主页
│   ├── detection.html            # 检测任务表单页
│   └── assets/                   # 静态资源（CSS/JS）
└── app/                          # 核心后端框架
    ├── api/
    │   └── main.py              # HTTP 路由与中间件
    ├── config/
    │   └── settings.py          # 全局配置（模型、日志、超时等）
    ├── core/
    │   ├── agent.py             # Agent 核心类与执行逻辑
    │   └── graph.py             # LangGraph 工作流定义
    ├── exceptions/
    │   └── base.py              # 统一异常体系（AppError + 子类）
    ├── memory/
    │   ├── state.py             # 执行状态与上下文
    │   └── checkpoint.py        # 检查点与持久化
    ├── prompts/
    │   └── README.md            # 提示词模板说明
    ├── schemas/
    │   └── detection.py         # 数据模型（Pydantic）
    ├── tools/
    │   └── anomaly_detection.py # 异常检测工具实现
    └── utils/
        └── logging.py           # 日志与追踪工具
```

---

## 🛠️ 本地开发环境

### 前置要求

- **Python 3.11+**（Anaconda/Conda）
- **Git**
- **pip**（或 conda）

### 快速开始

#### 1. 克隆项目

```bash
git clone <your-repo-url>
cd MMDL-Agent
```

#### 2. 创建并激活 Python 虚拟环境（推荐 Conda）

如果使用 **Anaconda/Miniconda**：

```bash
conda create -n mmdl-agent python=3.11
conda activate mmdl-agent
```

或使用 **venv**（Python 自带）：

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

#### 3. 安装项目依赖

```bash
pip install -e .
```

或者只安装必要的运行依赖：

```bash
pip install fastapi uvicorn pydantic pydantic-settings python-dotenv langchain langgraph httpx orjson
```

#### 4. 启动 FastAPI 应用

```bash
python -m uvicorn main:app --reload
```

**预期输出：**

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Application startup complete
```

#### 5. 验证服务运行

打开浏览器或使用 curl 验证：

```bash
# 根路由（欢迎页面）
curl http://127.0.0.1:8000/

# 健康检查
curl http://127.0.0.1:8000/health

# API 交互文档
# 浏览器打开 http://127.0.0.1:8000/docs
```

**返回示例：**

```json
{
  "app": "industrial-anomaly-agent",
  "version": "0.1.0",
  "message": "Welcome to MMDL-Agent",
  "docs": "/docs",
  "openapi_schema": "/openapi.json"
}
```

---

## 📋 核心模块说明

| 模块 | 职责 | 关键文件 |
|-----|------|--------|
| **API 层** | HTTP 路由、中间件、异常转换 | `app/api/main.py` |
| **Agent 核心** | 执行流程、状态管理、工具调用 | `app/core/agent.py` |
| **LangGraph** | 工作流定义与执行 | `app/core/graph.py` |
| **异常体系** | 统一异常处理与上下文追踪 | `app/exceptions/base.py` |
| **记忆管理** | 执行状态与检查点持久化 | `app/memory/state.py`, `app/memory/checkpoint.py` |
| **数据模型** | 请求/响应 Pydantic Schema | `app/schemas/detection.py` |
| **日志工具** | 追踪 ID、结构化日志 | `app/utils/logging.py` |
| **测试套件** | 单元测试与集成测试 | `tests/`, `TESTING.md` |
| **Web 前端** | 可视化仪表板与表单 | `web/index.html`, `web/detection.html`, `web/assets/*` |

### 异常体系

项目提供**结构化异常**便于错误处理与追踪：

- `AppError`: 基础异常类（包含 `details`、`original_error`、HTTP 状态码）
- `ModelError`: 模型调用失败
- `ToolError` / `ToolNotFoundError` / `ToolExecutionError`: 工具相关错误
- `ContextError` / `TokenLimitError`: 上下文与 Token 限制
- `MaxTurnsError`: 执行轮次超限
- `ResponseParseError`: 响应解析失败
- `ConfigurationError`: 配置错误
- `StreamError`: 流式处理错误

<a id="detection-algorithm"></a>

### 异常检测算法（概览）

- 客户端或 Web 前端向 `POST /v1/detect` 提交检测任务，请求体会被解析为 `DetectionTask`（见 `app/schemas/detection.py`）。
- Agent 调用在 `app/tools/anomaly_detection.py` 中注册的检测工具（如 `MockAnomalyDetectionTool`，后续可扩展为 `HttpAnomalyDetectionTool` 对接真实服务）。
- 工具返回 `DetectionResult`，其中包含任务状态、异常列表、摘要与元数据，最终被封装为标准 API 响应返回给调用方。

---

## 🚀 开发工作流

### 新增 API 端点

1. 在 `app/schemas/detection.py` 定义请求/响应数据模型
2. 在 `app/api/main.py` 添加路由处理函数
3. 在 `app/core/agent.py` 实现业务逻辑

### 新增工具或模型

1. 在 `app/tools/` 新建工具模块
2. 在 `app/core/agent.py` 注册工具到 Agent
3. 补充单元测试

### 日志与调试

使用 `app/utils/logging.py` 的统一日志接口：

```python
from app.utils.logging import setup_logger

logger = setup_logger(trace_id="custom-trace-id")
logger.info("Processing task")
logger.error("Task failed", extra={"task_id": "123"})
```

### Web 前端

- `web/` 目录提供纯静态 Web 前端，用于与后端 API（如 `/health`、`/v1/detect`）进行交互。
- 推荐使用任意静态文件服务器或 IDE 插件（如 VS Code Live Server）打开 `web/index.html` 进行调试。
- 更详细的前端结构与使用说明见 `web/README.md`。

---

## 🧪 测试与代码检查

```bash
# 安装开发依赖
pip install pytest ruff mypy

# 运行测试
pytest

# 代码风格检查与修复
ruff check --fix

# 类型检查
mypy app/
```

> 更完整的测试说明（覆盖率、并行运行、CI 集成等）请参考根目录下的 `TESTING.md`。

---

## 📖 API 示例

### 1. 健康检查

```bash
GET http://127.0.0.1:8000/health
```

响应：

```json
{ "status": "ok" }
```

### 2. 异常检测

```bash
POST http://127.0.0.1:8000/v1/detect
Content-Type: application/json

{
  "task_id": "task-001",
  "data": [...],
  "threshold": 0.5
}
```

---

## 🐛 常见问题

| 问题 | 解决方案 |
|------|--------|
| `ModuleNotFoundError: No module named 'uvicorn'` | 运行 `pip install uvicorn fastapi` |
| 端口被占用 | 更换端口 `python -m uvicorn main:app --port 8001` |
| Conda 环境激活失败 | 使用 `conda init` 初始化 shell |

---

## 📝 文件说明

- `main.py`: 应用入口（引入 FastAPI 实例）
- `pyproject.toml`: 项目元信息、依赖声明、工具配置
- `app/config/settings.py`: 应用全局配置（模型、超时、日志等）
- `app/api/main.py`: FastAPI 实例创建、路由注册、中间件配置
- `.env` (可选): 环境变量文件（如 API Key、模型选择等）

---
