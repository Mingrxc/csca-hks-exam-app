"""AI 问答模块路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.common.deps import get_current_user_id
from src.common.response import success
from src.config.database import get_db
from src.modules.ai.schemas import AIChatRequest
from src.modules.ai.service import chat_with_qwen as chat_with_qwen_service

router = APIRouter()


@router.post("/chat")
async def chat(
    payload: AIChatRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return success(await chat_with_qwen_service(db, payload))

