from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, Optional
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", ".env.local"), env_file_encoding="utf-8")

    APP_ENV: Literal["development", "testing", "production"] = "development"

    CORS_ORIGINS: str = "*"
    QUESTION_BANK_ROOT: str = str(Path(__file__).resolve().parents[4] / "original_question_bank")
    QUESTION_MEDIA_BASE_URL: str = ""

    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "csca_hks_exam"

    # 保留旧环境文件可包含的 Redis 字段，应用目前没有 Redis 连接。
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    JWT_SECRET_KEY: str = "csca-hks-dev-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 72
    AUTH_ALLOW_DEV_OPENID: bool = True
    DEV_OPENID: str = "dev-openid"

    WX_APPID: str = ""
    WX_SECRET: str = ""
    USER_AVATAR_ROOT: str = str(Path(__file__).resolve().parents[4] / "user_uploads" / "avatars")

    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_MODEL: str = "qwen3.8-27b"
    QWEN_TEMPERATURE: float = 0.3
    QWEN_MAX_TOKENS: int = 1024
    QWEN_TIMEOUT_SECONDS: int = 45

    # 兼容旧环境文件的白名单键，实际管理角色由数据库决定。
    CONTENT_ADMIN_OPENIDS: str = ""

    # 兼容旧环境文件里的对象存储字段，头像目前写入本地目录。
    OSS_ENDPOINT: str = ""
    OSS_BUCKET: str = ""
    OSS_ACCESS_KEY: str = ""
    OSS_SECRET_KEY: str = ""

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


settings = Settings()
