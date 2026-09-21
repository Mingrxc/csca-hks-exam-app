"""User API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from src.common.auth import create_token
from src.common.deps import get_current_openid
from src.common.response import ApiResponse, success
from src.config.database import SessionLocal, get_db
from src.modules.user.schemas import (
    DashboardResponse,
    UserProfileUpdate,
    UserResponse,
    WxLoginRequest,
    WxLoginResponse,
)
from src.modules.user.service import get_dashboard as get_dashboard_service
from src.modules.user.service import exchange_wx_code
from src.modules.user.service import (
    count_user_favorites,
    get_or_create_user_by_openid,
    get_target_dates,
    serialize_user,
    update_user_profile as update_user_profile_service,
)

router = APIRouter()


@router.post("/wx-login")
async def wx_login(payload: WxLoginRequest) -> ApiResponse[WxLoginResponse]:
    """Exchange a WeChat code asynchronously, then perform blocking DB work in a worker."""
    openid = await exchange_wx_code(payload.code)

    def complete_login() -> dict:
        with SessionLocal() as db:
            try:
                user = get_or_create_user_by_openid(db, openid)
                return success(
                    {
                        "token": create_token(openid),
                        "openid": openid,
                        "user": serialize_user(
                            user,
                            count_user_favorites(db, user.id),
                            get_target_dates(db, user),
                        ),
                    }
                )
            except Exception:
                db.rollback()
                raise

    return await run_in_threadpool(complete_login)


@router.get("/info")
def get_user_info(
    db: Session = Depends(get_db),
    openid: str = Depends(get_current_openid),
) -> ApiResponse[UserResponse]:
    """Return the current user profile."""
    user = get_or_create_user_by_openid(db, openid)
    return success(
        serialize_user(user, count_user_favorites(db, user.id), get_target_dates(db, user))
    )


@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    openid: str = Depends(get_current_openid),
) -> ApiResponse[DashboardResponse]:
    """Return the current learning dashboard."""
    user = get_or_create_user_by_openid(db, openid)
    return success(get_dashboard_service(db, user))


@router.put("/profile")
def update_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    openid: str = Depends(get_current_openid),
) -> ApiResponse[UserResponse]:
    """Update the current user profile."""
    return success(update_user_profile_service(db, openid, payload))
