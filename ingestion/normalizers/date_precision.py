import re
from datetime import date
from typing import Optional

_DAY_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_MONTH_REGEX = re.compile(r"^\d{4}-\d{2}$")
_YEAR_REGEX = re.compile(r"^\d{4}$")


def parse_date_and_precision(raw_date: Optional[str]) -> tuple[Optional[date], Optional[str]]:
    """Parse date string into a calendar date object and its precision ('day', 'month', 'year')."""
    if not raw_date or not isinstance(raw_date, str):
        return None, None

    trimmed = raw_date.strip()
    if not trimmed:
        return None, None

    try:
        if _DAY_REGEX.match(trimmed):
            return date.fromisoformat(trimmed), "day"

        if _MONTH_REGEX.match(trimmed):
            parts = trimmed.split("-")
            year, month = int(parts[0]), int(parts[1])
            if 1 <= month <= 12:
                return date(year, month, 1), "month"

        if _YEAR_REGEX.match(trimmed):
            year = int(trimmed)
            return date(year, 1, 1), "year"
    except (ValueError, TypeError):
        pass

    return None, None

