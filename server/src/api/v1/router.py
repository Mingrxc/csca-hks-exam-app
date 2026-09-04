"""API v1 router aggregation."""

from fastapi import APIRouter

from src.modules.ai.router import router as ai_router
from src.modules.content.router import router as content_router
from src.modules.favorite.router import router as favorite_router
from src.modules.exam.router import router as exam_router
from src.modules.question.router import router as question_router
from src.modules.user.router import router as user_router
from src.modules.wrongbook.router import router as wrongbook_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(user_router, prefix="/user", tags=["用户"])
api_router.include_router(question_router, prefix="/question", tags=["题库"])
api_router.include_router(exam_router, prefix="/exam", tags=["考试"])
api_router.include_router(wrongbook_router, prefix="/wrongbook", tags=["错题本"])
api_router.include_router(favorite_router, prefix="/favorite", tags=["收藏"])
api_router.include_router(content_router, prefix="/content", tags=["内容"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI问答"])
