"""错题本模块 SQLAlchemy 模型"""

from sqlalchemy import Column, DateTime, Float, Index, Integer, String, UniqueConstraint
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
        {"comment": "错题本表"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="记录 ID")
    user_id = Column(Integer, nullable=False, comment="用户 ID")
    question_id = Column(Integer, nullable=False, comment="题目 ID")
    wrong_count = Column(Integer, default=1, comment="累计错误次数")
    correct_count = Column(Integer, default=0, comment="连续正确次数")
    is_mastered = Column(
        Integer().with_variant(TINYINT(display_width=1), "mysql"),
        default=0,
        comment="是否已掌握（连续正确 N 次自动标）",
    )
    first_wrong_at = Column(DateTime, server_default=func.now(), comment="首次错误时间")
    last_wrong_at = Column(DateTime, server_default=func.now(), comment="最近错误时间")
    last_review_at = Column(DateTime, nullable=True, comment="最近复习时间")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<WrongBook(id={self.id}, user={self.user_id}, mastered={self.is_mastered})>"


class KnowledgeStat(Base):
    __tablename__ = "knowledge_stats"
    __table_args__ = (
        UniqueConstraint("user_id", "exam_type", "knowledge_point", name="uk_user_exam_point"),
        Index("idx_knowledge_user_exam", "user_id", "exam_type"),
        {"comment": "知识点统计表"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="统计 ID")
    user_id = Column(Integer, nullable=False, comment="用户 ID")
    exam_type = Column(SAEnum("CSCA", "HKS"), nullable=False, comment="考试类型")
    knowledge_point = Column(String(64), nullable=False, comment="知识点")
    total_answered = Column(Integer, default=0, comment="总答题数")
    total_correct = Column(Integer, default=0, comment="总正确数")
    correct_rate = Column(Float, default=0, comment="正确率")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<KnowledgeStat(user={self.user_id}, point={self.knowledge_point}, rate={self.correct_rate})>"
