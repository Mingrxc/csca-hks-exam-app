"""用户模块 Pydantic 模型"""

from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Literal, Optional


class UserCreate(BaseModel):
    openid: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    nickname: str
    avatar_url: Optional[str]
    target_exam: Optional[str]
    target_date: Optional[date]
    target_dates: dict[Literal["CSCA", "HKS"], date] = Field(default_factory=dict)
    total_questions: int
    total_correct: int
    streak_days: int
    favorite_count: int
    created_at: datetime


class WxLoginRequest(BaseModel):
    code: str = Field(min_length=1, max_length=256)


class WxLoginResponse(BaseModel):
    token: str
    openid: str
    user: UserResponse


class UserProfileUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    target_exam: Optional[Literal["CSCA", "HKS"]] = None
    target_date: Optional[date] = None
    target_dates: Optional[dict[Literal["CSCA", "HKS"], Optional[date]]] = None
