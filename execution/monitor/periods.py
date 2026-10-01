"""Inclusive finalized-data windows in Search Console's Pacific time zone."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def search_window(days: int, now: datetime | None = None) -> tuple[str, str]:
    if days < 1:
        raise ValueError('days must be positive')
    current = now or datetime.now(ZoneInfo('America/Los_Angeles'))
    end = current.astimezone(ZoneInfo('America/Los_Angeles')).date() - timedelta(days=3)
    start = end - timedelta(days=days - 1)
    return start.isoformat(), end.isoformat()
