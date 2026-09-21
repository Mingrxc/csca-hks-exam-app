"""题库模块 Pydantic 模型"""

from datetime import datetime
from typing import List, Literal, Optional
from enum import Enum

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class ExamType(str, Enum):
    CSCA = "CSCA"
    HKS = "HKS"


class QuestionType(str, Enum):
    SINGLE = "single"
    MULTI = "multi"
    JUDGE = "judge"
    FILL = "fill"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class DifficultyFilter(str, Enum):
    ALL = "all"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class PaperStrategy(str, Enum):
    RANDOM = "random"
    KNOWLEDGE = "knowledge"
    PROGRESSIVE = "progressive"
    REAL = "real"


class GeneratePaperRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    exam_type: ExamType = Field(validation_alias=AliasChoices("exam_type", "examType"))
    question_count: int = Field(20, ge=1, le=100, validation_alias=AliasChoices("question_count", "questionCount"))
    difficulty: DifficultyFilter = DifficultyFilter.ALL
    strategy: PaperStrategy = PaperStrategy.RANDOM
    knowledge_points: Optional[List[str]] = Field(
        None,
        validation_alias=AliasChoices("knowledge_points", "knowledgePoints"),
    )
    mode: Literal["exam", "practice"] = "practice"
    time_limit: int = Field(0, ge=0, validation_alias=AliasChoices("time_limit", "timeLimit"))


class QuestionOption(BaseModel):
    key: str
    text: str


class QuestionResponse(BaseModel):
    id: int
    exam_type: str
    subject: str
    knowledge_point: str
    difficulty: str
    question_type: str
    stem_text: str
    stem_image: Optional[str] = None
    stem_audio: Optional[str] = None
    options: List[QuestionOption]
    answer: Optional[str] = None
    analysis: Optional[str] = None


class PaperResponse(BaseModel):
    id: int
    title: str
    exam_type: str
    strategy: str
    question_ids: List[int]
    total_score: int
    time_limit: int
    mode: str
    difficulty: str
    questions: List[QuestionResponse] = Field(default_factory=list)


class HistoryPaperResponse(BaseModel):
    id: int
    title: str
    exam_type: str
    question_count: int
    score: float
    correct_rate: float
    time_used: int
    passed: bool
    finished_at: datetime


class SpecialOptionResponse(BaseModel):
    value: str
    label: str
    count: int
