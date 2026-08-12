from src.modules.question.models import Question
from src.modules.question.schemas import GeneratePaperRequest
from src.modules.question.service import generate_paper
from src.modules.user.models import User


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
        analysis="because alpha is correct",
        is_active=1,
    )


def test_generate_exam_paper_hides_solution_fields(db_session):
    user = User(openid="paper-exam-user")
    db_session.add_all([user, make_question("exam question")])
    db_session.commit()

    paper = generate_paper(
        db_session,
        user.id,
        GeneratePaperRequest(
            exam_type="CSCA",
            question_count=1,
            mode="exam",
        ),
    )

    question = paper["questions"][0]
    assert "answer" not in question
    assert "analysis" not in question


def test_generate_practice_paper_includes_solution_fields(db_session):
    user = User(openid="paper-practice-user")
    db_session.add_all([user, make_question("practice question")])
    db_session.commit()

    paper = generate_paper(
        db_session,
        user.id,
        GeneratePaperRequest(
            exam_type="CSCA",
            question_count=1,
            mode="practice",
        ),
    )

    question = paper["questions"][0]
    assert question["answer"] == "A"
    assert question["analysis"] == "because alpha is correct"
