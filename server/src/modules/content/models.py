"""Home-content SQLAlchemy models."""

from sqlalchemy import Column, DateTime, Enum as SAEnum, Index, Integer, String, Text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.sql import func

from src.config.database import Base


class ContentItem(Base):
    __tablename__ = "content_items"
    __table_args__ = (
        Index("idx_content_category", "category"),
        Index("idx_content_sort", "sort_order"),
        Index("idx_content_active", "is_active"),
        {"comment": "Home news and promotional content"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Content ID")
    category = Column(
        SAEnum("consulting", "club", "ad", "notice"),
        nullable=False,
        comment="Content category",
    )
    title = Column(String(128), nullable=False, comment="Title")
    summary = Column(String(255), nullable=False, comment="Summary")
    body = Column(Text, nullable=False, comment="Body content")
    cover_image = Column(String(512), nullable=True, comment="Cover image URL")
    link_url = Column(String(512), nullable=True, comment="Destination URL")
    sort_order = Column(Integer, default=0, comment="Display order")
    is_active = Column(
        Integer().with_variant(TINYINT(display_width=1), "mysql"),
        default=1,
        comment="Whether the content is active",
    )
    created_at = Column(DateTime, server_default=func.now(), comment="Creation time")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="Update time")

    def __repr__(self):
        return f"<ContentItem(id={self.id}, category={self.category}, title={self.title})>"

