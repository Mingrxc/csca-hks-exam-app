from datetime import date, datetime, timedelta

from src.modules.exam.models import AnswerRecord
from src.modules.exam.schemas import SubmitAnswerRequest
from src.modules.exam.service import get_result, submit_answer
from src.modules.question.models import Paper, Question
from src.modules.question.service import list_papers
from src.modules.user.models import StreakRecord, User
from src.modules.user.service import get_dashboard
from src.modules.wrongbook.models import WrongBook


def make_question(stem: str, answer: str = "A") -> Question:
    return Question(
        exam_type="CSCA",
        subject="math",
        knowledge_point="sets",
        difficulty="easy",
        question_type="single",
        stem_text=stem,
        options=[{"key": "A", "text": "alpha"}, {"key": "B", "text": "beta"}],
        answer=answer,
        is_active=1,
    )


def make_paper(user_id: int, question_ids: list[int], title: str = "history") -> Paper:
    return Paper(
        user_id=user_id,
        title=title,
        exam_type="CSCA",
        strategy="random",
        question_ids=question_ids,
        total_score=len(question_ids),
        mode="practice",
        difficulty="all",
    )


def test_history_only_returns_finished_papers_with_aggregates(db_session):
    user = User(openid="history-user")
    first = make_question("first")
    second = make_question("second", answer="B")
    db_session.add_all([user, first, second])
    db_session.commit()

    finished = make_paper(user.id, [first.id, second.id], "finished paper")
    finished.finished_at = datetime.now()
    unfinished = make_paper(user.id, [first.id], "unfinished paper")
    db_session.add_all([finished, unfinished])
    db_session.commit()
    db_session.add_all([
        AnswerRecord(
            user_id=user.id,
            paper_id=finished.id,
            question_id=first.id,
            user_answer="A",
            is_correct=1,
            time_spent=30,
        ),
        AnswerRecord(
            user_id=user.id,
            paper_id=finished.id,
            question_id=second.id,
            user_answer="A",
            is_correct=0,
            time_spent=45,
        ),
    ])
    db_session.commit()

    history = list_papers(db_session, user.id)

    assert len(history) == 1
    assert history[0]["id"] == finished.id
    assert history[0]["question_count"] == 2
    assert history[0]["correct_rate"] == 50
    assert history[0]["time_used"] == 75
    assert history[0]["passed"] is False


def test_dashboard_reports_today_pending_wrong_and_recent_papers(db_session):
    user = User(openid="dashboard-user", nickname="真实用户", target_exam="HKS")
    first = make_question("today correct")
    second = make_question("today wrong", answer="B")
    db_session.add_all([user, first, second])
    db_session.commit()
    paper = make_paper(user.id, [first.id, second.id], "recent paper")
    paper.finished_at = datetime.now()
    db_session.add(paper)
    db_session.commit()
    db_session.add_all([
        AnswerRecord(
            user_id=user.id,
            paper_id=paper.id,
            question_id=first.id,
            user_answer="A",
            is_correct=1,
            time_spent=10,
            created_at=datetime.now(),
        ),
        AnswerRecord(
            user_id=user.id,
            paper_id=paper.id,
            question_id=second.id,
            user_answer="A",
            is_correct=0,
            time_spent=15,
            created_at=datetime.now(),
        ),
        WrongBook(user_id=user.id, question_id=second.id, is_mastered=0),
    ])
    db_session.commit()

    dashboard = get_dashboard(db_session, user)

    assert dashboard["user_name"] == "真实用户"
    assert dashboard["target_exam"] == "HKS"
    assert dashboard["today_stats"] == {
        "question_count": 2,
        "correct_rate": 50,
        "wrong_count": 1,
    }
    assert dashboard["pending_wrong_count"] == 1
    assert dashboard["recent_papers"][0]["id"] == paper.id


def test_new_answers_update_daily_streak_once_per_question(db_session):
    user = User(
        openid="streak-user",
        streak_days=4,
        last_streak_at=date.today() - timedelta(days=1),
    )
    question = make_question("streak question")
    db_session.add_all([user, question])
    db_session.commit()
    paper = make_paper(user.id, [question.id])
    db_session.add(paper)
    db_session.commit()

    payload = SubmitAnswerRequest(
        paper_id=paper.id,
        question_id=question.id,
        user_answer="A",
    )
    submit_answer(db_session, user.id, payload)
    submit_answer(db_session, user.id, payload)
    db_session.refresh(user)
    streak = db_session.query(StreakRecord).one()

    assert user.streak_days == 5
    assert user.last_streak_at == date.today()
    assert streak.streak_date == date.today()
    assert streak.question_count == 1


def test_reopening_result_keeps_original_finished_time(db_session):
    user = User(openid="stable-finished-at")
    question = make_question("stable finish")
    db_session.add_all([user, question])
    db_session.commit()
    paper = make_paper(user.id, [question.id])
    paper.finished_at = datetime.now() - timedelta(days=2)
    original_finished_at = paper.finished_at
    db_session.add(paper)
    db_session.commit()

    get_result(db_session, user.id, paper.id)

    assert paper.finished_at == original_finished_at
