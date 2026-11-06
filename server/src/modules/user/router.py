from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from src.common.auth import create_token
from src.common.deps import get_current_openid, get_current_user_id
from src.common.response import ApiResponse, success
from src.config.database import SessionLocal, get_db
from src.modules.user.schemas import (
    CheckInResponse,
    DashboardResponse,
    UserProfileUpdate,
    UserResponse,
    WxLoginRequest,
    WxLoginResponse,
)
from src.modules.user.service import get_dashboard as get_dashboard_service
from src.modules.user.service import exchange_wx_code
from src.modules.user.service import (
    check_in as check_in_service,
    count_user_favorites,
    get_or_create_user_by_openid,
    get_user_by_openid,
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
                if payload.nickname:
                    user.nickname = payload.nickname
                    db.commit()
                    db.refresh(user)
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
    user = get_user_by_openid(db, openid)
    return success(
        serialize_user(user, count_user_favorites(db, user.id), get_target_dates(db, user))
    )


@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    openid: str = Depends(get_current_openid),
) -> ApiResponse[DashboardResponse]:
    """Return the current learning dashboard."""
    user = get_user_by_openid(db, openid)
    return success(get_dashboard_service(db, user))


@router.post("/check-in")
def check_in(
    db: Session = Depends(get_db),
    openid: str = Depends(get_current_openid),
) -> ApiResponse[CheckInResponse]:
    """Check in the authenticated account once per Beijing day."""
    return success(check_in_service(db, openid))


@router.put("/profile")
def update_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    openid: str = Depends(get_current_openid),
) -> ApiResponse[UserResponse]:
    """Update the current user profile."""
    return success(update_user_profile_service(db, openid, payload))


@router.post("/avatar")
def upload_avatar(file: UploadFile = File(...), db: Session = Depends(get_db),
                  user_id: int = Depends(get_current_user_id)) -> ApiResponse[UserResponse]:
    from src.modules.user.avatars import MAX_AVATAR_BYTES, save_avatar
    try:
        return success(save_avatar(db, user_id, file.file.read(MAX_AVATAR_BYTES + 1)))
    finally:
        file.file.close()


@router.get("/avatar/{filename}")
def get_avatar(filename: str):
    from src.modules.user.avatars import avatar_file
    return FileResponse(avatar_file(filename), media_type="image/jpeg",
                        headers={"X-Content-Type-Options": "nosniff", "Cache-Control": "public, max-age=86400"})
