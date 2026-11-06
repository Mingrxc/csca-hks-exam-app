from datetime import date, datetime, time, timedelta, timezone

STUDY_TIMEZONE = timezone(timedelta(hours=8))


def utc_now_naive() -> datetime:
    # 数据库的 DATETIME 字段按 UTC 保存，不携带时区信息。
    return datetime.now(timezone.utc).replace(tzinfo=None)


def study_today() -> date:
    return datetime.now(timezone.utc).astimezone(STUDY_TIMEZONE).date()


def study_day_utc_bounds(day: date | None = None) -> tuple[datetime, datetime]:
    # 先取北京时间的零点，再转换成数据库可比较的 UTC 边界。
    start = datetime.combine(day or study_today(), time.min, tzinfo=STUDY_TIMEZONE)
    return (start.astimezone(timezone.utc).replace(tzinfo=None),
            (start + timedelta(days=1)).astimezone(timezone.utc).replace(tzinfo=None))
