from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from app.services.scoring import scoring_service
from app.services.storage import storage
from app.services.feed_manager import feed_manager
from app.services.scrapers import scraper

router = APIRouter(prefix="/api")

@router.get("/money-match")
async def get_money_match(sector: Optional[str] = None, search: Optional[str] = None):
    scores = await scoring_service.calculate_all_scores()
    if sector:
        scores = [s for s in scores if s["sector"].lower() == sector.lower()]
    if search:
        s_lower = search.strip().lower()
        scores = [s for s in scores if (s_lower in s["ticker"].lower() or s_lower in s["name_en"].lower() or s_lower in s["name_ar"].lower())]
    return {
        "count": len(scores),
        "data": scores
    }

@router.get("/money-match/{ticker}")
async def get_money_match_detail(ticker: str):
    ticker_clean = ticker.upper().strip()
    if not ticker_clean.endswith(".CA") and "." not in ticker_clean:
        ticker_clean += ".CA"
        
    scores = await scoring_service.calculate_all_scores()
    match = next((s for s in scores if s["ticker"] == ticker_clean), None)
    if not match:
        raise HTTPException(status_code=404, detail="Ticker not found in tracked universe")

    news_col = storage.get_collection("news")
    insiders_col = storage.get_collection("insiders")
    inst_col = storage.get_collection("institutional")

    ticker_news = await (await news_col.find({"ticker": ticker_clean})).to_list(10)
    ticker_insiders = await (await insiders_col.find({"ticker": ticker_clean})).to_list(10)
    ticker_inst = await (await inst_col.find({"ticker": ticker_clean})).to_list(10)

    return {
        "summary": match,
        "underlying": {
            "news": ticker_news,
            "insiders": ticker_insiders,
            "institutional": ticker_inst
        }
    }

@router.get("/news")
async def get_news(ticker: Optional[str] = None, limit: int = 50):
    col = storage.get_collection("news")
    query = {}
    if ticker:
        t_clean = ticker.upper().strip()
        if not t_clean.endswith(".CA") and "." not in t_clean:
            t_clean += ".CA"
        query["ticker"] = t_clean
    cursor = await col.find(query, sort=[("published_at", -1)], limit=limit)
    items = await cursor.to_list(limit)
    status = await feed_manager.get_feed_status("news")
    return {
        "status": status,
        "count": len(items),
        "data": items
    }

@router.get("/insiders")
async def get_insiders(buys_only: bool = False, ticker: Optional[str] = None, limit: int = 50):
    col = storage.get_collection("insiders")
    query = {}
    if buys_only:
        query["transaction_type"] = {"$in": ["Buy", "Treasury Buyback"]}
    if ticker:
        t_clean = ticker.upper().strip()
        if not t_clean.endswith(".CA") and "." not in t_clean:
            t_clean += ".CA"
        query["ticker"] = t_clean

    cursor = await col.find(query, sort=[("filing_date", -1)], limit=limit)
    items = await cursor.to_list(limit)
    status = await feed_manager.get_feed_status("insiders")
    return {
        "status": status,
        "count": len(items),
        "data": items
    }

@router.get("/institutional")
async def get_institutional(ticker: Optional[str] = None, limit: int = 50):
    col = storage.get_collection("institutional")
    query = {}
    if ticker:
        t_clean = ticker.upper().strip()
        if not t_clean.endswith(".CA") and "." not in t_clean:
            t_clean += ".CA"
        query["ticker"] = t_clean

    cursor = await col.find(query, sort=[("disclosure_date", -1)], limit=limit)
    items = await cursor.to_list(limit)
    status = await feed_manager.get_feed_status("institutional")
    return {
        "status": status,
        "count": len(items),
        "data": items
    }

@router.get("/macro")
async def get_macro(limit: int = 30):
    col = storage.get_collection("macro")
    cursor = await col.find({}, sort=[("published_at", -1)], limit=limit)
    items = await cursor.to_list(limit)
    status = await feed_manager.get_feed_status("macro")
    return {
        "status": status,
        "count": len(items),
        "data": items
    }

@router.get("/feed-status")
async def get_feed_statuses():
    return await feed_manager.get_all_feed_statuses()

async def execute_full_refresh():
    try:
        await scraper.scrape_news()
        await scraper.scrape_insiders()
        await scraper.scrape_institutional()
        await scraper.scrape_macro()
    except Exception as e:
        print(f"Error during refresh execution: {e}")

@router.post("/refresh")
async def trigger_refresh(background_tasks: BackgroundTasks):
    background_tasks.add_task(execute_full_refresh)
    return {
        "message": "Sync refresh scheduled in background",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
