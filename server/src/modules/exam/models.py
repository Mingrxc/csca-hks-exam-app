"""答题模块 SQLAlchemy 模型"""

from sqlalchemy import Column, DateTime, Index, Integer, String, UniqueConstraint
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
        {"comment": "答题记录表"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="记录 ID")
    user_id = Column(Integer, nullable=False, comment="用户 ID")
    paper_id = Column(Integer, nullable=False, comment="试卷 ID")
    question_id = Column(Integer, nullable=False, comment="题目 ID")
    user_answer = Column(String(256), nullable=True, comment="用户答案")
    is_correct = Column(
        Integer().with_variant(TINYINT(display_width=1), "mysql"),
        nullable=True,
        comment="是否正确",
    )
    time_spent = Column(Integer, default=0, comment="该题用时（秒）")
    wrong_reason = Column(
        SAEnum("知识点不会", "粗心大意", "审题错误", "时间不够", "选项混淆", "其他"),
        nullable=True,
        comment="错因标签",
    )
    created_at = Column(DateTime, server_default=func.now(), comment="答题时间")

    def __repr__(self):
        return f"<AnswerRecord(id={self.id}, user={self.user_id}, correct={self.is_correct})>"
