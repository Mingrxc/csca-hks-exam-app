"""Wrong-book SQLAlchemy models."""

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.sql import func

from src.config.database import Base


class WrongBook(Base):
    __tablename__ = "wrong_book"
    __table_args__ = (
        UniqueConstraint("user_id", "question_id", name="uk_user_question"),
        Index("idx_wrongbook_user", "user_id"),
        Index("idx_wrongbook_question", "question_id"),
        Index("idx_wrongbook_mastered", "is_mastered"),
        Index("idx_wrongbook_last_wrong", "last_wrong_at"),
        {"comment": "User wrong-book entries"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Record ID")
    user_id = Column(
        Integer,
        ForeignKey("users.id", name="fk_wrong_book_user", ondelete="CASCADE"),
        nullable=False,
        comment="User ID",
    )
    question_id = Column(
        Integer,
        ForeignKey("questions.id", name="fk_wrong_book_question", ondelete="RESTRICT"),
        nullable=False,
        comment="Question ID",
    )
    wrong_count = Column(Integer, default=1, comment="Cumulative incorrect-answer count")
    correct_count = Column(Integer, default=0, comment="Consecutive correct-answer count")
    is_mastered = Column(
        Integer().with_variant(TINYINT(display_width=1), "mysql"),
        default=0,
        comment="Whether mastered after the required correct-answer streak",
    )
    first_wrong_at = Column(DateTime, server_default=func.now(), comment="First incorrect-answer time")
    last_wrong_at = Column(DateTime, server_default=func.now(), comment="Most recent incorrect-answer time")
    last_review_at = Column(DateTime, nullable=True, comment="Most recent review time")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<WrongBook(id={self.id}, user={self.user_id}, mastered={self.is_mastered})>"


class KnowledgeStat(Base):
    __tablename__ = "knowledge_stats"
    __table_args__ = (
        UniqueConstraint("user_id", "exam_type", "knowledge_point", name="uk_user_exam_point"),
        Index("idx_knowledge_user_exam", "user_id", "exam_type"),
        {"comment": "Knowledge-point performance statistics"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Statistics ID")
    user_id = Column(
        Integer,
        ForeignKey("users.id", name="fk_knowledge_stats_user", ondelete="CASCADE"),
        nullable=False,
        comment="User ID",
    )
    exam_type = Column(SAEnum("CSCA", "HKS"), nullable=False, comment="Exam type")
    knowledge_point = Column(String(64), nullable=False, comment="Knowledge point")
    total_answered = Column(Integer, default=0, comment="Total answers")
    total_correct = Column(Integer, default=0, comment="Total correct answers")
    correct_rate = Column(Float, default=0, comment="Correct answer rate")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<KnowledgeStat(user={self.user_id}, point={self.knowledge_point}, rate={self.correct_rate})>"
