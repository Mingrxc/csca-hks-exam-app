"""User module SQLAlchemy models."""
from sqlalchemy import Column, Date, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.sql import func
from src.config.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("idx_users_openid", "openid"),
        Index("idx_users_created", "created_at"),
        {"comment": "Application users"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="User ID")
    openid = Column(String(64), nullable=False, unique=True, comment="WeChat OpenID")
    unionid = Column(String(64), nullable=True, comment="WeChat UnionID for cross-app identity")
    nickname = Column(String(64), default="考霸同学", comment="Display name")
    avatar_url = Column(String(512), nullable=True, comment="Avatar URL")
    target_exam = Column(SAEnum("CSCA", "HKS"), default="CSCA", comment="Primary target exam")
    target_date = Column(Date, nullable=True, comment="Primary target exam date")
    total_questions = Column(Integer, default=0, comment="Total questions answered")
    total_correct = Column(Integer, default=0, comment="Total correct answers")
    streak_days = Column(Integer, default=0, comment="Current study streak in days")
    last_streak_at = Column(Date, nullable=True, comment="Most recent streak date")
    created_at = Column(DateTime, server_default=func.now(), comment="Registration time")
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<User(id={self.id}, nickname={self.nickname})>"


class UserExamTarget(Base):
    __tablename__ = "user_exam_targets"
    __table_args__ = (
        UniqueConstraint("user_id", "exam_type", name="uk_user_exam_target"),
        Index("idx_user_exam_target_user", "user_id"),
        Index("idx_user_exam_target_exam", "exam_type"),
        {"comment": "Per-exam target dates for users"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Record ID")
    user_id = Column(
        Integer,
        ForeignKey("users.id", name="fk_user_exam_targets_user", ondelete="CASCADE"),
        nullable=False,
        comment="User ID",
    )
    exam_type = Column(SAEnum("CSCA", "HKS"), nullable=False, comment="Exam type")
    target_date = Column(Date, nullable=False, comment="Target date for this exam")
    created_at = Column(DateTime, server_default=func.now(), comment="Creation time")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<UserExamTarget(user_id={self.user_id}, exam_type={self.exam_type})>"


class StreakRecord(Base):
    __tablename__ = "streak_records"
    __table_args__ = (
        UniqueConstraint("user_id", "streak_date", name="uk_user_date"),
        Index("idx_streak_user", "user_id"),
        Index("idx_streak_date", "streak_date"),
        {"comment": "Daily study streak records"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Record ID")
    user_id = Column(
        Integer,
        ForeignKey("users.id", name="fk_streak_records_user", ondelete="CASCADE"),
        nullable=False,
        comment="User ID",
    )
    streak_date = Column(Date, nullable=False, comment="Study date")
    question_count = Column(Integer, default=0, comment="Questions answered that day")
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<StreakRecord(user_id={self.user_id}, date={self.streak_date})>"
