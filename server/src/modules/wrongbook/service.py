"""错题本业务逻辑."""

from datetime import datetime

from sqlalchemy.orm import Session

from src.common.exceptions import AppException
from src.modules.exam.models import AnswerRecord
from src.modules.question.models import Paper, Question
from src.modules.question.service import serialize_paper, serialize_question
from src.modules.wrongbook.models import WrongBook


def list_wrong_questions(
    db: Session,
    user_id: int,
    exam_type: str = "all",
    knowledge: str = "all",
    wrong_count: str = "all",
) -> list[dict]:
    query = (
        db.query(WrongBook, Question)
        .join(Question, Question.id == WrongBook.question_id)
        .filter(WrongBook.user_id == user_id)
        .order_by(WrongBook.last_wrong_at.desc())
    )

    if exam_type != "all":
        query = query.filter(Question.exam_type == exam_type)
    if knowledge != "all":
        query = query.filter(Question.knowledge_point == knowledge)
    if wrong_count == "1":
        query = query.filter(WrongBook.wrong_count == 1)
    elif wrong_count == "2+":
        query = query.filter(WrongBook.wrong_count >= 2)

    return [serialize_wrong_item(item, question) for item, question in query.all()]


def get_wrong_detail(db: Session, user_id: int, wrongbook_id: int) -> dict:
    row = (
        db.query(WrongBook, Question)
        .join(Question, Question.id == WrongBook.question_id)
        .filter(WrongBook.id == wrongbook_id, WrongBook.user_id == user_id)
        .first()
    )
    if not row:
        raise AppException(40421, "错题记录不存在", status_code=404)

    item, question = row
    return serialize_wrong_detail(db, user_id, item, question)


def get_wrong_detail_by_question(db: Session, user_id: int, question_id: int) -> dict:
    row = (
        db.query(WrongBook, Question)
        .join(Question, Question.id == WrongBook.question_id)
        .filter(WrongBook.user_id == user_id, WrongBook.question_id == question_id)
        .first()
    )
    if not row:
        raise AppException(40421, "错题记录不存在", status_code=404)

    item, question = row
    return serialize_wrong_detail(db, user_id, item, question)


def serialize_wrong_detail(db: Session, user_id: int, item: WrongBook, question: Question) -> dict:
    latest_record = (
        db.query(AnswerRecord)
        .filter(
            AnswerRecord.user_id == user_id,
            AnswerRecord.question_id == question.id,
            AnswerRecord.is_correct == 0,
        )
        .order_by(AnswerRecord.created_at.desc(), AnswerRecord.id.desc())
        .first()
    )
    return {
        **serialize_wrong_item(item, question),
        "question": serialize_question(question),
        "last_user_answer": latest_record.user_answer if latest_record else "",
        "wrong_options_analysis": question.wrong_options_analysis or {},
    }


def mark_mastered(db: Session, user_id: int, wrongbook_id: int) -> dict:
    item = (
        db.query(WrongBook)
        .filter(WrongBook.id == wrongbook_id, WrongBook.user_id == user_id)
        .first()
    )
    if not item:
        raise AppException(40421, "错题记录不存在", status_code=404)

    item.is_mastered = 0 if item.is_mastered else 1
    item.last_review_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return {
        "id": item.id,
        "question_id": item.question_id,
        "is_mastered": bool(item.is_mastered),
    }


def generate_redo_paper(db: Session, user_id: int, exam_type: str, limit: int = 20) -> dict:
    rows = (
        db.query(WrongBook, Question)
        .join(Question, Question.id == WrongBook.question_id)
        .filter(
            WrongBook.user_id == user_id,
            WrongBook.is_mastered == 0,
            Question.is_active == 1,
            Question.exam_type == exam_type,
        )
        .order_by(WrongBook.last_wrong_at.desc(), WrongBook.id.desc())
        .limit(limit)
        .all()
    )
    if not rows:
        raise AppException(40422, "No unmastered wrong questions found", status_code=404)

    questions = [question for _, question in rows]
    paper = Paper(
        user_id=user_id,
        title=f"{exam_type} 错题重做",
        exam_type=exam_type,
        strategy="knowledge",
        question_ids=[question.id for question in questions],
        total_score=len(questions),
        time_limit=0,
        mode="practice",
        difficulty="all",
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)
    return serialize_paper(paper, questions, include_solution=True)


def get_related(db: Session, question_id: int, limit: int = 3) -> list[dict]:
    question = db.query(Question).filter(Question.id == question_id, Question.is_active == 1).first()
    if not question:
        raise AppException(40401, "题目不存在", status_code=404)

    related = (
        db.query(Question)
        .filter(
            Question.id != question.id,
            Question.is_active == 1,
            Question.exam_type == question.exam_type,
            Question.knowledge_point == question.knowledge_point,
        )
        .limit(limit)
        .all()
    )
    return [
        {
            **serialize_question(item, include_solution=False),
            "similarity_score": 1.0,
        }
        for item in related
    ]


def serialize_wrong_item(item: WrongBook, question: Question) -> dict:
    return {
        "id": item.id,
        "question_id": question.id,
        "stem": question.stem_text,
        "type": question.question_type,
        "difficulty": question.difficulty,
        "knowledge_point": question.knowledge_point,
        "wrong_count": item.wrong_count or 0,
        "correct_count": item.correct_count or 0,
        "is_mastered": bool(item.is_mastered),
        "first_wrong_at": item.first_wrong_at,
        "last_wrong_at": item.last_wrong_at,
        "last_review_at": item.last_review_at,
    }
