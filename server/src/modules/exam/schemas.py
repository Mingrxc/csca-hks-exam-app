"""考试模块 Pydantic 模型"""

from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from typing import Optional

from src.modules.question.schemas import PaperResponse


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


class KnowledgeResultResponse(BaseModel):
    total: int
    correct: int
    correct_rate: float


class WrongQuestionResponse(BaseModel):
    id: int
    stem: str
    type_label: str
    your_answer: str
    correct_answer: str


class ReviewQuestionResponse(BaseModel):
    id: int
    stem: str
    type_label: str
    options: list[dict]
    user_answer: str
    correct_answer: str
    analysis: str
    is_correct: bool


class ExamResultResponse(BaseModel):
    paper: PaperResponse
    score: float
    correct_count: int
    total_count: int
    correct_rate: float
    time_used: int
    knowledge_analysis: dict[str, KnowledgeResultResponse]
    wrong_questions: list[WrongQuestionResponse]
    review_questions: list[ReviewQuestionResponse]
