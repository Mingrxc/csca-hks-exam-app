from src.modules.exam.schemas import SubmitAnswerRequest
from src.modules.exam.service import submit_answer
from src.modules.question.models import Paper, Question
from src.modules.user.models import User
from src.modules.wrongbook.models import WrongBook
from src.modules.wrongbook.service import (
    generate_redo_paper,
    get_related,
    list_wrong_questions,
    mark_mastered,
)


def make_question(stem: str, knowledge_point: str = "sets", answer: str = "A") -> Question:
    return Question(
        exam_type="CSCA",
        subject="math",
        knowledge_point=knowledge_point,
        difficulty="easy",
        question_type="single",
        stem_text=stem,
        options=[
            {"key": "A", "text": "alpha"},
            {"key": "B", "text": "beta"},
        ],
        answer=answer,
        analysis="because alpha is correct",
        is_active=1,
    )


def make_paper(db_session, user_id: int, question_id: int, title: str) -> Paper:
    paper = Paper(
        user_id=user_id,
        title=title,
        exam_type="CSCA",
        strategy="random",
        question_ids=[question_id],
        total_score=1,
        mode="practice",
        difficulty="all",
    )
    db_session.add(paper)
    db_session.commit()
    return paper


def test_wrongbook_item_is_marked_mastered_after_three_later_correct_answers(db_session):
    user = User(openid="wrongbook-auto-master")
    question = make_question("auto mastered wrongbook question", answer="B")
    db_session.add_all([user, question])
    db_session.commit()

    wrong_paper = make_paper(db_session, user.id, question.id, "wrong attempt")
    submit_answer(
        db_session,
        user.id,
        SubmitAnswerRequest(paper_id=wrong_paper.id, question_id=question.id, user_answer="A"),
    )

    for index in range(3):
        paper = make_paper(db_session, user.id, question.id, f"correct review {index}")
        submit_answer(
            db_session,
            user.id,
            SubmitAnswerRequest(paper_id=paper.id, question_id=question.id, user_answer="B"),
        )

    item = db_session.query(WrongBook).one()
    assert item.wrong_count == 1
    assert item.correct_count == 3
    assert item.is_mastered == 1
    assert item.last_review_at is not None


def test_mark_mastered_toggles_current_user_wrongbook_item(db_session):
    user = User(openid="wrongbook-manual-master")
    question = make_question("manual mastered wrongbook question", answer="B")
    db_session.add_all([user, question])
    db_session.commit()

    wrong_paper = make_paper(db_session, user.id, question.id, "wrong attempt")
    submit_answer(
        db_session,
        user.id,
        SubmitAnswerRequest(paper_id=wrong_paper.id, question_id=question.id, user_answer="A"),
    )
    item = db_session.query(WrongBook).one()

    first = mark_mastered(db_session, user.id, item.id)
    second = mark_mastered(db_session, user.id, item.id)

    assert first["is_mastered"] is True
    assert second["is_mastered"] is False
    assert item.last_review_at is not None


def test_list_wrong_questions_filters_by_exam_knowledge_and_wrong_count(db_session):
    user = User(openid="wrongbook-list-filter")
    algebra = make_question("algebra wrong question", knowledge_point="algebra", answer="B")
    geometry = make_question("geometry wrong question", knowledge_point="geometry", answer="B")
    db_session.add_all([user, algebra, geometry])
    db_session.commit()

    for question in (algebra, geometry):
        paper = make_paper(db_session, user.id, question.id, f"wrong {question.knowledge_point}")
        submit_answer(
            db_session,
            user.id,
            SubmitAnswerRequest(paper_id=paper.id, question_id=question.id, user_answer="A"),
        )

    algebra_again = make_paper(db_session, user.id, algebra.id, "wrong algebra again")
    submit_answer(
        db_session,
        user.id,
        SubmitAnswerRequest(paper_id=algebra_again.id, question_id=algebra.id, user_answer="A"),
    )

    all_items = list_wrong_questions(db_session, user.id)
    algebra_items = list_wrong_questions(db_session, user.id, knowledge="algebra")
    repeated_items = list_wrong_questions(db_session, user.id, wrong_count="2+")

    assert len(all_items) == 2
    assert [item["knowledge_point"] for item in algebra_items] == ["algebra"]
    assert len(repeated_items) == 1
    assert repeated_items[0]["question_id"] == algebra.id


def test_get_related_returns_same_knowledge_point_without_solution(db_session):
    base = make_question("base related question", knowledge_point="sets")
    related = make_question("related same point", knowledge_point="sets")
    unrelated = make_question("unrelated point", knowledge_point="geometry")
    db_session.add_all([base, related, unrelated])
    db_session.commit()

    result = get_related(db_session, base.id, limit=5)

    assert len(result) == 1
    assert result[0]["id"] == related.id
    assert "answer" not in result[0]
    assert "analysis" not in result[0]


def test_generate_redo_paper_uses_unmastered_wrong_questions_for_exam_type(db_session):
    user = User(openid="wrongbook-redo-paper")
    csca_question = make_question("redo csca question", answer="B")
    hks_question = make_question("redo hks question", answer="B")
    hks_question.exam_type = "HKS"
    mastered_question = make_question("redo mastered question", answer="B")
    db_session.add_all([user, csca_question, hks_question, mastered_question])
    db_session.commit()

    for question in (csca_question, hks_question, mastered_question):
        paper = make_paper(db_session, user.id, question.id, f"wrong {question.stem_text}")
        submit_answer(
            db_session,
            user.id,
            SubmitAnswerRequest(paper_id=paper.id, question_id=question.id, user_answer="A"),
        )

    mastered_item = db_session.query(WrongBook).filter(WrongBook.question_id == mastered_question.id).one()
    mastered_item.is_mastered = 1
    db_session.commit()

    paper = generate_redo_paper(db_session, user.id, "CSCA", limit=10)

    assert paper["title"] == "CSCA 错题重做"
    assert paper["mode"] == "practice"
    assert paper["strategy"] == "knowledge"
    assert paper["question_ids"] == [csca_question.id]
    assert paper["questions"][0]["answer"] == "B"
