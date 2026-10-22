"""New-bank contracts, media isolation, grouped selection and self-assessment."""
from contextlib import contextmanager
from dataclasses import replace
from functools import lru_cache
from pathlib import Path
import sys

import pytest

from src.common.exceptions import AppException
from src.modules.exam.models import AnswerRecord
from src.modules.exam.schemas import SelfReviewRequest, SubmitAnswerRequest
from src.modules.exam.service import get_result, grade_answer, self_review, submit_answer
from src.modules.question.models import Paper, Question
from src.modules.question.schemas import GeneratePaperRequest
from src.modules.question.service import generate_paper, serialize_question
from src.modules.question.bank import PRACTICE_PROFILES
from src.modules.user.models import User
from src.modules.user.service import get_dashboard
from src.modules.wrongbook.models import WrongBook

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from import_questions import load_questions, upsert_questions


@lru_cache
def bank():
    return load_questions(ROOT.parent / "original_question_bank")


def make_question(**overrides):
    values = dict(exam_type="HKS", exam_version="HSK3.0", level="1", subject="阅读", knowledge_point="词义",
                  difficulty="easy", question_type="single", response_mode="choice", scoring_mode="objective",
                  stem_text="选择正确词语", options=[{"key": "A", "text": "老师"}, {"key": "B", "text": "学生"}],
                  answer="A", analysis="答案依据与选项辨析", max_score=1, is_active=1)
    values.update(overrides)
    return Question(**values)


def setup_paper(db, questions, mode="practice"):
    user = User(openid="bank-v2-user")
    db.add_all([user, *questions]); db.commit()
    paper = Paper(user_id=user.id, title="新版练习", exam_type="HKS", strategy="random", question_ids=[q.id for q in questions], mode=mode)
    db.add(paper); db.commit()
    return user, paper


def test_complete_bank_preserves_source_and_excludes_all_spoken_tasks():
    questions, report = bank()
    assert not report.invalid and report.duplicate_in_source == 0
    assert len(questions) == 1221
    assert sum(q.exam_type == "HKS" for q in questions) == 671
    assert report.skipped_resources["deferred_oral_questions"] == 99
    assert len({q.bank_id for q in questions}) == len(questions)
    assert all(q.source_data["question_id"] == q.bank_id for q in questions)
    assert not any(q.response_mode in {"oral", "oral_translation"} for q in questions)
    assert sum(q.response_mode in {"written_response", "essay", "short_answer", "translation"} for q in questions) == 81
    image_question = next(q for q in questions if any(o.get("image") for o in q.options))
    assert image_question.options[0]["image"]
    assert max(len(q.answer) for q in questions) > 256


def test_every_timed_profile_can_be_built_from_complete_source_groups():
    questions, _ = bank()
    for level, profile in PRACTICE_PROFILES.items():
        for subject, requested in profile.items():
            groups = {}
            for q in questions:
                if q.level == level and q.subject == subject:
                    key = q.material_id or q.bank_id
                    groups[key] = groups.get(key, 0) + 1
            attainable = {0}
            for size in groups.values():
                attainable |= {count + size for count in list(attainable)}
            assert requested in attainable, (level, subject, requested)


def test_stable_id_updates_changed_question_instead_of_inserting(db_session, monkeypatch):
    import src.config.database as database
    @contextmanager
    def session():
        yield db_session
    monkeypatch.setattr(database, "SessionLocal", session)
    original = bank()[0][0]
    assert upsert_questions([original]) == (1, 0)
    revised = replace(original, stem_text="校订后的题干", knowledge_point="校订后的知识点")
    assert upsert_questions([revised]) == (0, 1)
    assert db_session.query(Question).count() == 1
    assert db_session.query(Question).one().stem_text == revised.stem_text


def test_hsk_requires_explicit_version_and_level(db_session):
    user, _ = setup_paper(db_session, [make_question()])
    with pytest.raises(AppException, match="版本和等级"):
        generate_paper(db_session, user.id, GeneratePaperRequest(exam_type="HKS"))


def test_level_selection_and_solution_redaction(db_session):
    first = make_question(source_data={"transcript": "私有原文", "accepted_answers": ["答案"], "grading_key_points": ["秘密要点"]})
    second = make_question(level="2")
    user, _ = setup_paper(db_session, [first, second])
    paper = generate_paper(db_session, user.id, GeneratePaperRequest(exam_type="HKS", exam_version="HSK3.0", level="1", question_count=1))
    assert paper["question_ids"] == [first.id]
    assert not {"answer", "transcript", "analysis", "accepted_answers", "grading_key_points"} & set(paper["questions"][0])


def test_knowledge_filter_and_small_count_keep_material_group_complete(db_session):
    questions = [make_question(material_id="shared", bank_id=f"group-{i}", knowledge_point=f"point-{i}") for i in range(3)]
    user, _ = setup_paper(db_session, questions)
    paper = generate_paper(db_session, user.id, GeneratePaperRequest(exam_type="HKS", exam_version="HSK3.0", level="1", subjects=["阅读"], knowledge_points=["point-0"], question_count=1))
    assert set(paper["question_ids"]) == {q.id for q in questions}
    assert len(paper["questions"]) == 3


