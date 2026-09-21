"""收藏业务逻辑."""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.common.exceptions import AppException
from src.modules.favorite.models import Favorite
from src.modules.question.models import Question
from src.modules.question.service import serialize_question


def list_favorites(db: Session, user_id: int, limit: int = 50) -> list[dict]:
    rows = (
        db.query(Favorite, Question)
        .join(Question, Question.id == Favorite.question_id)
        .filter(Favorite.user_id == user_id, Question.is_active == 1)
        .order_by(Favorite.created_at.desc(), Favorite.id.desc())
        .limit(limit)
        .all()
    )
    return [serialize_favorite_item(item, question) for item, question in rows]


def get_favorite_status(db: Session, user_id: int, question_id: int) -> dict:
    item = (
        db.query(Favorite)
        .filter(Favorite.user_id == user_id, Favorite.question_id == question_id)
        .first()
    )
    return {
        "question_id": question_id,
        "is_favorite": bool(item),
        "favorite_count": count_favorites(db, user_id),
    }


def toggle_favorite(
    db: Session,
    user_id: int,
    question_id: int,
    *,
    retry_on_conflict: bool = True,
) -> dict:
    question = db.query(Question).filter(Question.id == question_id, Question.is_active == 1).first()
    if not question:
        raise AppException(40431, "题目不存在", status_code=404)

    item = (
        db.query(Favorite)
        .filter(Favorite.user_id == user_id, Favorite.question_id == question_id)
        .first()
    )
    if item:
        db.delete(item)
        db.commit()
        return {
            "question_id": question_id,
            "is_favorite": False,
            "favorite_count": count_favorites(db, user_id),
        }

    item = Favorite(user_id=user_id, question_id=question_id)
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        if retry_on_conflict:
            return toggle_favorite(
                db,
                user_id,
                question_id,
                retry_on_conflict=False,
            )
        raise
    db.refresh(item)
    return {
        "question_id": question_id,
        "is_favorite": True,
        "favorite_count": count_favorites(db, user_id),
    }


def count_favorites(db: Session, user_id: int) -> int:
    return db.query(Favorite).filter(Favorite.user_id == user_id).count()


def serialize_favorite_item(item: Favorite, question: Question) -> dict:
    return {
        "id": item.id,
        "question_id": question.id,
        "question": serialize_question(question, include_solution=False),
        "note": item.note,
        "created_at": item.created_at,
    }

