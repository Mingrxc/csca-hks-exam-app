"""用户模块 SQLAlchemy 模型"""
from sqlalchemy import Column, Date, DateTime, Index, Integer, String, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.sql import func
from src.config.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("idx_users_openid", "openid"),
        Index("idx_users_created", "created_at"),
        {"comment": "用户表"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="用户 ID")
    openid = Column(String(64), nullable=False, unique=True, comment="微信 OpenID")
    unionid = Column(String(64), nullable=True, comment="微信 UnionID（多端互通）")
    nickname = Column(String(64), default="考霸同学", comment="昵称")
    avatar_url = Column(String(512), nullable=True, comment="头像 URL")
    target_exam = Column(SAEnum("CSCA", "HKS"), default="CSCA", comment="目标考试类型")
    target_date = Column(Date, nullable=True, comment="考试日期")
    total_questions = Column(Integer, default=0, comment="累计刷题数")
    total_correct = Column(Integer, default=0, comment="累计正确数")
    streak_days = Column(Integer, default=0, comment="连续打卡天数")
    last_streak_at = Column(Date, nullable=True, comment="最近打卡日期")
    created_at = Column(DateTime, server_default=func.now(), comment="注册时间")
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<User(id={self.id}, nickname={self.nickname})>"


class StreakRecord(Base):
    __tablename__ = "streak_records"
    __table_args__ = (
        UniqueConstraint("user_id", "streak_date", name="uk_user_date"),
        Index("idx_streak_user", "user_id"),
        Index("idx_streak_date", "streak_date"),
        {"comment": "打卡记录表"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="记录 ID")
    user_id = Column(Integer, nullable=False, comment="用户 ID")
    streak_date = Column(Date, nullable=False, comment="打卡日期")
    question_count = Column(Integer, default=0, comment="当日刷题数")
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<StreakRecord(user_id={self.user_id}, date={self.streak_date})>"
