"""AI 问答模块 Pydantic 模型"""

from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ChatRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class AIChatRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    messages: List[ChatMessage] = Field(default_factory=list)
    exam_type: Optional[Literal["CSCA", "HKS"]] = Field(default=None, validation_alias="examType")
    question: Optional[str] = None
    topic: Optional[str] = None
    context: Optional[str] = None


class AIChatResponse(BaseModel):
    reply: str
    model: str
    usage: dict[str, int] = Field(default_factory=dict)

