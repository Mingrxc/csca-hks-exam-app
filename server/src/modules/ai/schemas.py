"""AI 问答模块 Pydantic 模型"""

from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ChatRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=12000)


class AIChatRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    messages: List[ChatMessage] = Field(default_factory=list, max_length=100)
    exam_type: Optional[Literal["CSCA", "HKS"]] = Field(default=None, validation_alias="examType")
    question: Optional[str] = Field(default=None, max_length=12000)
    topic: Optional[str] = Field(default=None, max_length=200)
    context: Optional[str] = Field(default=None, max_length=12000)


class AIChatResponse(BaseModel):
    reply: str
    model: str
    usage: dict[str, int] = Field(default_factory=dict)

