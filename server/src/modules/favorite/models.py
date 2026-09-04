"""收藏模块 SQLAlchemy 模型"""

from sqlalchemy import Column, DateTime, Index, Integer, String, UniqueConstraint
from sqlalchemy.sql import func

from src.config.database import Base


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "question_id", name="uk_user_favorite_question"),
        Index("idx_favorites_user", "user_id"),
        Index("idx_favorites_question", "question_id"),
        Index("idx_favorites_created", "created_at"),
        {"comment": "收藏题目表"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="收藏 ID")
    user_id = Column(Integer, nullable=False, comment="用户 ID")
    question_id = Column(Integer, nullable=False, comment="题目 ID")
    note = Column(String(256), nullable=True, comment="收藏备注")
    created_at = Column(DateTime, server_default=func.now(), comment="收藏时间")

    def __repr__(self):
        return f"<Favorite(id={self.id}, user={self.user_id}, question={self.question_id})>"

