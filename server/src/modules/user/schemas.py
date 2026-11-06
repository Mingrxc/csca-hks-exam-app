from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import Literal, Optional


class UserResponse(BaseModel):
    admin_role: Literal["user", "viewer", "owner"] = "user"
    id: int
    user_code: str
    nickname: str
    avatar_url: Optional[str]
    target_exam: Optional[str]
    target_date: Optional[date]
    target_dates: dict[Literal["CSCA", "HKS"], date] = Field(default_factory=dict)
    total_questions: int
    total_correct: int
    total_objective: int = 0
    correct_rate: int
    streak_days: int
    favorite_count: int
    created_at: datetime


class WxLoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    code: str = Field(min_length=1, max_length=256)
    nickname: Optional[str] = Field(default=None, min_length=1, max_length=64)


class WxLoginResponse(BaseModel):
    token: str
    openid: str
    user: UserResponse


class UserProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    nickname: Optional[str] = Field(default=None, min_length=1, max_length=64)
    avatar_url: Optional[str] = None
    target_exam: Optional[Literal["CSCA", "HKS"]] = None
    target_date: Optional[date] = None
    target_dates: Optional[dict[Literal["CSCA", "HKS"], Optional[date]]] = None


class TodayStatsResponse(BaseModel):
    question_count: int
    correct_rate: int
    wrong_count: int
    objective_count: int = 0


class DashboardPaperResponse(BaseModel):
    id: int
    title: str
    exam_type: str
    question_count: int
    objective_count: int = 0
    score: float
    correct_rate: float
    time_used: int
    passed: bool
    finished_at: datetime


class CheckInDayResponse(BaseModel):
    date: date
    checked: bool


class CheckInResponse(BaseModel):
    today: date
    checked_in: bool
    streak_days: int
    week: list[CheckInDayResponse]


class DashboardResponse(BaseModel):
    user_name: str
    target_exam: str
    target_date: Optional[date]
    target_dates: dict[Literal["CSCA", "HKS"], date] = Field(default_factory=dict)
    today_stats: TodayStatsResponse
    pending_wrong_count: int
    favorite_count: int
    recent_papers: list[DashboardPaperResponse] = Field(default_factory=list)
    check_in: CheckInResponse
