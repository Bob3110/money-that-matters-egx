import pytest
from datetime import datetime, timezone
from app.utils.date_parser import parse_date_to_iso, parse_arabic_relative_time

def test_arabic_relative_times():
    now_year = str(datetime.now(timezone.utc).year)
    
    res_hours = parse_date_to_iso("منذ 3 ساعات")
    assert res_hours is not None
    assert now_year in res_hours

    res_two_hours = parse_date_to_iso("منذ ساعتين")
    assert res_two_hours is not None
    assert now_year in res_two_hours

    res_days = parse_date_to_iso("منذ 4 أيام")
    assert res_days is not None

    res_yesterday = parse_date_to_iso("أمس")
    assert res_yesterday is not None

    res_mins = parse_date_to_iso("منذ 25 دقيقة")
    assert res_mins is not None

def test_arabic_calendar_dates_with_ampm():
    # September 10 at 03:35 PM
    res_pm = parse_date_to_iso("10 سبتمبر 03:35 م")
    assert res_pm is not None
    assert "-09-10" in res_pm
    assert "15:35" in res_pm

    # March 12 at 09:20 AM
    res_am = parse_date_to_iso("12 مارس 09:20 ص")
    assert res_am is not None
    assert "-03-12" in res_am
    assert "09:20" in res_am

def test_arabic_indic_digits():
    res = parse_date_to_iso("١٠ سبتمبر ٠٣:٣٥ م")
    assert res is not None
    assert "-09-10" in res
    assert "15:35" in res

def test_empty_or_invalid_date_returns_none():
    assert parse_date_to_iso("") is None
    assert parse_date_to_iso(None) is None
    assert parse_date_to_iso("not a valid date string") is None
