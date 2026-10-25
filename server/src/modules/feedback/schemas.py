from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

FeedbackCategory = Literal["question", "bug", "suggestion", "other"]
FeedbackStatus = Literal["unread", "read", "resolved"]


class FeedbackCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    request_id: str = Field(min_length=8, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    category: FeedbackCategory = "suggestion"
    content: str = Field(min_length=1, max_length=1000)
    app_version: str = Field(min_length=1, max_length=24, pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")


class FeedbackReceipt(BaseModel):
    id: int
    status: FeedbackStatus
    created_at: datetime


class FeedbackAdminItem(FeedbackReceipt):
    user_id: int
    category: FeedbackCategory
    content: str
    app_version: str
    updated_at: datetime


class FeedbackPage(BaseModel):
    items: list[FeedbackAdminItem]
    total: int
    page: int
    page_size: int


class FeedbackStatusUpdate(BaseModel):
    status: FeedbackStatus
