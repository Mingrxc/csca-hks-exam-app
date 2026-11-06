from datetime import date, datetime, timezone

import pytest

from main import app
from src.common.auth import create_token
from src.common import time as study_time
from src.config.database import get_db
from src.modules.exam.models import AnswerRecord
from src.modules.exam.schemas import SubmitAnswerRequest
from src.modules.exam.service import submit_answer
from src.modules.question.models import Paper, Question
from src.modules.user import service
from src.modules.user.models import StreakRecord, User


@pytest.fixture
def api(client, db_session, monkeypatch):
    monkeypatch.setattr(service, "study_today", lambda: date(2026, 11, 1))
    db_session.add_all([User(openid="check-in-learner"), User(openid="check-in-other")])
    db_session.commit()

    def override_db():
        try:
            yield db_session
        except Exception:
            db_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_db
    try:
        yield client
    finally:
        app.dependency_overrides.clear()


def auth(openid="check-in-learner"):
    return {"Authorization": "Bearer " + create_token(openid)}


def test_check_in_rejects_guests_and_deleted_accounts(api, db_session):
    assert api.post("/api/v1/user/check-in").status_code == 401
    assert api.post("/api/v1/user/check-in", headers=auth("deleted")).status_code == 401
    assert db_session.query(User).count() == 2
    assert db_session.query(StreakRecord).count() == 0


def test_check_in_is_persistent_idempotent_and_does_not_fabricate_answers(api, db_session):
    before = api.get("/api/v1/user/dashboard", headers=auth()).json()["data"]
    assert before["check_in"]["streak_days"] == 0
    first = api.post("/api/v1/user/check-in", headers=auth())
    assert first.status_code == 200
    result = first.json()["data"]
    again = api.post("/api/v1/user/check-in", headers=auth()).json()["data"]
    assert result == again
    assert (result["today"], result["checked_in"], result["streak_days"]) == ("2026-11-01", True, 1)
    assert db_session.query(StreakRecord).one().question_count == 0
    assert db_session.query(AnswerRecord).count() == 0
    after = api.get("/api/v1/user/dashboard", headers=auth()).json()["data"]
    assert after["check_in"] == result
    assert after["today_stats"]["question_count"] == 0
    assert api.get("/api/v1/user/info", headers=auth()).json()["data"]["total_questions"] == 0


def test_week_is_monday_to_sunday_and_isolated_by_user(api, db_session, monkeypatch):
    learner = service.get_user_by_openid(db_session, "check-in-learner")
    other = service.get_user_by_openid(db_session, "check-in-other")
    for user_id, day in [(learner.id, 25), (learner.id, 26), (learner.id, 28), (other.id, 27)]:
        db_session.add(StreakRecord(user_id=user_id, streak_date=date(2026, 10, day), question_count=1))
    db_session.commit()
    state = api.post("/api/v1/user/check-in", headers=auth()).json()["data"]
    assert [day["date"] for day in state["week"]] == [
        "2026-10-26", "2026-10-27", "2026-10-28", "2026-10-29", "2026-10-30", "2026-10-31", "2026-11-01",
    ]
    assert [day["checked"] for day in state["week"]] == [True, False, True, False, False, False, True]
    other_state = api.get("/api/v1/user/dashboard", headers=auth("check-in-other")).json()["data"]["check_in"]
    assert other_state["checked_in"] is False
    assert [day["checked"] for day in other_state["week"]] == [False, True, False, False, False, False, False]

    monkeypatch.setattr(service, "study_today", lambda: date(2026, 11, 2))
    monday = api.post("/api/v1/user/check-in", headers=auth()).json()["data"]
    assert monday["streak_days"] == 2
    assert monday["week"][0] == {"date": "2026-11-02", "checked": True}
    assert [day["checked"] for day in monday["week"]] == [True, False, False, False, False, False, False]


def test_streak_continues_from_yesterday_and_resets_after_missing_a_day(api, monkeypatch):
    monkeypatch.setattr(service, "study_today", lambda: date(2026, 10, 31))
    assert api.post("/api/v1/user/check-in", headers=auth()).json()["data"]["streak_days"] == 1
    monkeypatch.setattr(service, "study_today", lambda: date(2026, 11, 1))
    before = api.get("/api/v1/user/dashboard", headers=auth()).json()["data"]["check_in"]
    assert before["streak_days"] == 1 and not before["checked_in"]
    assert api.post("/api/v1/user/check-in", headers=auth()).json()["data"]["streak_days"] == 2
    monkeypatch.setattr(service, "study_today", lambda: date(2026, 11, 3))
    assert api.get("/api/v1/user/dashboard", headers=auth()).json()["data"]["check_in"]["streak_days"] == 0
    assert api.get("/api/v1/user/info", headers=auth()).json()["data"]["streak_days"] == 0
    assert api.post("/api/v1/user/check-in", headers=auth()).json()["data"]["streak_days"] == 1


@pytest.mark.parametrize("check_in_first", [True, False])
def test_check_in_and_answering_share_one_day_without_losing_question_counts(api, db_session, check_in_first):
    user = service.get_user_by_openid(db_session, "check-in-learner")
    question = Question(exam_type="HKS", subject="reading", knowledge_point="reading", difficulty="easy",
                        question_type="single", stem_text="题目", options=[{"key": "A", "text": "答案"}], answer="A", is_active=1)
    db_session.add(question)
    db_session.flush()
    paper = Paper(user_id=user.id, title="check-in", exam_type="HKS", strategy="random",
                  question_ids=[question.id], total_score=1, mode="practice", difficulty="all")
    db_session.add(paper)
    db_session.commit()
    payload = SubmitAnswerRequest(paper_id=paper.id, question_id=question.id, user_answer="A")
    if check_in_first:
        assert api.post("/api/v1/user/check-in", headers=auth()).status_code == 200
    submit_answer(db_session, user.id, payload)
    assert api.post("/api/v1/user/check-in", headers=auth()).json()["data"]["streak_days"] == 1
    submit_answer(db_session, user.id, payload)
    assert db_session.query(StreakRecord).one().question_count == 1
    assert db_session.query(AnswerRecord).count() == 1
    db_session.refresh(user)
    assert user.total_questions == 1 and user.streak_days == 1


def test_check_in_changes_date_at_beijing_midnight(db_session, monkeypatch):
    instant = datetime(2026, 11, 1, 15, 59, 59, tzinfo=timezone.utc)

    class FixedClock(datetime):
        @classmethod
        def now(cls, tz=None):
            return instant.astimezone(tz)

    monkeypatch.setattr(study_time, "datetime", FixedClock)
    user = User(openid="beijing-midnight")
    db_session.add(user)
    db_session.commit()
    assert service.check_in(db_session, user.openid)["today"] == date(2026, 11, 1)
    instant = datetime(2026, 11, 1, 16, 0, 0, tzinfo=timezone.utc)
    state = service.check_in(db_session, user.openid)
    assert state["today"] == date(2026, 11, 2) and state["streak_days"] == 2
    assert db_session.query(StreakRecord).count() == 2
