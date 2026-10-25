"""Shared FastAPI dependencies."""

from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from src.common.auth import decode_token
from src.common.exceptions import AppException
from src.config.database import get_db
from src.config.settings import settings


def get_current_openid(authorization: Optional[str] = Header(default=None)) -> str:
    if authorization and authorization.startswith("Bearer "):
        return decode_token(authorization[7:])
    if settings.AUTH_ALLOW_DEV_OPENID:
        return settings.DEV_OPENID
    raise HTTPException(status_code=401, detail="Missing bearer token")


def get_current_user_id(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
) -> int:
    from src.modules.user.service import get_or_create_user_by_openid

    openid = get_current_openid(authorization)
    user = get_or_create_user_by_openid(db, openid)
    return user.id


def get_authenticated_openid(authorization: Optional[str] = Header(default=None)) -> str:
    """Private feedback and administration never use the anonymous dev fallback."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="请先登录")
    return decode_token(authorization[7:])


def get_authenticated_user_id(
    db: Session = Depends(get_db),
    openid: str = Depends(get_authenticated_openid),
) -> int:
    from src.modules.user.models import User

    # A locking first read also keeps feedback quota checks current on MySQL's
    # REPEATABLE READ isolation level after waiting for another submission.
    user = db.query(User).filter(User.openid == openid).with_for_update().first()
    if not user:
        raise HTTPException(status_code=401, detail="登录状态已失效，请重新登录")
    return user.id


def get_admin_openid(openid: str = Depends(get_authenticated_openid)) -> str:
    if openid not in settings.content_admin_openids:
        raise AppException(40341, "没有管理权限", status_code=403)
    return openid
