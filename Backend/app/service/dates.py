from datetime import date, datetime, time


def day_bounds(day: date) -> tuple[datetime, datetime]:
    start = datetime.combine(day, time.min).astimezone()
    end = datetime.combine(day, time.max).astimezone()
    return start, end


def now_local() -> datetime:
    return datetime.now().astimezone()
