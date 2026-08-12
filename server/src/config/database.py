"""数据库连接配置"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .settings import settings

DATABASE_URL = (
    f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
    f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
    f"?charset=utf8mb4"
)

# 同步引擎（用于 Alembic 迁移）
sync_url = DATABASE_URL.replace("mysql+aiomysql://", "mysql+pymysql://")
sync_engine = create_engine(sync_url, pool_pre_ping=True)

Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
