"""错题本模块 Pydantic 模型"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class WrongReason(str, Enum):
    KNOWLEDGE = "知识点不会"
    CARELESS = "粗心大意"
    MISREAD = "审题错误"
    TIMEOUT = "时间不够"
    CONFUSION = "选项混淆"
    OTHER = "其他"


class WrongBookItem(BaseModel):
    id: int
    question_id: int
    stem: str
    type: str
    difficulty: str
    knowledge_point: str
    wrong_count: int
    is_mastered: bool
    last_wrong_at: datetime


class RelatedQuestion(BaseModel):
    id: int
    stem: str
    type: str
    difficulty: str
    knowledge_point: str
    similarity_score: float
