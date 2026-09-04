"""收藏模块 Pydantic 模型"""

from datetime import datetime
from typing import Optional

from pydantic import AliasChoices, BaseModel, Field

from src.modules.question.schemas import QuestionResponse


class FavoriteToggleRequest(BaseModel):
    question_id: int = Field(
        validation_alias=AliasChoices("question_id", "questionId"),
        ge=1,
    )


class FavoriteQuestionResponse(BaseModel):
    id: int
    question_id: int
    question: QuestionResponse
    note: Optional[str] = None
    created_at: datetime


class FavoriteStatusResponse(BaseModel):
    question_id: int
    is_favorite: bool
    favorite_count: int
