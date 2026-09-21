"""Exam answer SQLAlchemy models."""

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.sql import func

from src.config.database import Base


class AnswerRecord(Base):
    __tablename__ = "answer_records"
    __table_args__ = (
        UniqueConstraint("user_id", "paper_id", "question_id", name="uk_user_paper_question"),
        Index("idx_user_paper", "user_id", "paper_id"),
        Index("idx_question", "question_id"),
        Index("idx_correct", "is_correct"),
        Index("idx_wrong_reason", "wrong_reason"),
        {"comment": "Answer submission records"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Record ID")
    user_id = Column(
        Integer,
        ForeignKey("users.id", name="fk_answer_records_user", ondelete="CASCADE"),
        nullable=False,
        comment="User ID",
    )
    paper_id = Column(
        Integer,
        ForeignKey("papers.id", name="fk_answer_records_paper", ondelete="CASCADE"),
        nullable=False,
        comment="Paper ID",
    )
    question_id = Column(
        Integer,
        ForeignKey("questions.id", name="fk_answer_records_question", ondelete="RESTRICT"),
        nullable=False,
        comment="Question ID",
    )
    user_answer = Column(String(256), nullable=True, comment="Submitted answer")
    is_correct = Column(
        Integer().with_variant(TINYINT(display_width=1), "mysql"),
        nullable=True,
        comment="Whether the submitted answer is correct",
    )
    time_spent = Column(Integer, default=0, comment="Time spent on this question in seconds")
    wrong_reason = Column(
        SAEnum("知识点不会", "粗心大意", "审题错误", "时间不够", "选项混淆", "其他"),
        nullable=True,
        comment="Incorrect-answer reason tag",
    )
    created_at = Column(DateTime, server_default=func.now(), comment="Submission time")

    def __repr__(self):
        return f"<AnswerRecord(id={self.id}, user={self.user_id}, correct={self.is_correct})>"
