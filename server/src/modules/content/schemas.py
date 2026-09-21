"""首页内容模块 Pydantic 模型"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ContentCategory(str, Enum):
    CONSULTING = "consulting"
    CLUB = "club"
    AD = "ad"
    NOTICE = "notice"


class ContentItemBase(BaseModel):
    category: ContentCategory
    title: str = Field(min_length=1, max_length=128)
    summary: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1)
    cover_image: Optional[str] = None
    link_url: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True


class ContentItemCreate(ContentItemBase):
    pass


class ContentItemUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    category: Optional[ContentCategory] = None
    title: Optional[str] = Field(default=None, min_length=1, max_length=128)
    summary: Optional[str] = Field(default=None, min_length=1, max_length=255)
    body: Optional[str] = Field(default=None, min_length=1)
    cover_image: Optional[str] = None
    link_url: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class ContentItemResponse(ContentItemBase):
    id: int
    created_at: datetime
    updated_at: datetime


class ContentDeleteResponse(BaseModel):
    id: int
    deleted: bool

