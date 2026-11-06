from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from src.modules.question.schemas import QuestionResponse


class WrongBookItem(BaseModel):
    id: int
    question_id: int
    exam_type: str
    subject: str
    stem: str
    type: str
    difficulty: str
    knowledge_point: str
    wrong_count: int
    correct_count: int
    is_mastered: bool
    first_wrong_at: datetime
    last_wrong_at: datetime
    last_review_at: Optional[datetime]


class RelatedQuestion(BaseModel):
    id: int
    exam_type: str
    subject: str
    knowledge_point: str
    difficulty: str
    question_type: str
    stem_text: str
    stem_image: Optional[str] = None
    stem_audio: Optional[str] = None
    options: list[dict]
    similarity_score: float


class WrongBookDetail(WrongBookItem):
    question: QuestionResponse
    last_user_answer: str
    wrong_options_analysis: dict[str, str]


class MasteredStatusResponse(BaseModel):
    id: int
    question_id: int
    is_mastered: bool
