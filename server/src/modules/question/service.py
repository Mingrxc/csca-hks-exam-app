"""题库业务逻辑."""

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from src.common.exceptions import AppException
from src.modules.question.models import Paper, Question
from src.modules.question.schemas import GeneratePaperRequest


DIFFICULTY_ORDER = case(
    (Question.difficulty == "easy", 1),
    (Question.difficulty == "medium", 2),
    (Question.difficulty == "hard", 3),
    else_=4,
)


def serialize_question(question: Question, include_solution: bool = True) -> dict:
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
        .filter(Paper.user_id == user_id)
        .order_by(Paper.created_at.desc())
        .limit(limit)
        .all()
    )
    return [serialize_paper(paper, []) for paper in papers]


def generate_paper(db: Session, user_id: int, payload: GeneratePaperRequest) -> dict:
    query = db.query(Question).filter(
        Question.exam_type == payload.exam_type.value,
        Question.is_active == 1,
    )

    if payload.difficulty.value != "all":
        query = query.filter(Question.difficulty == payload.difficulty.value)

    if payload.strategy.value == "knowledge" and payload.knowledge_points:
        query = query.filter(Question.knowledge_point.in_(payload.knowledge_points))

    if payload.strategy.value == "progressive":
        query = query.order_by(DIFFICULTY_ORDER, func.rand())
    else:
        query = query.order_by(func.rand())

    questions = query.limit(payload.question_count).all()
    if not questions:
        raise AppException(40402, "没有找到符合条件的题目", status_code=404)

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

    return serialize_paper(paper, questions, include_solution=payload.mode != "exam")


def serialize_paper(paper: Paper, questions: list[Question], include_solution: bool = True) -> dict:
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
            serialize_question(question, include_solution=include_solution)
            for question in questions
        ],
    }


def strategy_label(strategy: str) -> str:
    return {
        "random": "随机组卷",
        "knowledge": "知识点专项",
        "progressive": "难度递进",
        "real": "模拟真题",
    }.get(strategy, "练习试卷")
