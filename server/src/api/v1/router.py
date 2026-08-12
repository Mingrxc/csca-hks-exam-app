"""API v1 router aggregation."""

from fastapi import APIRouter

from src.modules.exam import router as exam_router
from src.modules.question import router as question_router
from src.modules.user import router as user_router
from src.modules.wrongbook import router as wrongbook_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(user_router, prefix="/user", tags=["用户"])
api_router.include_router(question_router, prefix="/question", tags=["题库"])
api_router.include_router(exam_router, prefix="/exam", tags=["考试"])
api_router.include_router(wrongbook_router, prefix="/wrongbook", tags=["错题本"])
