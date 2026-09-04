"""首页内容模块路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.common.deps import get_current_openid, get_current_user_id
from src.common.exceptions import AppException
from src.common.response import success
from src.config.database import get_db
from src.config.settings import settings
from src.modules.content.schemas import ContentItemCreate, ContentItemUpdate
from src.modules.content.service import delete_content as delete_content_service
from src.modules.content.service import get_content as get_content_service
from src.modules.content.service import list_content_admin as list_content_admin_service
from src.modules.content.service import list_home_contents as list_home_contents_service
from src.modules.content.service import save_content as save_content_service

router = APIRouter()


def require_content_admin(openid: str) -> None:
    if openid not in settings.content_admin_openids:
        raise AppException(40341, "没有内容管理权限", status_code=403)


@router.get("/home")
async def list_home_contents(db: Session = Depends(get_db)):
    return success(list_home_contents_service(db))


@router.get("/list")
async def list_content_admin(
    db: Session = Depends(get_db),
    openid: str = Depends(get_current_openid),
):
    require_content_admin(openid)
    return success(list_content_admin_service(db))


@router.get("/{content_id}")
async def get_content(content_id: int, db: Session = Depends(get_db)):
    return success(get_content_service(db, content_id))


@router.post("")
async def create_content(
    payload: ContentItemCreate,
    db: Session = Depends(get_db),
    openid: str = Depends(get_current_openid),
):
    require_content_admin(openid)
    return success(save_content_service(db, payload))


@router.put("/{content_id}")
async def update_content(
    content_id: int,
    payload: ContentItemUpdate,
    db: Session = Depends(get_db),
    openid: str = Depends(get_current_openid),
):
    require_content_admin(openid)
    return success(save_content_service(db, payload, content_id))


@router.delete("/{content_id}")
async def remove_content(
    content_id: int,
    db: Session = Depends(get_db),
    openid: str = Depends(get_current_openid),
):
    require_content_admin(openid)
    return success(delete_content_service(db, content_id))
