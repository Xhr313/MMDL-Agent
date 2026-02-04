# 配置扩展示例
# 展示如何在 Settings 类中添加 LLM 和 HTTP 工具的配置
# 你可以将这些配置添加到 app/config/settings.py 中

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类（扩展版本）"""
    
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")

    # ========================================================================
    # 应用基础配置（现有）
    # ========================================================================
    app_name: str = "industrial-anomaly-agent"
    log_level: str = "INFO"
    enable_tracing: bool = False

    # ========================================================================
    # LLM 配置（新增 - 用于 summarize_node）
    # ========================================================================
    
    # OpenAI API Key（必需，如果使用 OpenAI 模型）
    openai_api_key: str = ""
    
    # LLM 模型名称
    # 可选值：gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo 等
    llm_model: str = "gpt-4o-mini"
    
    # LLM 温度参数（0.0-2.0，越高越随机）
    llm_temperature: float = 0.3
    
    # LLM 超时时间（秒）
    llm_timeout: float = 30.0
    
    # LLM 最大 Token 数
    llm_max_tokens: int = 500

    # ========================================================================
    # 异常检测服务配置（新增 - 用于 HttpAnomalyDetectionTool）
    # ========================================================================
    
    # 外部异常检测服务 URL
    # 示例：http://localhost:8080/api 或 https://api.example.com/v1
    anomaly_detection_url: str = ""
    
    # HTTP 请求超时时间（秒）
    anomaly_detection_timeout: float = 30.0
    
    # HTTP 请求重试次数
    anomaly_detection_retries: int = 3

    # ========================================================================
    # 检查点配置（新增 - 用于状态持久化）
    # ========================================================================
    
    # 检查点存储类型：memory, redis, postgres
    checkpoint_store_type: str = "memory"
    
    # Redis 连接 URL（如果使用 Redis 检查点）
    redis_url: str = "redis://localhost:6379/0"
    
    # 检查点过期时间（秒）
    checkpoint_ttl: int = 3600  # 1小时

    # ========================================================================
    # 工作流配置（新增）
    # ========================================================================
    
    # 最大执行轮次（防止死循环）
    max_turns: int = 10
    
    # 是否启用检查点
    enable_checkpoint: bool = False


# 使用示例：
"""
# 在 .env 文件中添加以下配置：

# LLM 配置
APP_OPENAI_API_KEY=sk-your-api-key-here
APP_LLM_MODEL=gpt-4o-mini
APP_LLM_TEMPERATURE=0.3

# 异常检测服务配置
APP_ANOMALY_DETECTION_URL=http://localhost:8080/api
APP_ANOMALY_DETECTION_TIMEOUT=30.0

# 检查点配置
APP_CHECKPOINT_STORE_TYPE=memory
APP_REDIS_URL=redis://localhost:6379/0
APP_ENABLE_CHECKPOINT=true
"""
