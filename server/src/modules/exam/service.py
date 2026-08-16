"""考试业务逻辑."""

from collections import defaultdict

from sqlalchemy.orm import Session

from src.common.exceptions import AppException
from src.common.time import utc_now_naive
from src.modules.exam.models import AnswerRecord
from src.modules.exam.schemas import SubmitAnswerRequest
from src.modules.question.models import Paper, Question
from src.modules.question.service import serialize_paper
from src.modules.wrongbook.models import KnowledgeStat, WrongBook


def normalize_answer(answer: str) -> str:
    return "".join(sorted(answer.replace(" ", "").upper()))


def submit_answer(db: Session, user_id: int, payload: SubmitAnswerRequest) -> dict:
    paper = db.query(Paper).filter(Paper.id == payload.paper_id, Paper.user_id == user_id).first()
    if not paper:
        raise AppException(40411, "试卷不存在", status_code=404)

    if payload.question_id not in set(paper.question_ids or []):
        raise AppException(40013, "Question does not belong to this paper", status_code=400)

    question = db.query(Question).filter(Question.id == payload.question_id, Question.is_active == 1).first()
    if not question:
        raise AppException(40412, "题目不存在", status_code=404)

    user_answer = normalize_answer(payload.user_answer)
    correct_answer = normalize_answer(question.answer)
    is_correct = user_answer == correct_answer

    record = (
        db.query(AnswerRecord)
        .filter(
            AnswerRecord.user_id == user_id,
            AnswerRecord.paper_id == payload.paper_id,
            AnswerRecord.question_id == payload.question_id,
        )
        .first()
    )
    recorded_new = record is None
    previous_correct = bool(record.is_correct) if record else False

    if not record:
        record = AnswerRecord(
            user_id=user_id,
            paper_id=payload.paper_id,
            question_id=payload.question_id,
        )
        db.add(record)

    record.user_answer = payload.user_answer
    record.is_correct = 1 if is_correct else 0
    record.time_spent = payload.time_spent
    record.wrong_reason = payload.wrong_reason

    if recorded_new:
        update_user_counters(db, user_id, is_correct)
        update_user_streak(db, user_id)
        update_question_counters(db, question, is_correct)
        update_wrong_book(db, user_id, question, is_correct)
        update_knowledge_stat(db, user_id, paper.exam_type, question, is_correct)
    elif previous_correct != is_correct:
        # 仅在首次记录发生变化时反向修正，避免重复提交重复加总
        adjust_user_counters(db, user_id, previous_correct, is_correct)
        adjust_question_counters(db, question, previous_correct, is_correct)
        adjust_wrong_book(db, user_id, question, previous_correct, is_correct)
        adjust_knowledge_stat(db, user_id, paper.exam_type, question, previous_correct, is_correct)

    db.commit()

    response_payload = {
        "paper_id": payload.paper_id,
        "question_id": payload.question_id,
        "user_answer": payload.user_answer,
        "recorded_new": recorded_new,
        "time_spent": payload.time_spent,
    }
    if paper.mode != "exam":
        response_payload.update({
            "is_correct": is_correct,
            "correct_answer": question.answer,
        })
    return response_payload


def get_result(db: Session, user_id: int, paper_id: int) -> dict:
    paper = db.query(Paper).filter(Paper.id == paper_id, Paper.user_id == user_id).first()
    if not paper:
        raise AppException(40411, "试卷不存在", status_code=404)

    question_ids = paper.question_ids or []
    questions = db.query(Question).filter(Question.id.in_(question_ids)).all() if question_ids else []
    question_map = {question.id: question for question in questions}
    records = (
        db.query(AnswerRecord)
        .filter(AnswerRecord.user_id == user_id, AnswerRecord.paper_id == paper_id)
        .all()
    )
    record_map = {record.question_id: record for record in records}

    total_count = len(question_ids)
    correct_count = 0
    time_used = 0
    knowledge_analysis = defaultdict(lambda: {"total": 0, "correct": 0})
    wrong_questions = []
    review_questions = []

    for question_id in question_ids:
        question = question_map.get(question_id)
        if not question:
            continue
        record = record_map.get(question_id)
        if record:
            time_used += record.time_spent or 0
        is_correct = bool(record and record.is_correct)
        if is_correct:
            correct_count += 1
        else:
            wrong_questions.append(
                {
                    "id": question.id,
                    "stem": question.stem_text,
                    "type_label": question.question_type,
                    "your_answer": record.user_answer if record else "",
                    "correct_answer": question.answer,
                }
            )
        review_questions.append({
            "id": question.id,
            "stem": question.stem_text,
            "type_label": question.question_type,
            "options": question.options or [],
            "user_answer": record.user_answer if record else "",
            "correct_answer": question.answer,
            "analysis": question.analysis or "暂无解析",
            "is_correct": is_correct,
        })
        bucket = knowledge_analysis[question.knowledge_point]
        bucket["total"] += 1
        bucket["correct"] += 1 if is_correct else 0

    knowledge_payload = {
        point: {
            "total": data["total"],
            "correct": data["correct"],
            "correct_rate": round(data["correct"] / data["total"] * 100, 2) if data["total"] else 0,
        }
        for point, data in knowledge_analysis.items()
    }

    if paper.finished_at is None:
        paper.finished_at = utc_now_naive()
    db.commit()

    correct_rate = round(correct_count / total_count * 100, 2) if total_count else 0
    return {
        "paper": serialize_paper(paper, questions),
        "score": correct_rate,
        "correct_count": correct_count,
        "total_count": total_count,
        "correct_rate": correct_rate,
        "time_used": time_used,
        "knowledge_analysis": knowledge_payload,
        "wrong_questions": wrong_questions,
        "review_questions": review_questions,
    }


