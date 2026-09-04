"""收藏模块路由"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.common.deps import get_current_user_id
from src.common.response import success
from src.config.database import get_db
from src.modules.favorite.schemas import FavoriteToggleRequest
from src.modules.favorite.service import count_favorites as count_favorites_service
from src.modules.favorite.service import get_favorite_status as get_favorite_status_service
from src.modules.favorite.service import list_favorites as list_favorites_service
from src.modules.favorite.service import toggle_favorite as toggle_favorite_service

router = APIRouter()


@router.get("/list")
async def list_favorites(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return success(list_favorites_service(db, user_id, limit))


@router.get("/status/{question_id}")
async def get_favorite_status(
    question_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return success(get_favorite_status_service(db, user_id, question_id))


@router.post("/toggle")
async def toggle_favorite(
    payload: FavoriteToggleRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return success(toggle_favorite_service(db, user_id, payload.question_id))


@router.get("/count")
async def count_favorites(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return success({"favorite_count": count_favorites_service(db, user_id)})

