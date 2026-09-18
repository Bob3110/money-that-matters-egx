from typing import List, Dict, Any, Optional
from app.config import SEED_UNIVERSE
from app.services.storage import storage
from app.services.feed_manager import (
    feed_manager, FEED_NEWS, FEED_INSIDERS, FEED_INSTITUTIONAL
)

def compute_money_match_score(news_lean: int, insider_lean: int, inst_lean: int,
                              news_stale: bool, insider_stale: bool, inst_stale: bool) -> Dict[str, Any]:
    signals = []
    active_sources = 0

    if not news_stale and news_lean != 0:
        signals.append(news_lean)
        active_sources += 1

    if not insider_stale and insider_lean != 0:
        signals.append(insider_lean)
        active_sources += 1

    if not inst_stale and inst_lean != 0:
        signals.append(inst_lean)
        active_sources += 1

    if not signals:
        return {
            "score": 0,
            "direction": "neutral",
            "active_sources_count": active_sources,
            "strong_match": False,
            "coverage_cap": 0,
            "signals_breakdown": {
                "news": {"lean": news_lean, "stale": news_stale},
                "insiders": {"lean": insider_lean, "stale": insider_stale},
                "institutional": {"lean": inst_lean, "stale": inst_stale}
            }
        }

    positive_votes = sum(1 for s in signals if s > 0)
    negative_votes = sum(1 for s in signals if s < 0)
    net_lean = positive_votes - negative_votes
    total_votes = len(signals)

    direction = "bullish" if net_lean > 0 else ("bearish" if net_lean < 0 else "neutral")

    if total_votes == 1:
        coverage_cap = 33
        raw_score = 33 if net_lean != 0 else 0
    elif total_votes == 2:
        coverage_cap = 67
        if positive_votes == 2 or negative_votes == 2:
            raw_score = 67
        else:
            raw_score = 0
    else:
        coverage_cap = 100
        if positive_votes == 3 or negative_votes == 3:
            raw_score = 100
        elif positive_votes == 2 or negative_votes == 2:
            raw_score = 45
        else:
            raw_score = 0

    score = min(raw_score, coverage_cap)
    strong_match = (score >= 60 and total_votes == 3 and (positive_votes == 3 or negative_votes == 3))

    return {
        "score": score,
        "direction": direction,
        "active_sources_count": total_votes,
        "strong_match": strong_match,
        "coverage_cap": coverage_cap,
        "signals_breakdown": {
            "news": {"lean": news_lean, "stale": news_stale},
            "insiders": {"lean": insider_lean, "stale": insider_stale},
            "institutional": {"lean": inst_lean, "stale": inst_stale}
        }
    }

class ScoringService:
    async def get_tracked_universe(self) -> Dict[str, Any]:
        universe_col = storage.get_collection("tracked_universe")
        custom_items = await (await universe_col.find()).to_list()
        universe = SEED_UNIVERSE.copy()
        if custom_items:
            for item in custom_items:
                universe[item["ticker"]] = item
        return universe

    async def calculate_all_scores(self) -> List[Dict[str, Any]]:
        universe = await self.get_tracked_universe()
        feed_statuses = await feed_manager.get_all_feed_statuses()

        news_stale = feed_statuses.get(FEED_NEWS, {}).get("is_stale", False)
        insider_stale = feed_statuses.get(FEED_INSIDERS, {}).get("is_stale", False)
        inst_stale = feed_statuses.get(FEED_INSTITUTIONAL, {}).get("is_stale", False)

        news_col = storage.get_collection("news")
        insiders_col = storage.get_collection("insiders")
        inst_col = storage.get_collection("institutional")

        all_news = await (await news_col.find()).to_list()
        all_insiders = await (await insiders_col.find()).to_list()
        all_inst = await (await inst_col.find()).to_list()

        results = []

        for ticker, meta in universe.items():
            ticker_news = [n for n in all_news if n.get("ticker") == ticker]
            news_lean = 0
            if ticker_news:
                leans = [n.get("lean", 0) for n in ticker_news]
                news_lean = 1 if sum(leans) > 0 else (-1 if sum(leans) < 0 else 0)

            ticker_insiders = [i for i in all_insiders if i.get("ticker") == ticker]
            insider_lean = 0
            if ticker_insiders:
                leans = [i.get("lean", 0) for i in ticker_insiders]
                insider_lean = 1 if sum(leans) > 0 else (-1 if sum(leans) < 0 else 0)

            ticker_inst = [inst for inst in all_inst if inst.get("ticker") == ticker]
            if not ticker_inst:
                ticker_inst = [inst for inst in all_inst if inst.get("ticker") == "EGX_MARKET_WIDE"]
            inst_lean = 0
            if ticker_inst:
                leans = [inst.get("lean", 0) for inst in ticker_inst]
                inst_lean = 1 if sum(leans) > 0 else (-1 if sum(leans) < 0 else 0)

            score_data = compute_money_match_score(
                news_lean=news_lean,
                insider_lean=insider_lean,
                inst_lean=inst_lean,
                news_stale=news_stale,
                insider_stale=insider_stale,
                inst_stale=inst_stale
            )

            results.append({
                "ticker": ticker,
                "name_en": meta.get("name_en", ticker),
                "name_ar": meta.get("name_ar", ticker),
                "sector": meta.get("sector", "EGX Equity"),
                "currency": "EGP",
                "score": score_data["score"],
                "direction": score_data["direction"],
                "strong_match": score_data["strong_match"],
                "active_sources_count": score_data["active_sources_count"],
                "coverage_cap": score_data["coverage_cap"],
                "signals": score_data["signals_breakdown"],
                "item_counts": {
                    "news": len(ticker_news),
                    "insiders": len(ticker_insiders),
                    "institutional": len(ticker_inst)
                }
            })

        results.sort(key=lambda x: (x["score"], x["active_sources_count"], x["ticker"]), reverse=True)
        return results

scoring_service = ScoringService()
