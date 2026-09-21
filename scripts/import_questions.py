"""Validate and import the sibling original_question_bank into questions.

Default mode is a dry run:
    server/.venv/Scripts/python.exe scripts/import_questions.py

Write to the configured database explicitly:
    server/.venv/Scripts/python.exe scripts/import_questions.py --apply
"""

from __future__ import annotations

import argparse
import os
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PROJECT_ROOT.parent
DEFAULT_SOURCE = WORKSPACE_ROOT / "original_question_bank"
SERVER_ROOT = PROJECT_ROOT / "server"

EXAM_TYPE_MAP = {
    "CSCA": "CSCA",
    "HKS": "HKS",
    "HSK": "HKS",
}

DIFFICULTY_MAP = {
    "easy": "easy",
    "medium": "medium",
    "hard": "hard",
}

QUESTION_TYPE_MAP = {
    "single": "single",
    "multi": "multi",
    "judge": "judge",
    "fill": "fill",
    "listening_true_false": "judge",
    "listening_choice": "single",
    "reading_comprehension": "single",
    "reading_ordering": "single",
    "fill_in_blank": "single",
    "writing_construction": "fill",
}

RAW_KNOWLEDGE_POINTS = {
    "listening_true_false": "听力判断",
    "listening_choice": "听力选择",
    "reading_comprehension": "阅读理解",
    "reading_ordering": "语序排列",
    "fill_in_blank": "选词填空",
    "writing_construction": "完成句子",
}

RAW_SUBJECTS = {
    "listening_true_false": "听力",
    "listening_choice": "听力",
    "reading_comprehension": "阅读",
    "reading_ordering": "阅读",
    "fill_in_blank": "阅读",
    "writing_construction": "书写",
}

OPTION_PREFIX_RE = re.compile(r"^[A-Z][.、\s]+")


@dataclass(frozen=True)
class ImportQuestion:
    exam_type: str
    subject: str
    knowledge_point: str
    difficulty: str
    question_type: str
    stem_text: str
    options: list[dict[str, str]]
    answer: str
    analysis: str | None = None
    stem_image: str | None = None
    stem_audio: str | None = None
    wrong_options_analysis: Any | None = None

    @property
    def natural_key(self) -> tuple[str, str, str, str, str, str]:
        return (
            self.exam_type,
            self.subject,
            self.knowledge_point,
            self.question_type,
            self.stem_text,
            self.answer,
        )


@dataclass
class ImportReport:
    parsed: int = 0
    duplicate_in_source: int = 0
    invalid: Counter[str] | None = None
    skipped_resources: Counter[str] | None = None

    def __post_init__(self) -> None:
        self.invalid = self.invalid or Counter()
        self.skipped_resources = self.skipped_resources or Counter()


