"""Time helpers for MySQL DATETIME columns."""

from datetime import datetime, timezone


def utc_now_naive() -> datetime:
    """Return explicit UTC with tzinfo removed for timezone-naive DB columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