def test_timed_profile_reports_insufficient_questions(db_session):
    user, _ = setup_paper(db_session, [make_question()])
    with pytest.raises(AppException, match="不足"):
        generate_paper(db_session, user.id, GeneratePaperRequest(exam_type="HKS", exam_version="HSK3.0", level="1", strategy="real"))


def test_character_answers_preserve_order_and_accept_declared_variants():
    question = make_question(question_type="fill", response_mode="character", scoring_mode="exact_or_handwriting_review", answer="中国", source_data={"accepted_answers": ["中国", "中华"]})
    assert grade_answer(question, "中国") is True
    assert grade_answer(question, "中华") is True
    assert grade_answer(question, "国中") is False


def test_open_answer_is_not_automatically_wrong_or_in_wrongbook(db_session):
    objective = make_question()
    essay = make_question(question_type="fill", response_mode="essay", scoring_mode="rubric", options=[], max_score=10, answer="参考表达", source_data={"grading_key_points": ["言之有理"]})
    user, paper = setup_paper(db_session, [objective, essay])
    submit_answer(db_session, user.id, SubmitAnswerRequest(paper_id=paper.id, question_id=objective.id, user_answer="A"))
    response = submit_answer(db_session, user.id, SubmitAnswerRequest(paper_id=paper.id, question_id=essay.id, user_answer="我自己的合理表达" * 100))
    assert response["is_correct"] is None
    assert response["evaluation_status"] == "awaiting_self_review"
    assert response["solution"]["grading_key_points"] == ["言之有理"]
    assert db_session.query(WrongBook).count() == 0
    assert user.total_questions == 2 and user.total_objective == 1
    result = get_result(db_session, user.id, paper.id)
    assert result["correct_rate"] == 100 and result["objective_count"] == 1
    assert result["subjective_count"] == 1 and result["pending_self_review"] == 1
    self_review(db_session, user.id, SelfReviewRequest(paper_id=paper.id, question_id=essay.id, score=8))
    self_review(db_session, user.id, SelfReviewRequest(paper_id=paper.id, question_id=essay.id, score=9))
    result = get_result(db_session, user.id, paper.id)
    assert result["self_score"] == 9 and result["self_max_score"] == 10
    assert result["pending_self_review"] == 0 and result["correct_rate"] == 100
    assert db_session.query(AnswerRecord).count() == 2


def test_exam_hides_solution_and_disallows_self_review_until_finished(db_session):
    essay = make_question(question_type="fill", response_mode="essay", scoring_mode="rubric", options=[], max_score=10)
    user, paper = setup_paper(db_session, [essay], mode="exam")
    response = submit_answer(db_session, user.id, SubmitAnswerRequest(paper_id=paper.id, question_id=essay.id, user_answer="自己的回答"))
    assert "solution" not in response and "correct_answer" not in response
    with pytest.raises(AppException, match="交卷后"):
        self_review(db_session, user.id, SelfReviewRequest(paper_id=paper.id, question_id=essay.id, score=7))
    get_result(db_session, user.id, paper.id)
    with pytest.raises(AppException, match="满分"):
        self_review(db_session, user.id, SelfReviewRequest(paper_id=paper.id, question_id=essay.id, score=11))
    with pytest.raises(AppException):
        self_review(db_session, user.id + 1, SelfReviewRequest(paper_id=paper.id, question_id=essay.id, score=7))
    assert self_review(db_session, user.id, SelfReviewRequest(paper_id=paper.id, question_id=essay.id, score=7))["self_score"] == 7


def test_open_only_dashboard_and_history_have_no_automatic_denominator(db_session):
    essay = make_question(question_type="fill", response_mode="essay", scoring_mode="rubric", options=[], max_score=10)
    user, paper = setup_paper(db_session, [essay])
    submit_answer(db_session, user.id, SubmitAnswerRequest(paper_id=paper.id, question_id=essay.id, user_answer="我的表达"))
    get_result(db_session, user.id, paper.id)
    dashboard = get_dashboard(db_session, user)
    assert dashboard["today_stats"]["question_count"] == 1
    assert dashboard["today_stats"]["objective_count"] == 0
    assert dashboard["today_stats"]["wrong_count"] == 0
    assert dashboard["recent_papers"][0]["objective_count"] == 0


def test_study_day_bounds_compare_utc_timestamps_in_beijing_day():
    from datetime import date, datetime
    from src.common.time import study_day_utc_bounds
    start, end = study_day_utc_bounds(date(2026, 10, 22))
    assert start == datetime(2026, 10, 21, 16)
    assert end == datetime(2026, 10, 22, 16)


def test_media_endpoint_serves_only_binary_assets(client):
    questions, _ = bank()
    audio = next(q.stem_audio for q in questions if q.stem_audio)
    response = client.get("/api/v1/question/media/" + audio)
    assert response.status_code == 200 and response.content[:4] == b"RIFF"
    assert client.get("/api/v1/question/media/" + audio + ".meta.json").status_code == 404
    assert client.get("/api/v1/question/media/HSK/HSK3.0/1级/听力/questions.json").status_code == 404
