import pytest
from datetime import datetime, timezone, timedelta
from app.services.feed_manager import feed_manager, FEED_NEWS, FEED_INSIDERS
from app.services.storage import storage
from app.services.scoring import compute_money_match_score

@pytest.mark.asyncio
async def test_feed_modes_transitions():
    await storage.initialize()
    
    # 1. Unsynced feed -> 'empty'
    status_empty = await feed_manager.get_feed_status("test_feed_empty")
    assert status_empty["mode"] == "empty"
    assert status_empty["is_live"] is False
    assert status_empty["is_stale"] is False

    # 2. Record sync success -> 'live'
    await feed_manager.record_sync_success("test_feed_live", count=15)
    status_live = await feed_manager.get_feed_status("test_feed_live")
    assert status_live["mode"] == "live"
    assert status_live["is_live"] is True
    assert status_live["is_stale"] is False
    assert status_live["item_count"] == 15

    # 3. Simulate >24h old success -> 'stale'
    old_time = (datetime.now(timezone.utc) - timedelta(hours=26)).isoformat()
    meta_col = storage.get_collection("feed_metadata")
    await meta_col.update_one(
        {"feed_name": "test_feed_stale"},
        {
            "$set": {
                "feed_name": "test_feed_stale",
                "last_success_at": old_time,
                "status": "live",
                "item_count": 8
            }
        },
        upsert=True
    )
    status_stale = await feed_manager.get_feed_status("test_feed_stale")
    assert status_stale["mode"] == "stale"
    assert status_stale["is_stale"] is True
    assert status_stale["is_live"] is False

@pytest.mark.asyncio
async def test_failed_fetch_preserves_good_cached_records():
    await storage.initialize()
    news_col = storage.get_collection("news")
    
    # Insert a real test record
    test_record = {
        "url": "https://enterprise.news/story/real-cib-quarterly-earnings",
        "headline": "CIB reports strong quarterly earnings on EGX",
        "ticker": "COMI.CA",
        "outlet": "Enterprise Egypt",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "lean": 1
    }
    await news_col.update_one({"url": test_record["url"]}, {"$set": test_record}, upsert=True)
    await feed_manager.record_sync_success(FEED_NEWS, count=1)

    initial_count = await news_col.count_documents({"url": test_record["url"]})
    assert initial_count == 1

    # Record fetch failure
    await feed_manager.record_sync_failure(FEED_NEWS, "Connection timed out")

    # Verify cached record was NOT wiped out
    preserved_count = await news_col.count_documents({"url": test_record["url"]})
    assert preserved_count == 1

    # Status maintains last_success_at
    status = await feed_manager.get_feed_status(FEED_NEWS)
    assert status["last_success_at"] is not None
    assert status["last_error"] == "Connection timed out"

def test_stale_feed_vote_excluded_from_money_match():
    # If news and insiders are bullish, but news is stale:
    # Only 1 active source counts (insiders), so score caps at 33 instead of 67.
    score_active = compute_money_match_score(
        news_lean=1, insider_lean=1, inst_lean=0,
        news_stale=False, insider_stale=False, inst_stale=False
    )
    assert score_active["score"] == 67
    assert score_active["active_sources_count"] == 2

    score_with_stale = compute_money_match_score(
        news_lean=1, insider_lean=1, inst_lean=0,
        news_stale=True, insider_stale=False, inst_stale=False
    )
    assert score_with_stale["score"] == 33
    assert score_with_stale["active_sources_count"] == 1
    assert score_with_stale["signals_breakdown"]["news"]["stale"] is True
