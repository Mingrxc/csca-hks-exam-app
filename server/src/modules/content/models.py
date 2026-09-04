"""首页内容模块 SQLAlchemy 模型"""

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
        {"comment": "首页资讯和广告内容表"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="内容 ID")
    category = Column(
        SAEnum("consulting", "club", "ad", "notice"),
        nullable=False,
        comment="内容分类",
    )
    title = Column(String(128), nullable=False, comment="标题")
    summary = Column(String(255), nullable=False, comment="摘要")
    body = Column(Text, nullable=False, comment="正文")
    cover_image = Column(String(512), nullable=True, comment="封面图")
    link_url = Column(String(512), nullable=True, comment="跳转链接")
    sort_order = Column(Integer, default=0, comment="排序")
    is_active = Column(
        Integer().with_variant(TINYINT(display_width=1), "mysql"),
        default=1,
        comment="是否启用",
    )
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<ContentItem(id={self.id}, category={self.category}, title={self.title})>"

