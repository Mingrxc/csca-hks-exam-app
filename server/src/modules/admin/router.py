from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from src.common.deps import get_admin_openid, get_owner_user
from src.common.response import ApiResponse, success
from src.config.database import get_db
from src.modules.user.models import User
from src.modules.admin import service
from src.modules.admin.schemas import AdminOverview, AdminUserItem, AdminUserPage, MemberChange, MemberCreate

router = APIRouter()


@router.get("/overview")
def overview(db: Session = Depends(get_db), _admin: str = Depends(get_admin_openid)) -> ApiResponse[AdminOverview]:
    return success(service.overview(db))


@router.get("/users")
def users(search: str = Query("", max_length=64), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
          db: Session = Depends(get_db), _admin: str = Depends(get_admin_openid)) -> ApiResponse[AdminUserPage]:
    return success(service.users(db, search=search.strip(), page=page, page_size=page_size))


@router.get("/members")
def members(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
            db: Session = Depends(get_db), _owner: User = Depends(get_owner_user)) -> ApiResponse[AdminUserPage]:
    return success(service.users(db, members_only=True, page=page, page_size=page_size))


@router.get("/members/lookup")
def lookup(user_code: str = Query(..., pattern=r"^lw[0-9]{3,}$", max_length=32),
           db: Session = Depends(get_db), _owner: User = Depends(get_owner_user)) -> ApiResponse[AdminUserItem]:
    return success(service.lookup(db, user_code))


@router.post("/members")
def grant(payload: MemberCreate, db: Session = Depends(get_db), owner: User = Depends(get_owner_user)) -> ApiResponse[MemberChange]:
    return success(service.grant(db, owner, payload.user_code))


@router.delete("/members/{user_id}")
def revoke(user_id: int = Path(..., ge=1), db: Session = Depends(get_db), owner: User = Depends(get_owner_user)) -> ApiResponse[MemberChange]:
    return success(service.revoke(db, owner, user_id))