def update_user_counters(db: Session, user_id: int, is_correct: bool) -> None:
    from src.modules.user.models import User

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return
    user.total_questions = (user.total_questions or 0) + 1
    if is_correct:
        user.total_correct = (user.total_correct or 0) + 1


def update_user_streak(db: Session, user_id: int) -> None:
    from src.modules.user.models import User
    from src.modules.user.service import record_daily_answer

    user = db.query(User).filter(User.id == user_id).first()
    if user:
        record_daily_answer(db, user)


def adjust_user_counters(db: Session, user_id: int, previous_correct: bool, is_correct: bool) -> None:
    from src.modules.user.models import User

    if previous_correct == is_correct:
        return
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return
    if previous_correct and not is_correct:
        user.total_correct = max((user.total_correct or 0) - 1, 0)
    elif not previous_correct and is_correct:
        user.total_correct = (user.total_correct or 0) + 1


def update_question_counters(db: Session, question: Question, is_correct: bool) -> None:
    if is_correct:
        question.correct_count = (question.correct_count or 0) + 1
    else:
        question.wrong_count = (question.wrong_count or 0) + 1
    total = (question.correct_count or 0) + (question.wrong_count or 0)
    question.wrong_rate = round((question.wrong_count or 0) / total * 100, 2) if total else 0


def adjust_question_counters(db: Session, question: Question, previous_correct: bool, is_correct: bool) -> None:
    if previous_correct == is_correct:
        return
    if previous_correct and not is_correct:
        question.correct_count = max((question.correct_count or 0) - 1, 0)
        question.wrong_count = (question.wrong_count or 0) + 1
    elif not previous_correct and is_correct:
        question.wrong_count = max((question.wrong_count or 0) - 1, 0)
        question.correct_count = (question.correct_count or 0) + 1
    total = (question.correct_count or 0) + (question.wrong_count or 0)
    question.wrong_rate = round((question.wrong_count or 0) / total * 100, 2) if total else 0


def update_wrong_book(db: Session, user_id: int, question: Question, is_correct: bool) -> None:
    item = (
        db.query(WrongBook)
        .filter(WrongBook.user_id == user_id, WrongBook.question_id == question.id)
        .first()
    )
    if is_correct:
        if item:
            item.correct_count = (item.correct_count or 0) + 1
            if item.correct_count >= 3:
                item.is_mastered = 1
                item.last_review_at = utc_now_naive()
        return

    if not item:
        item = WrongBook(user_id=user_id, question_id=question.id, wrong_count=1)
        db.add(item)
    else:
        item.wrong_count = (item.wrong_count or 0) + 1

    item.correct_count = 0
    item.is_mastered = 0
    item.last_wrong_at = utc_now_naive()


def adjust_wrong_book(
    db: Session,
    user_id: int,
    question: Question,
    previous_correct: bool,
    is_correct: bool,
) -> None:
    if previous_correct == is_correct:
        return
    item = (
        db.query(WrongBook)
        .filter(WrongBook.user_id == user_id, WrongBook.question_id == question.id)
        .first()
    )
    if not item:
        return
    if previous_correct and not is_correct:
        item.wrong_count = (item.wrong_count or 0) + 1
        item.correct_count = 0
        item.is_mastered = 0
        item.last_wrong_at = utc_now_naive()
    elif not previous_correct and is_correct:
        item.correct_count = (item.correct_count or 0) + 1
        if item.correct_count >= 3:
            item.is_mastered = 1
            item.last_review_at = utc_now_naive()


def update_knowledge_stat(db: Session, user_id: int, exam_type: str, question: Question, is_correct: bool) -> None:
    item = (
        db.query(KnowledgeStat)
        .filter(
            KnowledgeStat.user_id == user_id,
            KnowledgeStat.exam_type == exam_type,
            KnowledgeStat.knowledge_point == question.knowledge_point,
        )
        .first()
    )
    if not item:
        item = KnowledgeStat(
            user_id=user_id,
            exam_type=exam_type,
            knowledge_point=question.knowledge_point,
        )
        db.add(item)

    item.total_answered = (item.total_answered or 0) + 1
    if is_correct:
        item.total_correct = (item.total_correct or 0) + 1
    item.correct_rate = round((item.total_correct or 0) / item.total_answered * 100, 2)


def adjust_knowledge_stat(
    db: Session,
    user_id: int,
    exam_type: str,
    question: Question,
    previous_correct: bool,
    is_correct: bool,
) -> None:
    if previous_correct == is_correct:
        return
    item = (
        db.query(KnowledgeStat)
        .filter(
            KnowledgeStat.user_id == user_id,
            KnowledgeStat.exam_type == exam_type,
            KnowledgeStat.knowledge_point == question.knowledge_point,
        )
        .first()
    )
    if not item:
        return
    if previous_correct and not is_correct:
        item.total_correct = max((item.total_correct or 0) - 1, 0)
    elif not previous_correct and is_correct:
        item.total_correct = (item.total_correct or 0) + 1
    item.correct_rate = round((item.total_correct or 0) / item.total_answered * 100, 2) if item.total_answered else 0
