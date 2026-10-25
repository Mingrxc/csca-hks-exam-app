"""Feedback is private to the operator, separate from learning records."""

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint

from src.common.time import utc_now_naive
from src.config.database import Base


class Feedback(Base):
    __tablename__ = "feedback"
    __table_args__ = (
        UniqueConstraint("user_id", "request_id", name="uk_feedback_user_request"),
        Index("idx_feedback_user_created", "user_id", "created_at"),
        Index("idx_feedback_status_created", "status", "created_at"),
        {"comment": "Private user feedback for the operator"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", name="fk_feedback_user", ondelete="CASCADE"), nullable=False)
    request_id = Column(String(64), nullable=False, comment="Per-user idempotency key")
    category = Column(String(24), nullable=False)
    content = Column(Text, nullable=False)
    app_version = Column(String(24), nullable=False)
    status = Column(String(16), nullable=False, default="unread", server_default="unread")
    created_at = Column(DateTime, nullable=False, default=utc_now_naive)
    updated_at = Column(DateTime, nullable=False, default=utc_now_naive, onupdate=utc_now_naive)
