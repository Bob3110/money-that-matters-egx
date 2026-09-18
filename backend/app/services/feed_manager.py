from datetime import datetime, timezone
from typing import Dict, Any, Optional
from app.services.storage import storage
from app.config import STALE_HOURS_THRESHOLD

FEED_NEWS = "news"
FEED_INSIDERS = "insiders"
FEED_INSTITUTIONAL = "institutional"
FEED_MACRO = "macro"

ALL_FEEDS = [FEED_NEWS, FEED_INSIDERS, FEED_INSTITUTIONAL, FEED_MACRO]

class FeedManager:
    """
    Tracks and enforces the 3 feed modes:
      - 'live': fetched successfully recently (<= 24h).
      - 'stale': succeeded before but not within 24h. Last-known-good real data keeps rendering,
                 clearly labeled, but excluded from score calculation.
      - 'empty': never synced. Honest 'waiting for first sync' state.
    
    CRITICAL RULE: A failed fetch must never overwrite good cached data.
    """
    async def record_sync_success(self, feed_name: str, count: int):
        now_iso = datetime.now(timezone.utc).isoformat()
        col = storage.get_collection("feed_metadata")
        await col.update_one(
            {"feed_name": feed_name},
            {
                "$set": {
                    "feed_name": feed_name,
                    "last_success_at": now_iso,
                    "last_attempt_at": now_iso,
                    "status": "live",
                    "item_count": count,
                    "last_error": None
                }
            },
            upsert=True
        )

    async def record_sync_failure(self, feed_name: str, error_msg: str):
        now_iso = datetime.now(timezone.utc).isoformat()
        col = storage.get_collection("feed_metadata")
        existing = await col.find_one({"feed_name": feed_name})
        if existing and existing.get("last_success_at"):
            await col.update_one(
                {"feed_name": feed_name},
                {
                    "$set": {
                        "last_attempt_at": now_iso,
                        "last_error": error_msg
                    }
                }
            )
        else:
            await col.update_one(
                {"feed_name": feed_name},
                {
                    "$set": {
                        "feed_name": feed_name,
                        "last_success_at": None,
                        "last_attempt_at": now_iso,
                        "status": "empty",
                        "item_count": 0,
                        "last_error": error_msg
                    }
                },
                upsert=True
            )

    async def get_feed_status(self, feed_name: str) -> Dict[str, Any]:
        col = storage.get_collection("feed_metadata")
        meta = await col.find_one({"feed_name": feed_name})
        if not meta or not meta.get("last_success_at"):
            return {
                "feed_name": feed_name,
                "mode": "empty",
                "last_success_at": None,
                "is_stale": False,
                "is_live": False,
                "item_count": meta.get("item_count", 0) if meta else 0,
                "last_error": meta.get("last_error") if meta else None
            }

        last_success_str = meta["last_success_at"]
        try:
            last_success_dt = datetime.fromisoformat(last_success_str)
            now = datetime.now(timezone.utc)
            delta = now - last_success_dt
            is_stale = delta.total_seconds() > (STALE_HOURS_THRESHOLD * 3600)
        except Exception:
            is_stale = False

        mode = "stale" if is_stale else "live"
        return {
            "feed_name": feed_name,
            "mode": mode,
            "last_success_at": last_success_str,
            "is_stale": is_stale,
            "is_live": not is_stale,
            "item_count": meta.get("item_count", 0),
            "last_error": meta.get("last_error")
        }

    async def get_all_feed_statuses(self) -> Dict[str, Dict[str, Any]]:
        statuses = {}
        for feed in ALL_FEEDS:
            statuses[feed] = await self.get_feed_status(feed)
        return statuses

feed_manager = FeedManager()
