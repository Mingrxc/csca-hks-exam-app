from datetime import timedelta, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.common.exceptions import AppException
from src.common.time import study_day_utc_bounds, utc_now_naive
from src.modules.feedback.models import Feedback
from src.modules.feedback.schemas import FeedbackCreate
from src.modules.user.models import User


def serialize_feedback(item: Feedback, *, admin: bool = False) -> dict:
    result = {
        "id": item.id,
        "status": item.status,
        "created_at": item.created_at.replace(tzinfo=timezone.utc),
    }
    if admin:
        result.update(user_id=item.user_id, category=item.category, content=item.content,
                      app_version=item.app_version, updated_at=item.updated_at.replace(tzinfo=timezone.utc))
    return result


def check_replay(item: Feedback, payload: FeedbackCreate) -> dict:
    if (item.category, item.content, item.app_version) != (payload.category, payload.content, payload.app_version):
        raise AppException(40961, "这次反馈内容已变更，请重新提交", status_code=409)
    return serialize_feedback(item)


def submit_feedback(db: Session, user_id: int, payload: FeedbackCreate) -> dict:
    # Serialize submissions per user on MySQL, including the frequency checks.
    db.query(User).filter(User.id == user_id).with_for_update().one()
    existing = db.query(Feedback).filter_by(user_id=user_id, request_id=payload.request_id).first()
    if existing:
        result = check_replay(existing, payload)
        db.commit()
        return result
    now = utc_now_naive()
    recent = db.query(Feedback).filter(Feedback.user_id == user_id, Feedback.created_at > now - timedelta(seconds=30)).first()
    if recent:
        raise AppException(42961, "反馈提交较频繁，请稍后再试", status_code=429)
    start, end = study_day_utc_bounds()
    today_count = db.query(Feedback).filter(Feedback.user_id == user_id, Feedback.created_at >= start, Feedback.created_at < end).count()
    if today_count >= 20:
        raise AppException(42962, "今日反馈次数已达上限，请明天再试", status_code=429)
    item = Feedback(user_id=user_id, **payload.model_dump(), created_at=now, updated_at=now)
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.query(Feedback).filter_by(user_id=user_id, request_id=payload.request_id).first()
        if existing:
            return check_replay(existing, payload)
        raise
    db.refresh(item)
    return serialize_feedback(item)


def list_feedback(db: Session, *, status: str | None, page: int, page_size: int) -> dict:
    query = db.query(Feedback)
    if status:
        query = query.filter(Feedback.status == status)
    total = query.count()
    items = query.order_by(Feedback.created_at.desc(), Feedback.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [serialize_feedback(item, admin=True) for item in items], "total": total,
            "page": page, "page_size": page_size}


def update_feedback_status(db: Session, feedback_id: int, status: str) -> dict:
    item = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not item:
        raise AppException(40461, "反馈不存在", status_code=404)
    item.status = status
    item.updated_at = utc_now_naive()
    db.commit()
    db.refresh(item)
    return serialize_feedback(item, admin=True)
