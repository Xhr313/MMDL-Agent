# 配置管理，基于 pydantic-settings 读取环境变量
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict

# 自动去寻找配置，优先级为：环境变量 > .env 文件 > 代码默认值
# 后期如果要对接新的第三方算法 URL，只需要在Settings类里加一行，更新 .env 即可
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")

    # 应用基础配置
    app_name: str = "industrial-anomaly-agent"
    log_level: str = "INFO"
    enable_tracing: bool = False

settings = Settings()

