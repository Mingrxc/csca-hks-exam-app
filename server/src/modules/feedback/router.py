from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.common.deps import get_admin_openid, get_authenticated_user_id
from src.common.response import ApiResponse, success
from src.config.database import get_db
from src.modules.feedback import service
from src.modules.feedback.schemas import FeedbackAdminItem, FeedbackCreate, FeedbackPage, FeedbackReceipt, FeedbackStatus, FeedbackStatusUpdate

router = APIRouter()


@router.post("")
def submit_feedback(payload: FeedbackCreate, db: Session = Depends(get_db),
                    user_id: int = Depends(get_authenticated_user_id)) -> ApiResponse[FeedbackReceipt]:
    return success(service.submit_feedback(db, user_id, payload))


@router.get("/admin")
def list_feedback(status: FeedbackStatus | None = None, page: int = Query(1, ge=1),
                  page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db),
                  _admin: str = Depends(get_admin_openid)) -> ApiResponse[FeedbackPage]:
    return success(service.list_feedback(db, status=status, page=page, page_size=page_size))


@router.put("/admin/{feedback_id}/status")
def update_status(feedback_id: int, payload: FeedbackStatusUpdate, db: Session = Depends(get_db),
                  _admin: str = Depends(get_admin_openid)) -> ApiResponse[FeedbackAdminItem]:
    return success(service.update_feedback_status(db, feedback_id, payload.status))
