"""用户业务逻辑."""

from sqlalchemy.orm import Session

from src.modules.user.models import User


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
    db.commit()
    db.refresh(user)
    return user


def serialize_user(user: User) -> dict:
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
        "total_questions": total_questions,
        "total_correct": total_correct,
        "correct_rate": correct_rate,
        "streak_days": user.streak_days or 0,
        "created_at": user.created_at,
    }