def main() -> int:
    parser = argparse.ArgumentParser(description="Import CSCA/HKS question-bank JSON files.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Path to original_question_bank.")
    parser.add_argument("--apply", action="store_true", help="Write inserts/updates to the configured database.")
    parser.add_argument("--verify-db", action="store_true", help="Read database question counts without importing.")
    args = parser.parse_args()

    if args.verify_db:
        try:
            print_database_stats()
        except Exception as exc:
            print(f"Database verification failed: {exc.__class__.__name__}: {exc}", file=sys.stderr)
            return 1
        return 0

    questions, report = load_questions(args.source)
    print_report(args.source, questions, report)

    if not args.apply:
        print("Dry run only. Re-run with --apply to write to the database.")
        return 0

    try:
        inserted, updated = upsert_questions(questions)
    except Exception as exc:
        print(f"Database import failed: {exc.__class__.__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"Database import complete: inserted={inserted}, updated={updated}.")
    return 0


def load_questions(source: Path) -> tuple[list[ImportQuestion], ImportReport]:
    if not source.exists():
        raise SystemExit(f"Question-bank source does not exist: {source}")

    report = ImportReport()
    by_key: dict[tuple[str, str, str, str, str, str], ImportQuestion] = {}

    for path in sorted(source.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            report.invalid["invalid_json"] += 1
            continue

        for record in normalize_file(source, path, data, report):
            key = record.natural_key
            if key in by_key:
                report.duplicate_in_source += 1
                continue
            by_key[key] = record

    report.parsed = len(by_key)
    return list(by_key.values()), report


def normalize_file(source: Path, path: Path, data: Any, report: ImportReport) -> Iterable[ImportQuestion]:
    if is_canonical_question_list(data):
        for item in data:
            normalized = normalize_canonical_question(item, source, path, report)
            if normalized:
                yield normalized
        return

    if isinstance(data, dict) and isinstance(data.get("questions"), list):
        for item in data["questions"]:
            normalized = normalize_raw_hsk4_question(item, data, source, path, report)
            if normalized:
                yield normalized
        return

    report.skipped_resources[path.relative_to(source).as_posix()] += count_resource_records(data)


def is_canonical_question_list(data: Any) -> bool:
    return (
        isinstance(data, list)
        and bool(data)
        and isinstance(data[0], dict)
        and {"stem_text", "options", "answer"}.issubset(data[0])
    )


def normalize_canonical_question(
    item: dict[str, Any],
    source: Path,
    path: Path,
    report: ImportReport,
) -> ImportQuestion | None:
    try:
        exam_type = normalize_exam_type(item.get("exam_type") or infer_exam_type(source, path))
        question_type = normalize_question_type(item.get("question_type"))
        difficulty = normalize_difficulty(item.get("difficulty"))
        subject = required_text(item.get("subject") or infer_subject(source, path), "subject")
        knowledge_point = required_text(item.get("knowledge_point") or subject, "knowledge_point")
        stem_text = required_text(item.get("stem_text"), "stem_text")
        answer = required_text(item.get("answer"), "answer")
        options = normalize_options(item.get("options"), allow_empty=question_type == "fill")
    except ValueError as exc:
        report.invalid[str(exc)] += 1
        return None

    return ImportQuestion(
        exam_type=exam_type,
        subject=subject,
        knowledge_point=knowledge_point,
        difficulty=difficulty,
        question_type=question_type,
        stem_text=stem_text,
        stem_image=optional_text(item.get("stem_image")),
        stem_audio=optional_text(item.get("stem_audio")),
        options=options,
        answer=answer,
        analysis=optional_text(item.get("analysis")),
        wrong_options_analysis=item.get("wrong_options_analysis"),
    )


def normalize_raw_hsk4_question(
    item: dict[str, Any],
    parent: dict[str, Any],
    source: Path,
    path: Path,
    report: ImportReport,
) -> ImportQuestion | None:
    raw_type = item.get("type")
    try:
        question_type = normalize_question_type(raw_type)
        raw_options = item.get("options") or []
        correct_index = item.get("correct_answer_index")
        options = normalize_options(raw_options, allow_empty=question_type == "fill")
        answer = answer_from_index(options, raw_options, correct_index, question_type)
        stem_text = optional_text(item.get("text")) or default_raw_stem(raw_type, item)
    except ValueError as exc:
        report.invalid[str(exc)] += 1
        return None

    title = optional_text(parent.get("title")) or path.stem
    number = item.get("number", "?")
    source_id = item.get("original_id")
    source_note = f"{title} #{number}"
    if source_id is not None:
        source_note = f"{source_note}; original_id={source_id}"

    analysis = optional_text(item.get("explanation"))
    if analysis:
        analysis = f"{analysis}\n\nSource: {source_note}"
    else:
        analysis = f"Source: {source_note}"

    return ImportQuestion(
        exam_type="HKS",
        subject=RAW_SUBJECTS.get(str(raw_type), infer_subject(source, path)),
        knowledge_point=RAW_KNOWLEDGE_POINTS.get(str(raw_type), str(raw_type)),
        difficulty="medium",
        question_type=question_type,
        stem_text=stem_text,
        stem_image=optional_text(item.get("image")),
        stem_audio=optional_text(item.get("audio")),
        options=[] if question_type == "fill" else options,
        answer=answer,
        analysis=analysis,
    )


def normalize_exam_type(value: Any) -> str:
    normalized = EXAM_TYPE_MAP.get(str(value).upper())
    if not normalized:
        raise ValueError("unknown_exam_type")
    return normalized


def normalize_question_type(value: Any) -> str:
    normalized = QUESTION_TYPE_MAP.get(str(value))
    if not normalized:
        raise ValueError("unknown_question_type")
    return normalized


def normalize_difficulty(value: Any) -> str:
    normalized = DIFFICULTY_MAP.get(str(value))
    if not normalized:
        raise ValueError("unknown_difficulty")
    return normalized


def normalize_options(value: Any, allow_empty: bool = False) -> list[dict[str, str]]:
    if value in (None, []) and allow_empty:
        return []
    if not isinstance(value, list) or not value:
        raise ValueError("invalid_options")

    options: list[dict[str, str]] = []
    for index, option in enumerate(value):
        default_key = chr(ord("A") + index)
        if isinstance(option, dict):
            option_key = optional_text(option.get("key")) or default_key
            option_text = optional_text(option.get("text"))
        else:
            option_key = default_key
            option_text = optional_text(option)
            if option_text:
                option_text = OPTION_PREFIX_RE.sub("", option_text).strip()
        if not option_text:
            if allow_empty:
                continue
            raise ValueError("missing_option_text")
        options.append({"key": option_key.upper(), "text": option_text})
    if not options and not allow_empty:
        raise ValueError("invalid_options")
    return options


def answer_from_index(
    options: list[dict[str, str]],
    raw_options: list[Any],
    correct_index: Any,
    question_type: str,
) -> str:
    if not isinstance(correct_index, int) or correct_index < 0:
        raise ValueError("invalid_correct_answer_index")
    if correct_index >= len(raw_options):
        raise ValueError("invalid_correct_answer_index")
    if question_type == "fill":
        raw_answer = raw_options[correct_index]
        if isinstance(raw_answer, dict):
            return required_text(raw_answer.get("text"), "answer")
        return OPTION_PREFIX_RE.sub("", required_text(raw_answer, "answer")).strip()
    if correct_index >= len(options):
        raise ValueError("invalid_correct_answer_index")
    return options[correct_index]["key"]


def required_text(value: Any, field: str) -> str:
    text = optional_text(value)
    if not text:
        raise ValueError(f"missing_{field}")
    return text


def optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def infer_exam_type(source: Path, path: Path) -> str:
    parts = path.relative_to(source).parts
    return normalize_exam_type(parts[0])


def infer_subject(source: Path, path: Path) -> str:
    parts = path.relative_to(source).parts
    if len(parts) >= 3 and parts[0] == "HSK":
        return parts[-2]
    if len(parts) >= 2:
        return parts[1]
    return "General"


def default_raw_stem(raw_type: Any, item: dict[str, Any]) -> str:
    label = RAW_KNOWLEDGE_POINTS.get(str(raw_type), str(raw_type))
    number = item.get("number", "?")
    return f"{label} #{number}: choose the correct answer."


def count_resource_records(data: Any) -> int:
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict) and isinstance(data.get("questions"), list):
        return len(data["questions"])
    return 1


def upsert_questions(questions: list[ImportQuestion]) -> tuple[int, int]:
    sys.path.insert(0, str(SERVER_ROOT))
    original_cwd = Path.cwd()
    os.chdir(SERVER_ROOT)

    try:
        from src.config.database import SessionLocal
        from src.modules.question.models import Question

        inserted = 0
        updated = 0
        with SessionLocal() as db:
            for item in questions:
                existing = (
                    db.query(Question)
                    .filter(
                        Question.exam_type == item.exam_type,
                        Question.subject == item.subject,
                        Question.knowledge_point == item.knowledge_point,
                        Question.question_type == item.question_type,
                        Question.stem_text == item.stem_text,
                        Question.answer == item.answer,
                    )
                    .first()
                )
                values = {
                    "exam_type": item.exam_type,
                    "subject": item.subject,
                    "knowledge_point": item.knowledge_point,
                    "difficulty": item.difficulty,
                    "question_type": item.question_type,
                    "stem_text": item.stem_text,
                    "stem_image": item.stem_image,
                    "stem_audio": item.stem_audio,
                    "options": item.options,
                    "answer": item.answer,
                    "analysis": item.analysis,
                    "wrong_options_analysis": item.wrong_options_analysis,
                    "is_active": 1,
                }
                if existing:
                    for key, value in values.items():
                        setattr(existing, key, value)
                    updated += 1
                else:
                    db.add(Question(**values))
                    inserted += 1
            db.commit()
        return inserted, updated
    finally:
        os.chdir(original_cwd)


def print_database_stats() -> None:
    sys.path.insert(0, str(SERVER_ROOT))
    original_cwd = Path.cwd()
    os.chdir(SERVER_ROOT)

    try:
        from sqlalchemy import func

        from src.config.database import SessionLocal
        from src.modules.question.models import Question

        with SessionLocal() as db:
            total = db.query(func.count(Question.id)).scalar() or 0
            print(f"Database questions: {total}")
            print("Exam counts:")
            for exam_type, count in db.query(Question.exam_type, func.count(Question.id)).group_by(Question.exam_type):
                print(f"  {exam_type}: {count}")
            print("Difficulty counts:")
            for difficulty, count in db.query(Question.difficulty, func.count(Question.id)).group_by(Question.difficulty):
                print(f"  {difficulty}: {count}")
            print("Question type counts:")
            for question_type, count in db.query(Question.question_type, func.count(Question.id)).group_by(Question.question_type):
                print(f"  {question_type}: {count}")
            print("Subject counts:")
            rows = (
                db.query(Question.exam_type, Question.subject, func.count(Question.id))
                .group_by(Question.exam_type, Question.subject)
                .order_by(Question.exam_type, Question.subject)
                .all()
            )
            for exam_type, subject, count in rows:
                print(f"  {exam_type}/{subject}: {count}")
    finally:
        os.chdir(original_cwd)


def print_report(source: Path, questions: list[ImportQuestion], report: ImportReport) -> None:
    by_exam = Counter(question.exam_type for question in questions)
    by_subject = Counter((question.exam_type, question.subject) for question in questions)
    by_difficulty = Counter(question.difficulty for question in questions)
    by_type = Counter(question.question_type for question in questions)

    print(f"Source: {source}")
    print(f"Importable questions: {len(questions)}")
    print(f"Source duplicates skipped: {report.duplicate_in_source}")
    print(f"Exam counts: {dict(sorted(by_exam.items()))}")
    print(f"Difficulty counts: {dict(sorted(by_difficulty.items()))}")
    print(f"Question type counts: {dict(sorted(by_type.items()))}")
    print("Subject counts:")
    for (exam_type, subject), count in sorted(by_subject.items()):
        print(f"  {exam_type}/{subject}: {count}")
    if report.skipped_resources:
        print("Skipped non-question resources:")
        for resource, count in sorted(report.skipped_resources.items()):
            print(f"  {resource}: {count}")
    if report.invalid:
        print("Invalid records:")
        for reason, count in sorted(report.invalid.items()):
            print(f"  {reason}: {count}")


if __name__ == "__main__":
    raise SystemExit(main())
