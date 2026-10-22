"""题库业务逻辑."""

import random

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.common.exceptions import AppException
from src.modules.exam.models import AnswerRecord
from src.modules.question.models import Paper, Question
from src.modules.question.schemas import GeneratePaperRequest
from src.modules.question.bank import DEFERRED_MODES, PRACTICE_PROFILES, is_self_review, media_url


DIFFICULTY_ORDER = {"easy": 1, "medium": 2, "hard": 3}
REAL_EXAM_QUESTION_COUNTS = {
    "CSCA": {
        "数学": 48,
        "物理": 48,
        "化学": 48,
        "理科中文": 80,
        "文科中文": 80,
    },

}


def special_field_for_exam(exam_type: str):
    return Question.subject if exam_type == "CSCA" else Question.knowledge_point


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
        "stem_image": media_url(question.stem_image),
        "stem_audio": media_url(question.stem_audio),
        "options": [{**option, **({"image": media_url(option["image"])} if option.get("image") else {})} for option in question.options or []],
        "bank_id": question.bank_id,
        "exam_version": question.exam_version,
        "level": question.level,
        "knowledge_module": question.knowledge_module,
        "material_id": question.material_id,
        "response_mode": question.response_mode,
        "scoring_mode": question.scoring_mode,
        "max_score": question.max_score,
    }
    meta = question.source_data or {}
    for name in ("native_task", "source_type", "minimum_characters", "response_seconds", "source_language", "target_language", "translation_mode", "stimulus_note"):
        if name in meta:
            payload[name] = meta[name]
    if is_favorite is not None:
        payload["is_favorite"] = is_favorite
    if include_solution:
        payload.update({
            "answer": question.answer,
            "analysis": question.analysis,
            "wrong_options_analysis": question.wrong_options_analysis or {},
        })
        for name in ("transcript", "accepted_answers", "grading_key_points", "grading_rubric", "term_notes"):
            if name in meta:
                payload[name] = meta[name]
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
        paper_questions = db.query(Question).filter(Question.id.in_(paper.question_ids or [])).all()
        objective_count = sum(not is_self_review(q) for q in paper_questions)
        correct_count = sum(1 for record in paper_records if record.is_correct)
        correct_rate = round(correct_count / objective_count * 100, 2) if objective_count else 0
        result.append({
            "id": paper.id,
            "title": paper.title,
            "exam_type": paper.exam_type,
            "question_count": question_count,
            "objective_count": objective_count,
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
        Question.response_mode.notin_(DEFERRED_MODES),
    )
    if payload.exam_type.value == "HKS":
        if not payload.level or payload.exam_version != "HSK3.0":
            raise AppException(40021, "请选择 HSK 考试版本和等级", status_code=400)
        query = query.filter(Question.exam_version == payload.exam_version, Question.level == payload.level)
    elif payload.level or payload.exam_version:
        raise AppException(40022, "CSCA 不使用 HSK 版本或等级", status_code=400)
    unfiltered = query.order_by(Question.bank_id, Question.id).all()
    if payload.subjects:
        query = query.filter(Question.subject.in_(payload.subjects))
    if payload.knowledge_modules:
        query = query.filter(Question.knowledge_module.in_(payload.knowledge_modules))
    if payload.knowledge_points:
        query = query.filter(Question.knowledge_point.in_(payload.knowledge_points))
    candidates = query.order_by(Question.bank_id, Question.id).all()
    selected_materials = {(q.subject, q.material_id) for q in candidates if q.material_id}
    if selected_materials:
        selected_ids = {q.id for q in candidates}
        candidates = [q for q in unfiltered if q.id in selected_ids or (q.subject, q.material_id) in selected_materials]
    if payload.strategy.value == "real":
        if payload.knowledge_modules or payload.knowledge_points or (payload.exam_type.value == "HKS" and payload.subjects):
            raise AppException(40023, "限时综合练习不限定模块或知识点", status_code=400)
        if payload.exam_type.value == "HKS":
            questions = []
            for subject, count in PRACTICE_PROFILES[payload.level].items():
                questions.extend(select_questions([q for q in candidates if q.subject == subject], count, strict=True))
        else:
            if len(payload.subjects) != 1:
                raise AppException(40024, "请选择一门 CSCA 科目", status_code=400)
            count = REAL_EXAM_QUESTION_COUNTS["CSCA"].get(payload.subjects[0], 48)
            questions = select_questions(candidates, count, strict=True)
    else:
        if payload.strategy.value != "progressive" and payload.difficulty.value != "all":
            # Keep complete materials: a mixed-difficulty group is not split by a filter.
            blocked = {q.material_id for q in candidates if q.material_id and q.difficulty != payload.difficulty.value}
            candidates = [q for q in candidates if q.difficulty == payload.difficulty.value and q.material_id not in blocked]
        questions = select_questions(candidates, payload.question_count)
        if payload.strategy.value == "progressive":
            groups = group_questions(questions)
            groups.sort(key=lambda group: max(DIFFICULTY_ORDER.get(q.difficulty, 4) for q in group))
            questions = [q for group in groups for q in group]
    selected_ids = [q.id for q in questions]

    db.query(Question).filter(Question.id.in_(selected_ids)).update(
        {Question.usage_count: func.coalesce(Question.usage_count, 0) + 1},
        synchronize_session=False,
    )

    parts = [payload.exam_type.value, payload.exam_version, f"{payload.level}级" if payload.level else None,
             "/".join(payload.subjects), strategy_label(payload.strategy.value)]
    title = " ".join(part for part in parts if part)
    paper = Paper(
        user_id=user_id,
        title=title,
        exam_type=payload.exam_type.value,
        strategy=payload.strategy.value,
        question_ids=[question.id for question in questions],
        total_score=sum(q.max_score for q in questions),
        time_limit=payload.time_limit,
        mode=payload.mode,
        difficulty=payload.difficulty.value,
        selection={"exam_version": payload.exam_version, "level": payload.level, "subjects": payload.subjects,
                   "knowledge_modules": payload.knowledge_modules, "knowledge_points": payload.knowledge_points,
                   "requested_count": payload.question_count, "actual_count": len(questions)},
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
        include_solution=False,
        favorite_ids=favorite_ids,
    )


def serialize_paper(
    paper: Paper,
    questions: list[Question],
    include_solution: bool = False,
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
        "selection": paper.selection,
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
        "real": "限时综合练习",
    }.get(strategy, "练习试卷")


def group_questions(questions):
    groups = {}
    for question in questions:
        key = (question.exam_version, question.level, question.subject, question.material_id or f"question:{question.id}")
        groups.setdefault(key, []).append(question)
    return list(groups.values())


def select_questions(candidates, count, strict=False):
    if not candidates or (strict and len(candidates) < count):
        raise AppException(40402, "符合条件的题目不足，请调整筛选或选择日常练习", status_code=404)
    if not any(q.material_id for q in candidates):
        by_id = {q.id: q for q in candidates}
        return [by_id[qid] for qid in random.sample(list(by_id), min(count, len(candidates))) ]
    groups = group_questions(candidates)
    groups = random.sample(groups, len(groups))
    # Subset selection preserves whole groups while matching the requested size where possible.
    sizes = {0: []}
    for index, group in enumerate(groups):
        for total, indices in list(sizes.items()):
            new_total = total + len(group)
            if new_total <= count and new_total not in sizes:
                sizes[new_total] = indices + [index]
    total = max(sizes)
    if strict and total != count:
        raise AppException(40404, "完整题组无法组成所需题量，请选择日常练习", status_code=404)
    indices = sizes[total] if total else [min(range(len(groups)), key=lambda i: len(groups[i]))]
    return [q for index in indices for q in groups[index]]


def get_catalog(db: Session):
    fields = [Question.exam_type, Question.exam_version, Question.level, Question.subject,
              Question.knowledge_module, Question.knowledge_point]
    rows = db.query(*fields, func.count(Question.id)).filter(
        Question.is_active == 1, Question.response_mode.notin_(DEFERRED_MODES),
    ).group_by(*fields).order_by(*fields).all()
    names = [field.key for field in fields] + ["count"]
    return [dict(zip(names, row)) for row in rows]
