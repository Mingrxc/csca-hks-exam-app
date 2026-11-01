"""用户业务逻辑."""

from datetime import date, datetime, time, timedelta

import httpx
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.common.exceptions import AppException
from src.common.time import study_today, study_day_utc_bounds
from src.config.settings import settings
from src.modules.exam.models import AnswerRecord
from src.modules.question.service import list_papers
from src.modules.user.models import StreakRecord, User, UserExamTarget
from src.modules.user.schemas import UserProfileUpdate
from src.modules.wrongbook.models import WrongBook


async def exchange_wx_code(code: str, transport=None) -> str:
    """Exchange a WeChat login code for an OpenID, with an explicit local fallback."""
    if not settings.WX_APPID or not settings.WX_SECRET:
        if settings.AUTH_ALLOW_DEV_OPENID and not settings.is_production:
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
        if settings.AUTH_ALLOW_DEV_OPENID and not settings.is_production:
            return settings.DEV_OPENID
        raise AppException(50201, "微信登录服务暂时不可用", status_code=502) from exc

    if payload.get("errcode"):
        if settings.AUTH_ALLOW_DEV_OPENID and not settings.is_production:
            return settings.DEV_OPENID
        raise AppException(40101, "微信登录凭证无效或已过期", status_code=401)
    openid = payload.get("openid")
    if not openid:
        if settings.AUTH_ALLOW_DEV_OPENID and not settings.is_production:
            return settings.DEV_OPENID
        raise AppException(50202, "微信登录响应缺少用户标识", status_code=502)
    return openid


def get_or_create_user_by_openid(
    db: Session,
    openid: str,
    nickname: str = "留学同学",
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


def get_user_by_openid(db: Session, openid: str) -> User:
    user = db.query(User).filter(User.openid == openid).first()
    if user is None:
        raise AppException(40102, "登录状态已失效，请重新登录", status_code=401)
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
    from sqlalchemy.orm import object_session
    from src.modules.admin.service import role_for
    session = object_session(user)
    total_questions = user.total_questions or 0
    total_correct = user.total_correct or 0
    objective_count = user.total_objective or (total_questions if total_correct else 0)
    correct_rate = round(total_correct / objective_count * 100) if objective_count else 0

    return {
        "id": user.id,
        "user_code": user.user_code,
        "admin_role": role_for(session, user.id) if session else "user",
        "openid": user.openid,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "target_exam": user.target_exam,
        "target_date": user.target_date,
        "target_dates": target_dates if target_dates is not None else {},
        "total_questions": total_questions,
        "total_correct": total_correct,
        "total_objective": objective_count,
        "correct_rate": correct_rate,
        "streak_days": current_streak_days(user),
        "favorite_count": favorite_count,
        "created_at": user.created_at,
    }


def current_streak_days(user: User, today: date | None = None) -> int:
    today = today or study_today()
    if user.last_streak_at in {today, today - timedelta(days=1)}:
        return user.streak_days or 0
    return 0


def record_daily_activity(db: Session, user: User, activity_on: date | None = None,
                          *, answered: bool = False) -> None:
    """Share a daily record between manual check-in and answering; caller commits."""
    # Both writers lock the same user, then read the daily row with a current read
    # so MySQL REPEATABLE READ cannot duplicate a concurrent first check-in. Leave
    # pending answer writes for the caller's commit/conflict-retry transaction.
    with db.no_autoflush:
        streak_days, last_streak_at = (
            db.query(User.streak_days, User.last_streak_at)
            .filter(User.id == user.id).with_for_update().one()
        )
    streak_date = activity_on or study_today()
    with db.no_autoflush:
        record = (
            db.query(StreakRecord)
            .filter(
                StreakRecord.user_id == user.id,
                StreakRecord.streak_date == streak_date,
            )
            .with_for_update().first()
        )
    if record:
        if answered:
            record.question_count = (record.question_count or 0) + 1
    else:
        db.add(StreakRecord(user_id=user.id, streak_date=streak_date,
                            question_count=1 if answered else 0))
        if last_streak_at == streak_date - timedelta(days=1):
            streak_days = (streak_days or 0) + 1
        elif last_streak_at != streak_date:
            streak_days = 1
        last_streak_at = streak_date
    user.streak_days = streak_days
    user.last_streak_at = last_streak_at


def record_daily_answer(db: Session, user: User, answered_on: date | None = None) -> None:
    """Record one newly answered question without double-counting resubmissions."""
    record_daily_activity(db, user, answered_on, answered=True)


def get_check_in(db: Session, user: User, today: date | None = None) -> dict:
    today = today or study_today()
    monday = today - timedelta(days=today.weekday())
    checked_dates = {
        row.streak_date for row in db.query(StreakRecord).filter(
            StreakRecord.user_id == user.id,
            StreakRecord.streak_date >= monday,
            StreakRecord.streak_date <= today,
        ).all()
    }
    return {
        "today": today,
        "checked_in": today in checked_dates,
        "streak_days": current_streak_days(user, today),
        "week": [
            {"date": monday + timedelta(days=offset),
             "checked": monday + timedelta(days=offset) in checked_dates}
            for offset in range(7)
        ],
    }


def check_in(db: Session, openid: str) -> dict:
    user = get_user_by_openid(db, openid)
    record_daily_activity(db, user)
    # Keep the same Beijing date even if a request happens to cross midnight.
    checked_on = user.last_streak_at
    db.commit()
    return get_check_in(db, user, checked_on)


def get_dashboard(db: Session, user: User) -> dict:
    today = study_today()
    day_start, day_end = study_day_utc_bounds(today)
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
    objective_count = sum(record.is_correct is not None for record in today_records)
    wrong_count = sum(record.is_correct == 0 for record in today_records)
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
            "objective_count": objective_count,
            "question_count": question_count,
            "correct_rate": round(correct_count / objective_count * 100) if objective_count else 0,
            "wrong_count": wrong_count,
        },
        "pending_wrong_count": pending_wrong_count,
        "favorite_count": count_user_favorites(db, user.id),
        "recent_papers": list_papers(db, user.id, limit=3),
        "check_in": get_check_in(db, user, today),
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
    user = get_user_by_openid(db, openid)
    data = payload.model_dump(exclude_unset=True)
    if "nickname" in data and data["nickname"] is None:
        raise AppException(42201, "昵称不能为空", status_code=422)
    if "avatar_url" in data and data["avatar_url"] != user.avatar_url:
        raise AppException(42202, "请通过头像上传功能更新头像", status_code=422)
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
