"""考试业务逻辑."""

from collections import defaultdict

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.common.exceptions import AppException
from src.common.time import utc_now_naive
from src.modules.exam.models import AnswerRecord
from src.modules.exam.schemas import SubmitAnswerRequest
from src.modules.question.models import Paper, Question
from src.modules.question.service import serialize_paper, serialize_question
from src.modules.question.bank import is_self_review, DEFERRED_MODES
import unicodedata
from src.modules.wrongbook.models import KnowledgeStat, WrongBook


def normalize_answer(answer: str) -> str:
    return "".join(sorted(answer.replace(" ", "").upper()))


def grade_answer(question, user_answer):
    if is_self_review(question):
        return None
    if question.question_type in {"single", "judge"}:
        selected = user_answer.strip().upper()
        if selected not in {o["key"] for o in question.options or []}:
            raise AppException(40025, "请选择有效选项", status_code=400)
        return selected == question.answer.strip().upper()
    if question.question_type == "multi":
        return normalize_answer(user_answer) == normalize_answer(question.answer)
    accepted = (question.source_data or {}).get("accepted_answers") or [question.answer]
    normalized = unicodedata.normalize("NFC", user_answer).strip()
    return normalized in {unicodedata.normalize("NFC", answer).strip() for answer in accepted}


def submit_answer(db, user_id, payload, *, retry_on_conflict=True):
    paper = db.query(Paper).filter(Paper.id == payload.paper_id, Paper.user_id == user_id).first()
    if not paper:
        raise AppException(40411, "试卷不存在", status_code=404)
    if paper.finished_at:
        raise AppException(40026, "已交卷，请从成绩页回顾或开始新练习", status_code=400)
    if payload.question_id not in set(paper.question_ids or []):
        raise AppException(40013, "Question does not belong to this paper", status_code=400)
    question = db.query(Question).filter(Question.id == payload.question_id, Question.is_active == 1).first()
    if not question or question.response_mode in DEFERRED_MODES:
        raise AppException(40412, "题目不存在", status_code=404)
    if not payload.user_answer.strip():
        raise AppException(40027, "请先填写答案", status_code=400)
    is_correct = grade_answer(question, payload.user_answer)
    record = db.query(AnswerRecord).filter(AnswerRecord.user_id == user_id, AnswerRecord.paper_id == paper.id, AnswerRecord.question_id == question.id).first()
    recorded_new = record is None
    previous_correct = bool(record and record.is_correct)
    if not record:
        record = AnswerRecord(user_id=user_id, paper_id=paper.id, question_id=question.id, created_at=utc_now_naive())
        db.add(record)
    answer_changed = record.user_answer != payload.user_answer
    record.user_answer = payload.user_answer
    record.is_correct = None if is_correct is None else int(is_correct)
    record.time_spent = payload.time_spent
    record.wrong_reason = payload.wrong_reason
    if is_correct is None:
        if answer_changed:
            record.evaluation_status = "awaiting_self_review"
            record.self_score = None
        if recorded_new:
            from src.modules.user.models import User
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.total_questions = (user.total_questions or 0) + 1
    else:
        record.evaluation_status = "objective"
        if recorded_new:
            update_user_counters(db, user_id, is_correct)
            update_question_counters(db, question, is_correct)
            update_wrong_book(db, user_id, question, is_correct)
            update_knowledge_stat(db, user_id, paper.exam_type, question, is_correct)
        elif previous_correct != is_correct:
            adjust_user_counters(db, user_id, previous_correct, is_correct)
            adjust_question_counters(db, question, previous_correct, is_correct)
            adjust_wrong_book(db, user_id, question, previous_correct, is_correct)
            adjust_knowledge_stat(db, user_id, paper.exam_type, question, previous_correct, is_correct)
    if recorded_new:
        update_user_streak(db, user_id)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        if retry_on_conflict:
            return submit_answer(db, user_id, payload, retry_on_conflict=False)
        raise AppException(40911, "答案保存冲突，请重试", status_code=409)
    response = {"paper_id": paper.id, "question_id": question.id, "user_answer": record.user_answer,
                "recorded_new": recorded_new, "time_spent": record.time_spent}
    if paper.mode != "exam":
        response.update({"is_correct": is_correct, "correct_answer": question.answer,
                         "evaluation_status": record.evaluation_status, "self_score": record.self_score,
                         "solution": serialize_question(question, include_solution=True)})
    return response


