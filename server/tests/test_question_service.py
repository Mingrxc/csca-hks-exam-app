from src.modules.question.models import Question
from src.modules.question.schemas import GeneratePaperRequest
from src.modules.question import service
from src.modules.question.service import generate_paper
from src.modules.user.models import User


def make_question(stem: str, answer: str = "A", difficulty: str = "easy") -> Question:
    return Question(
        exam_type="CSCA",
        subject="math",
        knowledge_point="sets",
        difficulty=difficulty,
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


def test_generate_random_paper_preserves_sample_order(db_session, monkeypatch):
    user = User(openid="paper-sample-order")
    questions = [make_question(f"question {index}") for index in range(3)]
    db_session.add_all([user, *questions])
    db_session.commit()

    monkeypatch.setattr(
        service.random,
        "sample",
        lambda candidate_ids, count: [candidate_ids[-1], candidate_ids[0]],
    )
    paper = generate_paper(
        db_session,
        user.id,
        GeneratePaperRequest(exam_type="CSCA", question_count=2, strategy="random"),
    )

    assert paper["question_ids"] == [questions[-1].id, questions[0].id]


def test_generate_progressive_paper_orders_sample_by_difficulty(db_session, monkeypatch):
    user = User(openid="paper-progressive-order")
    hard = make_question("hard question", difficulty="hard")
    easy = make_question("easy question", difficulty="easy")
    medium = make_question("medium question", difficulty="medium")
    db_session.add_all([user, hard, easy, medium])
    db_session.commit()

    monkeypatch.setattr(
        service.random,
        "sample",
        lambda candidate_ids, count: list(reversed(candidate_ids)),
    )
    paper = generate_paper(
        db_session,
        user.id,
        GeneratePaperRequest(exam_type="CSCA", question_count=3, strategy="progressive"),
    )

    assert [question["difficulty"] for question in paper["questions"]] == [
        "easy",
        "medium",
        "hard",
    ]


def test_generate_hks_paper_filters_by_top_level_subject(db_session):
    user = User(openid="paper-hks-subject-user")
    listening = Question(
        exam_type="HKS",
        subject="听力",
        knowledge_point="听力选择",
        difficulty="medium",
        question_type="single",
        stem_text="listening question",
        options=[{"key": "A", "text": "alpha"}],
        answer="A",
        analysis="because alpha is correct",
        is_active=1,
    )
    reading = Question(
        exam_type="HKS",
        subject="阅读",
        knowledge_point="阅读理解",
        difficulty="medium",
        question_type="single",
        stem_text="reading question",
        options=[{"key": "A", "text": "alpha"}],
        answer="A",
        analysis="because alpha is correct",
        is_active=1,
    )
    db_session.add_all([user, listening, reading])
    db_session.commit()

    paper = generate_paper(
        db_session,
        user.id,
        GeneratePaperRequest(
            exam_type="HKS",
            question_count=1,
            strategy="knowledge",
            knowledge_points=["听力"],
        ),
    )

    assert [question["stem_text"] for question in paper["questions"]] == ["listening question"]


def test_generate_hks_real_paper_covers_all_subjects(db_session):
    user = User(openid="paper-hks-real-user")
    listening = Question(
        exam_type="HKS",
        subject="听力",
        knowledge_point="听力选择",
        difficulty="easy",
        question_type="single",
        stem_text="listening question",
        options=[{"key": "A", "text": "alpha"}],
        answer="A",
        analysis="because alpha is correct",
        is_active=1,
    )
    reading = Question(
        exam_type="HKS",
        subject="阅读",
        knowledge_point="阅读理解",
        difficulty="hard",
        question_type="single",
        stem_text="reading question",
        options=[{"key": "A", "text": "alpha"}],
        answer="A",
        analysis="because alpha is correct",
        is_active=1,
    )
    db_session.add_all([user, listening, reading])
    db_session.commit()

    paper = generate_paper(
        db_session,
        user.id,
        GeneratePaperRequest(
            exam_type="HKS",
            question_count=1,
            strategy="real",
            knowledge_points=["听力"],
            mode="exam",
        ),
    )

    assert {question["subject"] for question in paper["questions"]} == {"听力", "阅读"}
    assert set(paper["question_ids"]) == {listening.id, reading.id}
