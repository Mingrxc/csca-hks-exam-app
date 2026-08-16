"""用户模块路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.common.auth import create_token
from src.common.deps import get_current_openid
from src.common.response import success
from src.config.database import get_db
from src.modules.user.schemas import UserProfileUpdate, WxLoginRequest
from src.modules.user.service import get_dashboard as get_dashboard_service
from src.modules.user.service import exchange_wx_code
from src.modules.user.service import get_or_create_user_by_openid, serialize_user

router = APIRouter()


@router.post("/wx-login")
async def wx_login(payload: WxLoginRequest, db: Session = Depends(get_db)):
    """微信登录"""
    openid = await exchange_wx_code(payload.code)
    user = get_or_create_user_by_openid(db, openid)
    return success({
        "token": create_token(openid),
        "openid": openid,
        "user": serialize_user(user),
    })


@router.get("/info")
async def get_user_info(
    db: Session = Depends(get_db),
    openid: str = Depends(get_current_openid),
):
    """获取用户信息"""
    user = get_or_create_user_by_openid(db, openid)
    return success(serialize_user(user))


@router.get("/dashboard")
async def get_dashboard(
    db: Session = Depends(get_db),
    openid: str = Depends(get_current_openid),
):
    """获取首页学习摘要"""
    user = get_or_create_user_by_openid(db, openid)
    return success(get_dashboard_service(db, user))


@router.put("/profile")
async def update_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    openid: str = Depends(get_current_openid),
):
    """更新用户资料"""
    user = get_or_create_user_by_openid(db, openid)
    data = payload.model_dump(exclude_unset=True)
    for key in ("nickname", "avatar_url", "target_exam", "target_date"):
        if key in data:
            setattr(user, key, data[key])
    db.commit()
    db.refresh(user)
    return success(serialize_user(user))
