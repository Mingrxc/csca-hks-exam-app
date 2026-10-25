"""Home-content API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.common.deps import get_admin_openid
from src.common.response import ApiResponse, success
from src.config.database import get_db
from src.modules.content.schemas import (
    ContentDeleteResponse,
    AnnouncementPage,
    ContentItemCreate,
    ContentItemResponse,
    ContentItemUpdate,
)
from src.modules.content.service import delete_content as delete_content_service
from src.modules.content.service import get_content as get_content_service
from src.modules.content.service import list_content_admin as list_content_admin_service
from src.modules.content.service import list_home_contents as list_home_contents_service
from src.modules.content.service import save_content as save_content_service
from src.modules.content.service import list_announcements as list_announcements_service
from src.modules.content.service import get_announcement as get_announcement_service

router = APIRouter()


@router.get("/announcements")
def list_announcements(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                       db: Session = Depends(get_db)) -> ApiResponse[AnnouncementPage]:
    return success(list_announcements_service(db, page=page, page_size=page_size))


@router.get("/announcements/{content_id}")
def get_announcement(content_id: int, db: Session = Depends(get_db)) -> ApiResponse[ContentItemResponse]:
    return success(get_announcement_service(db, content_id))


@router.get("/home")
def list_home_contents(
    db: Session = Depends(get_db),
) -> ApiResponse[list[ContentItemResponse]]:
    return success(list_home_contents_service(db))


@router.get("/list")
def list_content_admin(
    db: Session = Depends(get_db),
    _admin: str = Depends(get_admin_openid),
) -> ApiResponse[list[ContentItemResponse]]:
    return success(list_content_admin_service(db))


@router.get("/{content_id}")
def get_content(
    content_id: int,
    db: Session = Depends(get_db),
) -> ApiResponse[ContentItemResponse]:
    return success(get_content_service(db, content_id))


@router.post("")
def create_content(
    payload: ContentItemCreate,
    db: Session = Depends(get_db),
    _admin: str = Depends(get_admin_openid),
) -> ApiResponse[ContentItemResponse]:
    return success(save_content_service(db, payload))


@router.put("/{content_id}")
def update_content(
    content_id: int,
    payload: ContentItemUpdate,
    db: Session = Depends(get_db),
    _admin: str = Depends(get_admin_openid),
) -> ApiResponse[ContentItemResponse]:
    return success(save_content_service(db, payload, content_id))


@router.delete("/{content_id}")
def remove_content(
    content_id: int,
    db: Session = Depends(get_db),
    _admin: str = Depends(get_admin_openid),
) -> ApiResponse[ContentDeleteResponse]:
    return success(delete_content_service(db, content_id))
