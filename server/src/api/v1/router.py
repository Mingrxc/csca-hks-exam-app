from fastapi import APIRouter
from src.modules.admin.router import router as admin_router

from src.modules.feedback.router import router as feedback_router
from src.modules.content.router import router as content_router
from src.modules.favorite.router import router as favorite_router
from src.modules.exam.router import router as exam_router
from src.modules.question.router import router as question_router
from src.modules.user.router import router as user_router
from src.modules.wrongbook.router import router as wrongbook_router

# AI 模块留待接回，当前只挂载已开放的接口。
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(user_router, prefix="/user", tags=["用户"])
api_router.include_router(admin_router, prefix="/admin", tags=["管理中心"])
api_router.include_router(question_router, prefix="/question", tags=["题库"])
api_router.include_router(exam_router, prefix="/exam", tags=["考试"])
api_router.include_router(wrongbook_router, prefix="/wrongbook", tags=["错题本"])
api_router.include_router(favorite_router, prefix="/favorite", tags=["收藏"])
api_router.include_router(content_router, prefix="/content", tags=["内容"])
api_router.include_router(feedback_router, prefix="/feedback", tags=["用户反馈"])
