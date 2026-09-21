"""Request-scoped context shared by logging and API responses."""

from contextvars import ContextVar, Token
from re import fullmatch
from uuid import uuid4


REQUEST_ID_HEADER = "X-Request-ID"
_request_id: ContextVar[str] = ContextVar("request_id", default="")


def normalize_request_id(value: str | None) -> str:
    """Accept a short safe caller ID or generate a new opaque request ID."""
    candidate = (value or "").strip()
    if candidate and len(candidate) <= 64 and fullmatch(r"[A-Za-z0-9._-]+", candidate):
        return candidate
    return uuid4().hex


def set_request_id(value: str) -> Token[str]:
    return _request_id.set(value)


def reset_request_id(token: Token[str]) -> None:
    _request_id.reset(token)


def get_request_id() -> str:
    return _request_id.get()
