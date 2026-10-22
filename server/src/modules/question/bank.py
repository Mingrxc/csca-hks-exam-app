"""Shared bank policy, media mapping and task semantics."""
from pathlib import Path, PurePosixPath
from urllib.parse import quote

from src.common.exceptions import AppException
from src.config.settings import settings

DEFERRED_MODES = {"oral", "oral_translation"}
SELF_REVIEW_MODES = {"written_response", "essay", "short_answer", "translation"}
LEVELS = ["1", "2", "3", "4", "5", "6", "7-9"]

# Timed practice profiles for the available non-oral bank; not official full papers.
PRACTICE_PROFILES = {
    "1": {"听力": 20, "阅读": 20},
    "2": {"听力": 20, "阅读": 20, "书写": 10},
    "3": {"听力": 18, "阅读": 20, "书写": 10},
    "4": {"听力": 18, "阅读": 20, "书写": 10},
    "5": {"听力": 20, "阅读": 20, "写作": 2},
    "6": {"听力": 20, "阅读": 20, "写作": 2},
    "7-9": {"听力": 20, "阅读": 20, "写作": 2, "翻译": 2},
}


def is_self_review(question):
    return question.response_mode in SELF_REVIEW_MODES or (
        question.question_type == "fill" and question.scoring_mode not in {"objective", "exact_or_handwriting_review"}
    )


def media_url(value):
    if not value:
        return None
    if value.startswith(("https://", "http://")):
        return value
    prefix = settings.QUESTION_MEDIA_BASE_URL.rstrip("/") or "/api/v1/question/media"
    return f"{prefix}/{quote(value, safe='/')}"


def media_path(relative):
    path = PurePosixPath(relative)
    allowed = {".wav", ".mp3", ".ogg", ".m4a", ".png", ".jpg", ".jpeg", ".webp"}
    root = Path(settings.QUESTION_BANK_ROOT).resolve()
    target = (root / path).resolve()
    if (path.is_absolute() or ".." in path.parts or "\\" in relative
            or path.parts[:2] != ("HSK", "_assets") or path.suffix.lower() not in allowed
            or not target.is_relative_to(root) or not target.is_file()):
        raise AppException(40403, "素材不存在", status_code=404)
    return target
