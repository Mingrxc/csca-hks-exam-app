"""应用配置"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", ".env.local"), env_file_encoding="utf-8")

    # API
    CORS_ORIGINS: str = "*"

    # 数据库
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "csca_hks_exam"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    # JWT
    JWT_SECRET_KEY: str = "csca-hks-dev-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 72
    AUTH_ALLOW_DEV_OPENID: bool = True
    DEV_OPENID: str = "dev-openid"

    # 微信小程序
    WX_APPID: str = ""
    WX_SECRET: str = ""

    # AI
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_MODEL: str = "qwen-plus-2025-07-28"
    QWEN_TEMPERATURE: float = 0.3
    QWEN_MAX_TOKENS: int = 1024
    QWEN_TIMEOUT_SECONDS: int = 45

    # 内容管理
    CONTENT_ADMIN_OPENIDS: str = "dev-openid"

    # 文件存储
    OSS_ENDPOINT: str = ""
    OSS_BUCKET: str = ""
    OSS_ACCESS_KEY: str = ""
    OSS_SECRET_KEY: str = ""

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def content_admin_openids(self) -> list[str]:
        return [openid.strip() for openid in self.CONTENT_ADMIN_OPENIDS.split(",") if openid.strip()]


settings = Settings()
