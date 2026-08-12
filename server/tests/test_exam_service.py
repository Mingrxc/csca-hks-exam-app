import pytest

from src.common.exceptions import AppException
from src.modules.exam.models import AnswerRecord
from src.modules.exam.schemas import SubmitAnswerRequest
from src.modules.exam.service import get_result, submit_answer
from src.modules.question.models import Paper, Question
from src.modules.user.models import User
from src.modules.wrongbook.models import KnowledgeStat, WrongBook


def make_question(stem: str, answer: str = "A") -> Question:
    return Question(
        exam_type="CSCA",
        subject="math",
        knowledge_point="sets",
        difficulty="easy",
        question_type="single",
        stem_text=stem,
        options=[
            {"key": "A", "text": "alpha"},
            {"key": "B", "text": "beta"},
        ],
        answer=answer,
        is_active=1,
    )


def test_submit_answer_rejects_question_outside_paper(db_session):
    user = User(openid="exam-submit-owner")
    included = make_question("included question")
    outside = make_question("outside question", answer="B")
    db_session.add_all([user, included, outside])
    db_session.commit()

    paper = Paper(
        user_id=user.id,
        title="membership check",
        exam_type="CSCA",
        strategy="random",
        question_ids=[included.id],
        total_score=1,
        mode="practice",
        difficulty="all",
    )
    db_session.add(paper)
    db_session.commit()

    payload = SubmitAnswerRequest(
        paper_id=paper.id,
        question_id=outside.id,
        user_answer="B",
    )

    with pytest.raises(AppException) as exc_info:
        submit_answer(db_session, user.id, payload)

    assert exc_info.value.status_code == 400
    assert exc_info.value.code == 40013
    assert db_session.query(AnswerRecord).count() == 0


def test_submit_answer_records_valid_paper_question(db_session):
    user = User(openid="exam-submit-valid")
    question = make_question("included valid question")
    db_session.add_all([user, question])
    db_session.commit()

    paper = Paper(
        user_id=user.id,
        title="valid submit",
        exam_type="CSCA",
        strategy="random",
        question_ids=[question.id],
        total_score=1,
        mode="practice",
        difficulty="all",
    )
    db_session.add(paper)
    db_session.commit()

    result = submit_answer(
        db_session,
        user.id,
        SubmitAnswerRequest(
            paper_id=paper.id,
            question_id=question.id,
            user_answer="A",
            time_spent=12,
        ),
    )

    assert result["recorded_new"] is True
    assert result["is_correct"] is True
    assert db_session.query(AnswerRecord).count() == 1


def test_submit_answer_is_idempotent_for_same_correctness(db_session):
    user = User(openid="exam-submit-idempotent")
    question = make_question("idempotent wrong question", answer="B")
    db_session.add_all([user, question])
    db_session.commit()

    paper = Paper(
        user_id=user.id,
        title="idempotent submit",
        exam_type="CSCA",
        strategy="random",
        question_ids=[question.id],
        total_score=1,
        mode="practice",
        difficulty="all",
    )
    db_session.add(paper)
    db_session.commit()

    payload = SubmitAnswerRequest(
        paper_id=paper.id,
        question_id=question.id,
        user_answer="A",
    )

    first = submit_answer(db_session, user.id, payload)
    second = submit_answer(db_session, user.id, payload)
    db_session.refresh(user)
    db_session.refresh(question)
    wrong_item = db_session.query(WrongBook).one()
    knowledge = db_session.query(KnowledgeStat).one()

    assert first["recorded_new"] is True
    assert second["recorded_new"] is False
    assert db_session.query(AnswerRecord).count() == 1
    assert user.total_questions == 1
    assert user.total_correct == 0
    assert question.wrong_count == 1
    assert question.correct_count == 0
    assert wrong_item.wrong_count == 1
    assert wrong_item.correct_count == 0
    assert knowledge.total_answered == 1
    assert knowledge.total_correct == 0


def test_submit_answer_adjusts_counters_when_answer_changes(db_session):
    user = User(openid="exam-submit-adjust")
    question = make_question("adjustable question", answer="B")
    db_session.add_all([user, question])
    db_session.commit()

    paper = Paper(
        user_id=user.id,
        title="adjust submit",
        exam_type="CSCA",
        strategy="random",
        question_ids=[question.id],
        total_score=1,
        mode="practice",
        difficulty="all",
    )
    db_session.add(paper)
    db_session.commit()

    submit_answer(
        db_session,
        user.id,
        SubmitAnswerRequest(paper_id=paper.id, question_id=question.id, user_answer="A"),
    )
    changed = submit_answer(
        db_session,
        user.id,
        SubmitAnswerRequest(paper_id=paper.id, question_id=question.id, user_answer="B"),
    )
    db_session.refresh(user)
    db_session.refresh(question)
    wrong_item = db_session.query(WrongBook).one()
    knowledge = db_session.query(KnowledgeStat).one()

    assert changed["recorded_new"] is False
    assert changed["is_correct"] is True
    assert user.total_questions == 1
    assert user.total_correct == 1
    assert question.wrong_count == 0
    assert question.correct_count == 1
    assert wrong_item.wrong_count == 1
    assert wrong_item.correct_count == 1
    assert wrong_item.is_mastered == 0
    assert knowledge.total_answered == 1
    assert knowledge.total_correct == 1
    assert knowledge.correct_rate == 100


def test_get_result_aggregates_records_and_unanswered_questions(db_session):
    user = User(openid="exam-result-user")
    correct_question = make_question("result correct question")
    unanswered_question = make_question("result unanswered question", answer="B")
    db_session.add_all([user, correct_question, unanswered_question])
    db_session.commit()

    paper = Paper(
        user_id=user.id,
        title="result aggregation",
        exam_type="CSCA",
        strategy="random",
        question_ids=[correct_question.id, unanswered_question.id],
        total_score=2,
        mode="exam",
        difficulty="all",
    )
    db_session.add(paper)
    db_session.commit()

    submit_answer(
        db_session,
        user.id,
        SubmitAnswerRequest(
            paper_id=paper.id,
            question_id=correct_question.id,
            user_answer="A",
            time_spent=8,
        ),
    )

    result = get_result(db_session, user.id, paper.id)

    assert result["total_count"] == 2
    assert result["correct_count"] == 1
    assert result["correct_rate"] == 50
    assert result["time_used"] == 8
    assert len(result["wrong_questions"]) == 1
    assert result["wrong_questions"][0]["id"] == unanswered_question.id
    assert paper.finished_at is not None
