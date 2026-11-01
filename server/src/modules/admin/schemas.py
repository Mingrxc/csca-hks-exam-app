from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

AdminRole = Literal["user", "viewer", "owner"]


class AdminUserItem(BaseModel):
    id: int
    user_code: str
    nickname: str
    avatar_url: str | None
    role: AdminRole
    created_at: datetime
    total_questions: int
    total_objective: int
    correct_rate: int
    streak_days: int
    last_study_at: datetime | None


class AdminUserPage(BaseModel):
    items: list[AdminUserItem]
    total: int
    page: int
    page_size: int


class AdminOverview(BaseModel):
    total_users: int
    new_users_today: int
    answering_users_today: int
    total_answers: int
    total_papers: int
    total_feedback: int
    unread_feedback: int
    study_timezone: str


class MemberCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    user_code: str = Field(pattern=r"^lw[0-9]{3,}$", max_length=32)


class MemberChange(BaseModel):
    user_id: int
    changed: bool
