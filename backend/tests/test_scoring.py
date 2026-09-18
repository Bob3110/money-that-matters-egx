import pytest
from app.services.scoring import compute_money_match_score

def test_single_source_cap_at_33():
    res = compute_money_match_score(
        news_lean=1, insider_lean=0, inst_lean=0,
        news_stale=False, insider_stale=False, inst_stale=False
    )
    assert res["score"] == 33
    assert res["direction"] == "bullish"
    assert res["strong_match"] is False
    assert res["coverage_cap"] == 33

def test_two_sources_agreeing_cap_at_67():
    res = compute_money_match_score(
        news_lean=1, insider_lean=1, inst_lean=0,
        news_stale=False, insider_stale=False, inst_stale=False
    )
    assert res["score"] == 67
    assert res["direction"] == "bullish"
    assert res["strong_match"] is False
    assert res["coverage_cap"] == 67

def test_two_sources_conflicting_penalized_to_zero():
    res = compute_money_match_score(
        news_lean=1, insider_lean=-1, inst_lean=0,
        news_stale=False, insider_stale=False, inst_stale=False
    )
    assert res["score"] == 0
    assert res["direction"] == "neutral"

def test_three_sources_all_agreeing_reaches_100_and_strong_match():
    res = compute_money_match_score(
        news_lean=1, insider_lean=1, inst_lean=1,
        news_stale=False, insider_stale=False, inst_stale=False
    )
    assert res["score"] == 100
    assert res["direction"] == "bullish"
    assert res["strong_match"] is True
    assert res["coverage_cap"] == 100

def test_stale_feed_excluded_from_score():
    res = compute_money_match_score(
        news_lean=1, insider_lean=1, inst_lean=0,
        news_stale=True, insider_stale=False, inst_stale=False
    )
    assert res["score"] == 33
    assert res["active_sources_count"] == 1
    assert res["strong_match"] is False
