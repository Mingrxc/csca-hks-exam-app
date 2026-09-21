"""AI assistant API routes."""

from fastapi import APIRouter, Depends

from src.common.deps import get_current_user_id
from src.common.response import ApiResponse, success
from src.modules.ai.schemas import AIChatRequest, AIChatResponse
from src.modules.ai.service import chat_with_qwen as chat_with_qwen_service

router = APIRouter()


@router.post("/chat")
async def chat(
    payload: AIChatRequest,
    _user_id: int = Depends(get_current_user_id),
) -> ApiResponse[AIChatResponse]:
    return success(await chat_with_qwen_service(payload))

