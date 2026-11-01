from datetime import timezone
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from src.common.exceptions import AppException
from src.common.time import study_day_utc_bounds, utc_now_naive
from src.modules.admin.models import AdminAudit, AdminMember, AdminOwner
from src.modules.exam.models import AnswerRecord
from src.modules.feedback.models import Feedback
from src.modules.question.models import Paper
from src.modules.user.models import User


def role_for(db, user_id: int) -> str:
    if db.query(AdminOwner).filter(AdminOwner.id == 1, AdminOwner.user_id == user_id).first():
        return "owner"
    return "viewer" if db.get(AdminMember, user_id) else "user"


def audit(db, actor: User, action: str, *, target_id=None, resource_id=None, details=None):
    db.add(AdminAudit(actor_user_id=actor.id, actor_code=actor.user_code, action=action,
                      target_user_id=target_id, resource_id=resource_id, details=details, created_at=utc_now_naive()))


def utc(value):
    return value.replace(tzinfo=timezone.utc) if value else None


def user_item(user, role="user", last_study_at=None):
    objective = user.total_objective or (user.total_questions if user.total_correct else 0) or 0
    return {"id": user.id, "user_code": user.user_code, "nickname": user.nickname,
            "avatar_url": user.avatar_url, "role": role, "created_at": utc(user.created_at),
            "total_questions": user.total_questions or 0, "total_objective": objective,
            "correct_rate": round((user.total_correct or 0) / objective * 100) if objective else 0,
            "streak_days": user.streak_days or 0, "last_study_at": utc(last_study_at)}


def overview(db):
    start, end = study_day_utc_bounds()
    return {"total_users": db.query(User).count(),
            "new_users_today": db.query(User).filter(User.created_at >= start, User.created_at < end).count(),
            "answering_users_today": db.query(func.count(func.distinct(AnswerRecord.user_id))).filter(
                AnswerRecord.created_at >= start, AnswerRecord.created_at < end).scalar(),
            "total_answers": db.query(AnswerRecord).count(), "total_papers": db.query(Paper).count(),
            "total_feedback": db.query(Feedback).count(),
            "unread_feedback": db.query(Feedback).filter(Feedback.status == "unread").count(),
            "study_timezone": "Asia/Shanghai"}


def users(db, *, search="", page=1, page_size=20, members_only=False):
    owner = db.get(AdminOwner, 1)
    owner_id = owner.user_id if owner else None
    members = db.query(AdminMember.user_id).scalar_subquery()
    query = db.query(User)
    if members_only:
        query = query.filter(or_(User.id == owner_id, User.id.in_(members)))
    if search:
        query = query.filter(or_(User.user_code == search, User.nickname.contains(search, autoescape=True)))
    total = query.count()
    recent = db.query(AnswerRecord.user_id.label("uid"), func.max(AnswerRecord.created_at).label("last_study")).group_by(AnswerRecord.user_id).subquery()
    rows = query.outerjoin(recent, User.id == recent.c.uid).add_columns(recent.c.last_study).order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    ids = [user.id for user, _ in rows]
    member_ids = {row.user_id for row in db.query(AdminMember).filter(AdminMember.user_id.in_(ids)).all()} if ids else set()
    return {"items": [user_item(user, "owner" if user.id == owner_id else "viewer" if user.id in member_ids else "user", last)
                      for user, last in rows], "total": total, "page": page, "page_size": page_size}


def lookup(db, user_code):
    user = db.query(User).filter(User.user_code == user_code).first()
    if not user:
        raise AppException(40471, "未找到该用户，请确认对方已登录并核对编号", status_code=404)
    return user_item(user, role_for(db, user.id))


def grant(db, actor, user_code):
    user = db.query(User).filter(User.user_code == user_code).with_for_update().first()
    if not user:
        raise AppException(40471, "未找到该用户，请确认对方已登录并核对编号", status_code=404)
    if user.id == actor.id:
        raise AppException(40971, "主管理员无需重复授权", status_code=409)
    if db.query(AdminMember).filter(AdminMember.user_id == user.id).with_for_update().first():
        return {"user_id": user.id, "changed": False}
    db.add(AdminMember(user_id=user.id, granted_by=actor.id, created_at=utc_now_naive()))
    audit(db, actor, "admin.grant", target_id=user.id, details={"user_code": user.user_code})
    db.commit()
    return {"user_id": user.id, "changed": True}


def revoke(db, actor, user_id):
    if user_id == actor.id:
        raise AppException(40972, "不能从界面撤销主管理员", status_code=409)
    member = db.query(AdminMember).filter(AdminMember.user_id == user_id).with_for_update().first()
    if not member:
        return {"user_id": user_id, "changed": False}
    db.delete(member)
    audit(db, actor, "admin.revoke", target_id=user_id)
    db.commit()
    return {"user_id": user_id, "changed": True}


def bootstrap_owner(db, user_code, *, apply=False, expected_user_id=None, temporary=False):
    """Operator-only bootstrap, never exposed by HTTP; preview without writes."""
    user = db.query(User).filter(User.user_code == user_code).with_for_update().first()
    if not user:
        raise ValueError("User does not exist")
    owner = db.query(AdminOwner).filter(AdminOwner.id == 1).with_for_update().first()
    reserved = db.query(User).filter(User.user_code == "lw000").first()
    if owner and owner.user_id != user.id:
        raise ValueError("Owner already belongs to another account")
    if not temporary and reserved and reserved.id != user.id:
        raise ValueError("Owner or lw000 already belongs to another account")
    if temporary and user.user_code == "lw000":
        raise ValueError("Temporary owner must keep a regular code; lw000 is reserved")
    if owner and bool(owner.is_temporary) != temporary:
        raise ValueError("Existing owner binding mode differs; no implicit conversion allowed")
    result = {"id": user.id, "nickname": user.nickname, "previous_code": user.user_code,
              "new_code": user.user_code if temporary else "lw000", "role": "owner", "temporary": temporary, "applied": apply}
    if not apply:
        return result
    if expected_user_id != user.id:
        raise ValueError("Verify the preview and pass --expected-user-id before applying")
    if owner:
        return result
    old_code = user.user_code
    if not temporary:
        user.user_code = "lw000"
    db.add(AdminOwner(id=1, user_id=user.id, is_temporary=temporary, created_at=utc_now_naive()))
    existing_member = db.get(AdminMember, user.id)
    if existing_member:
        db.delete(existing_member)
    audit(db, user, "owner.bootstrap_trial" if temporary else "owner.bootstrap", target_id=user.id,
          details={"previous_code": old_code, "temporary": temporary})
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Owner binding changed concurrently; inspect again") from exc
    return result
