"""考试模块 Pydantic 模型"""

from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class SubmitAnswerRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    paper_id: int = Field(validation_alias=AliasChoices("paper_id", "paperId"))
    question_id: int = Field(validation_alias=AliasChoices("question_id", "questionId"))
    user_answer: str = Field(validation_alias=AliasChoices("user_answer", "userAnswer"))
    time_spent: int = Field(0, ge=0, validation_alias=AliasChoices("time_spent", "timeSpent"))
    wrong_reason: Optional[str] = None


class SubmitAnswerResponse(BaseModel):
    paper_id: int
    question_id: int
    is_correct: Optional[bool] = None
    correct_answer: Optional[str] = None
    user_answer: str
    recorded_new: bool
    time_spent: int


class ExamResultResponse(BaseModel):
    paper_id: int
    score: float
    correct_count: int
    total_count: int
    correct_rate: float
    time_used: int
    knowledge_analysis: dict
    created_at: datetime
