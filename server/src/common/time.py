"""Time helpers for MySQL DATETIME columns."""

from datetime import date, datetime, time, timedelta, timezone

STUDY_TIMEZONE = timezone(timedelta(hours=8))


def utc_now_naive() -> datetime:
    """Return explicit UTC with tzinfo removed for timezone-naive DB columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def study_today() -> date:
    return datetime.now(timezone.utc).astimezone(STUDY_TIMEZONE).date()


def study_day_utc_bounds(day: date | None = None) -> tuple[datetime, datetime]:
    """Compare UTC-naive answers within a Beijing study day."""
    start = datetime.combine(day or study_today(), time.min, tzinfo=STUDY_TIMEZONE)
    return (start.astimezone(timezone.utc).replace(tzinfo=None),
            (start + timedelta(days=1)).astimezone(timezone.utc).replace(tzinfo=None))
