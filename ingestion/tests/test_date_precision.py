from datetime import date
from ingestion.normalizers.date_precision import parse_date_and_precision


def test_date_precision_day():
    d, precision = parse_date_and_precision("2022-03-24")
    assert d == date(2022, 3, 24)
    assert precision == "day"


def test_date_precision_month():
    d, precision = parse_date_and_precision("2021-08")
    assert d == date(2021, 8, 1)
    assert precision == "month"


def test_date_precision_year():
    d, precision = parse_date_and_precision("1995")
    assert d == date(1995, 1, 1)
    assert precision == "year"


def test_date_precision_empty_or_invalid():
    assert parse_date_and_precision(None) == (None, None)
    assert parse_date_and_precision("") == (None, None)
    assert parse_date_and_precision("   ") == (None, None)
    assert parse_date_and_precision("invalid-date-string") == (None, None)

