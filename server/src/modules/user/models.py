"""用户模块 SQLAlchemy 模型"""
from sqlalchemy import Column, Integer, String, Date, DateTime, Enum as SAEnum
from sqlalchemy.sql import func
from src.config.database import Base


class User(Base):
    __tablename__ = "users"

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
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )

    def __repr__(self):
        return f"<User(id={self.id}, nickname={self.nickname})>"


class StreakRecord(Base):
    __tablename__ = "streak_records"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="记录 ID")
    user_id = Column(Integer, nullable=False, comment="用户 ID")
    streak_date = Column(Date, nullable=False, comment="打卡日期")
    question_count = Column(Integer, default=0, comment="当日刷题数")
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<StreakRecord(user_id={self.user_id}, date={self.streak_date})>"
