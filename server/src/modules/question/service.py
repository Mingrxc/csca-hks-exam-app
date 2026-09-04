"""题库业务逻辑."""

import random

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.common.exceptions import AppException
from src.modules.exam.models import AnswerRecord
from src.modules.question.models import Paper, Question
from src.modules.question.schemas import GeneratePaperRequest


DIFFICULTY_ORDER = {"easy": 1, "medium": 2, "hard": 3}
REAL_EXAM_QUESTION_COUNTS = {
    "CSCA": {
        "数学": 48,
        "物理": 48,
        "化学": 48,
        "理科中文": 80,
        "文科中文": 80,
    },
    "HKS": {
        "听力": 45,
        "阅读": 40,
        "书写": 15,
        "口语": 14,
        "翻译": 10,
    },
}
REAL_EXAM_DEFAULT_QUESTION_COUNTS = {"CSCA": 48, "HKS": 100}


def special_field_for_exam(exam_type: str):
    return Question.subject if exam_type == "CSCA" else Question.knowledge_point


def paper_special_field_for_exam(exam_type: str):
    """组卷页使用考试一级科目筛选，HKS 不使用细分知识点。"""
    return Question.subject


def serialize_question(
    question: Question,
    include_solution: bool = True,
    is_favorite: bool | None = None,
) -> dict:
    payload = {
        "id": question.id,
        "exam_type": question.exam_type,
        "subject": question.subject,
        "knowledge_point": question.knowledge_point,
        "difficulty": question.difficulty,
        "question_type": question.question_type,
        "stem_text": question.stem_text,
        "stem_image": question.stem_image,
        "stem_audio": question.stem_audio,
        "options": question.options or [],
    }
    if is_favorite is not None:
        payload["is_favorite"] = is_favorite
    if include_solution:
        payload.update({
            "answer": question.answer,
            "analysis": question.analysis,
        })
    return payload


def get_question(db: Session, question_id: int) -> dict:
    question = db.query(Question).filter(Question.id == question_id, Question.is_active == 1).first()
    if not question:
        raise AppException(40401, "题目不存在", status_code=404)
    return serialize_question(question, include_solution=False)


def list_papers(db: Session, user_id: int, limit: int = 20) -> list[dict]:
    papers = (
        db.query(Paper)
        .filter(Paper.user_id == user_id, Paper.finished_at.isnot(None))
        .order_by(Paper.finished_at.desc(), Paper.id.desc())
        .limit(limit)
        .all()
    )
    if not papers:
        return []

    records = (
        db.query(AnswerRecord)
        .filter(
            AnswerRecord.user_id == user_id,
            AnswerRecord.paper_id.in_([paper.id for paper in papers]),
        )
        .all()
    )
    records_by_paper: dict[int, list[AnswerRecord]] = {}
    for record in records:
        records_by_paper.setdefault(record.paper_id, []).append(record)

    result = []
    for paper in papers:
        paper_records = records_by_paper.get(paper.id, [])
        question_count = len(paper.question_ids or [])
        correct_count = sum(1 for record in paper_records if record.is_correct)
        correct_rate = round(correct_count / question_count * 100, 2) if question_count else 0
        result.append({
            "id": paper.id,
            "title": paper.title,
            "exam_type": paper.exam_type,
            "question_count": question_count,
            "score": correct_rate,
            "correct_rate": correct_rate,
            "time_used": sum(record.time_spent or 0 for record in paper_records),
            "passed": correct_rate >= 60,
            "finished_at": paper.finished_at,
        })
    return result


def list_special_options(db: Session, exam_type: str, limit: int = 24) -> list[dict]:
    field = special_field_for_exam(exam_type)
    rows = (
        db.query(field.label("value"), func.count(Question.id).label("count"))
        .filter(Question.exam_type == exam_type, Question.is_active == 1)
        .group_by(field)
        .order_by(func.count(Question.id).desc(), field.asc())
        .limit(limit)
        .all()
    )
    return [
        {"value": value, "label": value, "count": count}
        for value, count in rows
    ]


def generate_paper(db: Session, user_id: int, payload: GeneratePaperRequest) -> dict:
    query = db.query(Question).filter(
        Question.exam_type == payload.exam_type.value,
        Question.is_active == 1,
    )

    if payload.strategy.value not in {"progressive", "real"} and payload.difficulty.value != "all":
        query = query.filter(Question.difficulty == payload.difficulty.value)

    is_hks_real_exam = payload.strategy.value == "real" and payload.exam_type.value == "HKS"
    if (
        payload.strategy.value in {"knowledge", "progressive", "real"}
        and payload.knowledge_points
        and not is_hks_real_exam
    ):
        field = paper_special_field_for_exam(payload.exam_type.value)
        query = query.filter(field.in_(payload.knowledge_points))

    candidate_ids = [question_id for (question_id,) in query.with_entities(Question.id).all()]
    if not candidate_ids:
        raise AppException(40402, "没有找到符合条件的题目", status_code=404)

    if payload.strategy.value == "real":
        question_count = (
            REAL_EXAM_DEFAULT_QUESTION_COUNTS["HKS"]
            if is_hks_real_exam
            else REAL_EXAM_QUESTION_COUNTS[payload.exam_type.value].get(
                (payload.knowledge_points or [""])[0],
                REAL_EXAM_DEFAULT_QUESTION_COUNTS[payload.exam_type.value],
            )
        )
    else:
        question_count = payload.question_count
    selected_ids = random.sample(candidate_ids, min(question_count, len(candidate_ids)))
    selected_questions = db.query(Question).filter(Question.id.in_(selected_ids)).all()
    question_map = {question.id: question for question in selected_questions}
    questions = [question_map[question_id] for question_id in selected_ids]
    if payload.strategy.value == "progressive":
        questions.sort(key=lambda question: DIFFICULTY_ORDER.get(question.difficulty, 4))

    for question in questions:
        question.usage_count = (question.usage_count or 0) + 1

    title = f"{payload.exam_type.value} {strategy_label(payload.strategy.value)}"
    paper = Paper(
        user_id=user_id,
        title=title,
        exam_type=payload.exam_type.value,
        strategy=payload.strategy.value,
        question_ids=[question.id for question in questions],
        total_score=len(questions),
        time_limit=payload.time_limit,
        mode=payload.mode,
        difficulty=payload.difficulty.value,
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)

    from src.modules.favorite.models import Favorite

    favorite_ids = {
        question_id
        for (question_id,) in db.query(Favorite.question_id)
        .filter(Favorite.user_id == user_id, Favorite.question_id.in_(selected_ids))
        .all()
    }
    return serialize_paper(
        paper,
        questions,
        include_solution=payload.mode != "exam",
        favorite_ids=favorite_ids,
    )


def serialize_paper(
    paper: Paper,
    questions: list[Question],
    include_solution: bool = True,
    favorite_ids: set[int] | None = None,
) -> dict:
    return {
        "id": paper.id,
        "title": paper.title,
        "exam_type": paper.exam_type,
        "strategy": paper.strategy,
        "question_ids": paper.question_ids or [],
        "total_score": paper.total_score,
        "time_limit": paper.time_limit,
        "mode": paper.mode,
        "difficulty": paper.difficulty,
        "questions": [
            serialize_question(
                question,
                include_solution=include_solution,
                is_favorite=question.id in favorite_ids if favorite_ids is not None else None,
            )
            for question in questions
        ],
    }


def strategy_label(strategy: str) -> str:
    return {
        "random": "随机组卷",
        "knowledge": "专项训练",
        "progressive": "难度递进",
        "real": "模拟真题",
    }.get(strategy, "练习试卷")
