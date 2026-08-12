"""Shared FastAPI dependencies."""

from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from src.common.auth import decode_token
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
