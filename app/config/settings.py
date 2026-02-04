# 配置管理，基于 pydantic-settings 读取环境变量
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")

    # 应用基础配置
    app_name: str = "industrial-anomaly-agent"
    log_level: str = "INFO"
    enable_tracing: bool = False

settings = Settings()

