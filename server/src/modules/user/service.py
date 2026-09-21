"""用户业务逻辑."""

from datetime import date, datetime, time, timedelta

import httpx
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.common.exceptions import AppException
from src.config.settings import settings
from src.modules.exam.models import AnswerRecord
from src.modules.question.service import list_papers
from src.modules.user.models import StreakRecord, User, UserExamTarget
from src.modules.user.schemas import UserProfileUpdate
from src.modules.wrongbook.models import WrongBook


async def exchange_wx_code(code: str, transport=None) -> str:
    """Exchange a WeChat login code for an OpenID, with an explicit local fallback."""
    if not settings.WX_APPID or not settings.WX_SECRET:
        if settings.AUTH_ALLOW_DEV_OPENID:
            return settings.DEV_OPENID
        raise AppException(50301, "微信登录尚未配置", status_code=503)

    try:
        async with httpx.AsyncClient(timeout=8, transport=transport) as client:
            response = await client.get(
                "https://api.weixin.qq.com/sns/jscode2session",
                params={
                    "appid": settings.WX_APPID,
                    "secret": settings.WX_SECRET,
                    "js_code": code,
                    "grant_type": "authorization_code",
                },
            )
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        if settings.AUTH_ALLOW_DEV_OPENID:
            return settings.DEV_OPENID
        raise AppException(50201, "微信登录服务暂时不可用", status_code=502) from exc

    if payload.get("errcode"):
        if settings.AUTH_ALLOW_DEV_OPENID:
            return settings.DEV_OPENID
        raise AppException(40101, "微信登录凭证无效或已过期", status_code=401)
    openid = payload.get("openid")
    if not openid:
        if settings.AUTH_ALLOW_DEV_OPENID:
            return settings.DEV_OPENID
        raise AppException(50202, "微信登录响应缺少用户标识", status_code=502)
    return openid


def get_or_create_user_by_openid(
    db: Session,
    openid: str,
    nickname: str = "考霸同学",
) -> User:
    user = db.query(User).filter(User.openid == openid).first()
    if user:
        return user

    user = User(openid=openid, nickname=nickname)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.query(User).filter(User.openid == openid).first()
        if existing:
            return existing
        raise
    db.refresh(user)
    return user


def get_target_dates(db: Session, user: User) -> dict[str, str]:
    rows = (
        db.query(UserExamTarget)
        .filter(UserExamTarget.user_id == user.id)
        .order_by(UserExamTarget.exam_type)
        .all()
    )
    target_dates = {
        str(row.exam_type): row.target_date.isoformat()
        for row in rows
        if row.target_date is not None
    }
    if not target_dates and user.target_exam and user.target_date:
        target_dates[str(user.target_exam)] = user.target_date.isoformat()
    return target_dates


def update_target_dates(
    db: Session,
    user_id: int,
    target_dates: dict[str, date | None],
) -> None:
    for exam_type, target_date in target_dates.items():
        if exam_type not in {"CSCA", "HKS"}:
            continue
        row = (
            db.query(UserExamTarget)
            .filter(
                UserExamTarget.user_id == user_id,
                UserExamTarget.exam_type == exam_type,
            )
            .first()
        )
        if target_date is None:
            if row:
                db.delete(row)
            continue
        if row:
            row.target_date = target_date
        else:
            db.add(
                UserExamTarget(
                    user_id=user_id,
                    exam_type=exam_type,
                    target_date=target_date,
                )
            )


def serialize_user(
    user: User,
    favorite_count: int = 0,
    target_dates: dict[str, str] | None = None,
) -> dict:
    total_questions = user.total_questions or 0
    total_correct = user.total_correct or 0
    correct_rate = round(total_correct / total_questions * 100) if total_questions else 0

    return {
        "id": user.id,
        "openid": user.openid,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "target_exam": user.target_exam,
        "target_date": user.target_date,
        "target_dates": target_dates if target_dates is not None else {},
        "total_questions": total_questions,
        "total_correct": total_correct,
        "correct_rate": correct_rate,
        "streak_days": user.streak_days or 0,
        "favorite_count": favorite_count,
        "created_at": user.created_at,
    }


def record_daily_answer(db: Session, user: User, answered_on: date | None = None) -> None:
    """Record one newly answered question without double-counting resubmissions."""
    streak_date = answered_on or date.today()
    record = (
        db.query(StreakRecord)
        .filter(
            StreakRecord.user_id == user.id,
            StreakRecord.streak_date == streak_date,
        )
        .first()
    )
    if record:
        record.question_count = (record.question_count or 0) + 1
        return

    db.add(StreakRecord(user_id=user.id, streak_date=streak_date, question_count=1))
    if user.last_streak_at == streak_date - timedelta(days=1):
        user.streak_days = (user.streak_days or 0) + 1
    elif user.last_streak_at != streak_date:
        user.streak_days = 1
    user.last_streak_at = streak_date


def get_dashboard(db: Session, user: User) -> dict:
    today = date.today()
    day_start = datetime.combine(today, time.min)
    day_end = day_start + timedelta(days=1)
    today_records = (
        db.query(AnswerRecord)
        .filter(
            AnswerRecord.user_id == user.id,
            AnswerRecord.created_at >= day_start,
            AnswerRecord.created_at < day_end,
        )
        .all()
    )
    question_count = len(today_records)
    correct_count = sum(1 for record in today_records if record.is_correct)
    wrong_count = question_count - correct_count
    pending_wrong_count = (
        db.query(WrongBook)
        .filter(WrongBook.user_id == user.id, WrongBook.is_mastered == 0)
        .count()
    )
    return {
        "user_name": user.nickname,
        "target_exam": user.target_exam,
        "target_date": user.target_date,
        "target_dates": get_target_dates(db, user),
        "today_stats": {
            "question_count": question_count,
            "correct_rate": round(correct_count / question_count * 100) if question_count else 0,
            "wrong_count": wrong_count,
        },
        "pending_wrong_count": pending_wrong_count,
        "favorite_count": count_user_favorites(db, user.id),
        "recent_papers": list_papers(db, user.id, limit=3),
    }


def count_user_favorites(db: Session, user_id: int) -> int:
    from src.modules.favorite.models import Favorite

    return db.query(Favorite).filter(Favorite.user_id == user_id).count()


def update_user_profile(
    db: Session,
    openid: str,
    payload: UserProfileUpdate,
) -> dict:
    """Update a profile and its per-exam targets in one service-owned transaction."""
    user = get_or_create_user_by_openid(db, openid)
    data = payload.model_dump(exclude_unset=True)
    target_dates = data.pop("target_dates", None)
    for key in ("nickname", "avatar_url", "target_exam", "target_date"):
        if key in data:
            setattr(user, key, data[key])
    if target_dates is not None:
        update_target_dates(db, user.id, target_dates)
        primary_exam = data.get("target_exam") or user.target_exam
        if "target_date" not in data and primary_exam in target_dates:
            user.target_date = target_dates[primary_exam]
    elif "target_date" in data and user.target_exam:
        update_target_dates(db, user.id, {user.target_exam: data["target_date"]})

    db.commit()
    db.refresh(user)
    return serialize_user(
        user,
        count_user_favorites(db, user.id),
        get_target_dates(db, user),
    )
