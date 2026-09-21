import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from import_questions import load_questions  # noqa: E402


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_load_questions_maps_hsk_folder_to_hks(tmp_path):
    source = tmp_path / "original_question_bank"
    write_json(
        source / "HSK" / "1级" / "听力" / "questions.json",
        [
            {
                "exam_type": "HKS",
                "subject": "听力",
                "knowledge_point": "词汇识别",
                "difficulty": "easy",
                "question_type": "single",
                "stem_text": "你听到了什么？",
                "options": [
                    {"key": "A", "text": "学生"},
                    {"key": "B", "text": "老师"},
                ],
                "answer": "B",
            }
        ],
    )

    questions, report = load_questions(source)

    assert report.invalid == {}
    assert len(questions) == 1
    assert questions[0].exam_type == "HKS"
    assert questions[0].subject == "听力"


def test_load_questions_normalizes_raw_hsk4_quiz_and_skips_resources(tmp_path):
    source = tmp_path / "original_question_bank"
    write_json(
        source / "HSK" / "4级" / "raw_test_01.json",
        {
            "title": "HSK 4 SAMPLE QUIZ",
            "questions": [
                {
                    "number": 1,
                    "type": "listening_choice",
                    "audio": "https://example.test/audio.wav",
                    "options": ["A 学校", "B 医院"],
                    "correct_answer_index": 1,
                },
                {
                    "number": 2,
                    "type": "writing_construction",
                    "text": "完成句子：音乐 喜欢 流行 他 听",
                    "options": ["他喜欢听流行音乐。"],
                    "correct_answer_index": 0,
                },
            ],
        },
    )
    write_json(source / "HSK" / "4级" / "vocabulary.json", [{"word": "爱"}])

    questions, report = load_questions(source)

    assert report.invalid == {}
    assert report.skipped_resources == {"HSK/4级/vocabulary.json": 1}
    assert [question.question_type for question in questions] == ["single", "fill"]
    assert questions[0].options[0]["text"] == "学校"
    assert questions[0].answer == "B"
    assert questions[1].options == []
    assert questions[1].answer == "他喜欢听流行音乐。"
