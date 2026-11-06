from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from src.common.auth import decode_token
from src.common.exceptions import AppException
from src.config.database import get_db
from src.config.settings import settings


def get_current_openid(authorization: Optional[str] = Header(default=None)) -> str:
    return get_authenticated_openid(authorization)


def get_current_user_id(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
) -> int:
    from src.modules.user.service import get_user_by_openid

    openid = get_current_openid(authorization)
    user = get_user_by_openid(db, openid)
    return user.id


def get_authenticated_openid(authorization: Optional[str] = Header(default=None)) -> str:
    """Protected routes require an explicit login token, including in development."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="请先登录")
    return decode_token(authorization[7:])


def get_authenticated_user_id(
    db: Session = Depends(get_db),
    openid: str = Depends(get_authenticated_openid),
) -> int:
    from src.modules.user.models import User

    # 先加用户锁，反馈限额检查才能读取上一笔提交后的数据。
    user = db.query(User).filter(User.openid == openid).with_for_update().first()
    if not user:
        raise HTTPException(status_code=401, detail="登录状态已失效，请重新登录")
    return user.id


def get_admin_openid(db: Session = Depends(get_db), openid: str = Depends(get_authenticated_openid)) -> str:
    from src.modules.admin.service import role_for
    from src.modules.user.service import get_user_by_openid
    user = get_user_by_openid(db, openid)
    if role_for(db, user.id) not in {"viewer", "owner"}:
        raise AppException(40341, "没有管理权限", status_code=403)
    return openid


def get_owner_user(db: Session = Depends(get_db), openid: str = Depends(get_authenticated_openid)):
    from src.modules.admin.models import AdminOwner
    from src.modules.user.service import get_user_by_openid
    user = get_user_by_openid(db, openid)
    # 锁住主管理员记录，让写入和权限变更按顺序执行。
    owner = db.query(AdminOwner).filter(AdminOwner.id == 1).with_for_update().first()
    if not owner or owner.user_id != user.id:
        raise AppException(40342, "仅主管理员可以执行此操作", status_code=403)
    return user