def self_review(db, user_id, payload):
    paper = db.query(Paper).filter(Paper.id == payload.paper_id, Paper.user_id == user_id).first()
    record = db.query(AnswerRecord).filter(AnswerRecord.user_id == user_id, AnswerRecord.paper_id == payload.paper_id, AnswerRecord.question_id == payload.question_id).first()
    question = db.get(Question, payload.question_id)
    if not paper or not record or not question or payload.question_id not in (paper.question_ids or []):
        raise AppException(40413, "请先提交本题答案", status_code=404)
    if not is_self_review(question):
        raise AppException(40028, "本题采用自动判分", status_code=400)
    if paper.mode == "exam" and not paper.finished_at:
        raise AppException(40029, "交卷后可进行自评", status_code=400)
    if payload.score > question.max_score:
        raise AppException(40030, "自评分不能超过本题满分", status_code=400)
    record.self_score = payload.score
    record.evaluation_status = "self_reviewed"
    db.commit()
    return {"question_id": question.id, "evaluation_status": record.evaluation_status,
            "self_score": record.self_score, "max_score": question.max_score}


def get_result(db, user_id, paper_id):
    paper = db.query(Paper).filter(Paper.id == paper_id, Paper.user_id == user_id).first()
    if not paper:
        raise AppException(40411, "试卷不存在", status_code=404)
    questions = db.query(Question).filter(Question.id.in_(paper.question_ids or [])).all()
    question_map = {q.id: q for q in questions}
    questions = [question_map[qid] for qid in paper.question_ids or [] if qid in question_map]
    records = db.query(AnswerRecord).filter(AnswerRecord.user_id == user_id, AnswerRecord.paper_id == paper.id).all()
    record_map = {record.question_id: record for record in records}
    automatic = [q for q in questions if not is_self_review(q)]
    correct_count = sum(bool(record_map.get(q.id) and record_map[q.id].is_correct) for q in automatic)
    knowledge_analysis = defaultdict(lambda: {"total": 0, "correct": 0, "correct_rate": 0})
    wrong_questions, review_questions = [], []
    pending, self_score, self_max_score = 0, 0, 0
    for question in questions:
        record = record_map.get(question.id)
        correct = bool(record and record.is_correct) if not is_self_review(question) else None
        if is_self_review(question):
            if record:
                pending += record.self_score is None
                if record.self_score is not None:
                    self_score += record.self_score
                    self_max_score += question.max_score
        else:
            bucket = knowledge_analysis[question.subject if paper.exam_type == "CSCA" else question.knowledge_point]
            bucket["total"] += 1
            bucket["correct"] += int(correct)
            bucket["correct_rate"] = round(bucket["correct"] / bucket["total"] * 100, 2)
            if record and not correct:
                wrong_questions.append({"id": question.id, "stem": question.stem_text, "type_label": question.question_type,
                                        "your_answer": record.user_answer, "correct_answer": question.answer})
        solution = serialize_question(question, include_solution=True)
        status = record.evaluation_status if record else "unanswered"
        review_questions.append({"id": question.id, "stem": question.stem_text, "type_label": question.question_type,
                                 "options": solution["options"], "user_answer": record.user_answer if record else "",
                                 "correct_answer": question.answer, "analysis": question.analysis or "",
                                 "is_correct": correct, "evaluation_status": status,
                                 "self_score": record.self_score if record else None, "question": solution})
    if not paper.finished_at:
        paper.finished_at = utc_now_naive()
        db.commit()
    rate = round(correct_count / len(automatic) * 100, 2) if automatic else 0
    return {"paper": serialize_paper(paper, questions, include_solution=True), "score": rate,
            "correct_count": correct_count, "total_count": len(questions), "correct_rate": rate,
            "time_used": sum(record.time_spent or 0 for record in records), "knowledge_analysis": dict(knowledge_analysis),
            "wrong_questions": wrong_questions, "review_questions": review_questions,
            "objective_count": len(automatic), "subjective_count": len(questions) - len(automatic),
            "pending_self_review": pending, "self_score": self_score, "self_max_score": self_max_score,
            "subjective_answered_count": sum(q.id in record_map for q in questions if is_self_review(q)),
            "unanswered_count": len(questions) - len(records)}


def update_user_counters(db: Session, user_id: int, is_correct: bool) -> None:
    from src.modules.user.models import User

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return
    user.total_questions = (user.total_questions or 0) + 1
    user.total_objective = (user.total_objective or 0) + 1
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
    bucket_key = question.subject if exam_type == "CSCA" else question.knowledge_point
    item = (
        db.query(KnowledgeStat)
        .filter(
            KnowledgeStat.user_id == user_id,
            KnowledgeStat.exam_type == exam_type,
            KnowledgeStat.knowledge_point == bucket_key,
        )
        .first()
    )
    if not item:
        item = KnowledgeStat(
            user_id=user_id,
            exam_type=exam_type,
            knowledge_point=bucket_key,
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
    bucket_key = question.subject if exam_type == "CSCA" else question.knowledge_point
    if previous_correct == is_correct:
        return
    item = (
        db.query(KnowledgeStat)
        .filter(
            KnowledgeStat.user_id == user_id,
            KnowledgeStat.exam_type == exam_type,
            KnowledgeStat.knowledge_point == bucket_key,
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
