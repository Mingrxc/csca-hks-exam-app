"""答题模块 SQLAlchemy 模型"""

from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum
from sqlalchemy.sql import func

from src.config.database import Base


class AnswerRecord(Base):
    __tablename__ = "answer_records"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="记录 ID")
    user_id = Column(Integer, nullable=False, comment="用户 ID")
    paper_id = Column(Integer, nullable=False, comment="试卷 ID")
    question_id = Column(Integer, nullable=False, comment="题目 ID")
    user_answer = Column(String(256), nullable=True, comment="用户答案")
    is_correct = Column(Integer, nullable=True, comment="是否正确")
    time_spent = Column(Integer, default=0, comment="该题用时（秒）")
    wrong_reason = Column(
        SAEnum("知识点不会", "粗心大意", "审题错误", "时间不够", "选项混淆", "其他"),
        nullable=True,
        comment="错因标签",
    )
    created_at = Column(DateTime, server_default=func.now(), comment="答题时间")

    def __repr__(self):
        return f"<AnswerRecord(id={self.id}, user={self.user_id}, correct={self.is_correct})>"
