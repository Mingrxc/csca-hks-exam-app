"""Favorite-question SQLAlchemy models."""

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.sql import func

from src.config.database import Base


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "question_id", name="uk_user_favorite_question"),
        Index("idx_favorites_user", "user_id"),
        Index("idx_favorites_question", "question_id"),
        Index("idx_favorites_created", "created_at"),
        {"comment": "User favorite questions"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Favorite ID")
    user_id = Column(
        Integer,
        ForeignKey("users.id", name="fk_favorites_user", ondelete="CASCADE"),
        nullable=False,
        comment="User ID",
    )
    question_id = Column(
        Integer,
        ForeignKey("questions.id", name="fk_favorites_question", ondelete="RESTRICT"),
        nullable=False,
        comment="Question ID",
    )
    note = Column(String(256), nullable=True, comment="Favorite note")
    created_at = Column(DateTime, server_default=func.now(), comment="Creation time")

    def __repr__(self):
        return f"<Favorite(id={self.id}, user={self.user_id}, question={self.question_id})>"

