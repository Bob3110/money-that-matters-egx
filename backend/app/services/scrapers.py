import re
import httpx
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from app.config import is_host_allowed, SEED_UNIVERSE
from app.utils.rate_limiter import limiter
from app.utils.arabic_nlp import (
    extract_egx_ticker, is_macro_or_market_subject,
    determine_sentiment_lean, normalize_arabic
)
from app.utils.date_parser import parse_date_to_iso
from app.services.storage import storage
from app.services.feed_manager import (
    feed_manager, FEED_NEWS, FEED_INSIDERS, FEED_INSTITUTIONAL, FEED_MACRO
)

HEADERS = {
    "User-Agent": "MoneyThatMatters-EGX/1.0 (Mobile Research Public Dashboard; +https://github.com/money-that-matters-egx; Chrome/124.0.0.0)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

RSS_NEWS_SOURCES = [
    {
        "name": "Enterprise Egypt",
        "url": "https://enterprise.news/feed/",
        "language": "en"
    },
    {
        "name": "Daily News Egypt - Business",
        "url": "https://www.dailynewsegypt.com/category/business/feed/",
        "language": "en"
    },
    {
        "name": "Daily News Egypt - Economy",
        "url": "https://www.dailynewsegypt.com/category/economy/feed/",
        "language": "en"
    },
    {
        "name": "Daily News Egypt",
        "url": "https://www.dailynewsegypt.com/feed/",
        "language": "en"
    }
]

class EGXDataScraper:
    def __init__(self):
        pass

    async def _fetch_url(self, url: str, timeout: float = 12.0) -> Optional[str]:
        if not is_host_allowed(url):
            print(f"[Gatekeeper] Discarded disallowed host: {url}")
            return None
        
        await limiter.acquire(url, min_interval=1.0)

        try:
            async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=timeout) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return resp.text
                else:
                    print(f"Fetch {url} returned status {resp.status_code}")
        except Exception as e:
            print(f"Notice fetching {url}: {e}")
        return None

    async def scrape_news(self) -> int:
        col = storage.get_collection("news")
        valid_items: List[Dict[str, Any]] = []

        universe_col = storage.get_collection("tracked_universe")
        custom_universe_list = await (await universe_col.find()).to_list()
        custom_universe = {item["ticker"]: item for item in custom_universe_list} if custom_universe_list else SEED_UNIVERSE.copy()

        # 1. Scrape RSS Feeds
        for src in RSS_NEWS_SOURCES:
            url = src["url"]
            source_name = src["name"]
            
            if not is_host_allowed(url):
                continue

            content = await self._fetch_url(url)
            if not content:
                continue

            try:
                feed = feedparser.parse(content)
                for entry in feed.entries[:20]:
                    link = getattr(entry, "link", "")
                    title = getattr(entry, "title", "").strip()
                    summary = getattr(entry, "summary", "").strip()
                    pub_date_raw = getattr(entry, "published", "") or getattr(entry, "updated", "")
                    iso_date = parse_date_to_iso(pub_date_raw) or datetime.now(timezone.utc).isoformat()

                    if not is_host_allowed(link):
                        continue

                    full_text = f"{title} {summary}"

                    matched_ticker = extract_egx_ticker(full_text, custom_universe)
                    is_macro = is_macro_or_market_subject(full_text)

                    if not matched_ticker and not is_macro:
                        continue

                    lean = determine_sentiment_lean(full_text)

                    # Dynamic ticker expansion
                    if matched_ticker and matched_ticker not in custom_universe:
                        new_ticker_doc = {
                            "ticker": matched_ticker,
                            "name_en": matched_ticker,
                            "name_ar": matched_ticker,
                            "sector": "EGX Dynamic Discovery",
                            "discovered_at": iso_date
                        }
                        await universe_col.update_one(
                            {"ticker": matched_ticker},
                            {"$set": new_ticker_doc},
                            upsert=True
                        )
                        custom_universe[matched_ticker] = new_ticker_doc

                    item_doc = {
                        "url": link,
                        "headline": title,
                        "summary": summary[:400] if summary else None,
                        "outlet": source_name,
                        "published_at": iso_date,
                        "ticker": matched_ticker,
                        "lean": lean,
                        "is_macro": is_macro
                    }
                    valid_items.append(item_doc)
            except Exception as ex:
                print(f"Error parsing feed from {source_name}: {ex}")

        # 2. Scrape Mubasher latest & top market headlines
        for sub_path in ["latest", "top"]:
            m_url = f"https://www.mubasher.info/news/eg/now/{sub_path}"
            m_html = await self._fetch_url(m_url)
            if m_html:
                try:
                    soup = BeautifulSoup(m_html, "html.parser")
                    for a in soup.find_all("a", href=True):
                        href = a["href"]
                        if "/news/" in href and any(c.isdigit() for c in href):
                            title = a.get_text(" ", strip=True)
                            if len(title) > 20:
                                link = f"https://www.mubasher.info{href}" if href.startswith("/") else href
                                if not is_host_allowed(link):
                                    continue
                                
                                matched_ticker = extract_egx_ticker(title, custom_universe)
                                is_macro = is_macro_or_market_subject(title)

                                if not matched_ticker and not is_macro:
                                    continue

                                lean = determine_sentiment_lean(title)
                                now_iso = datetime.now(timezone.utc).isoformat()

                                if matched_ticker and matched_ticker not in custom_universe:
                                    new_ticker_doc = {
                                        "ticker": matched_ticker,
                                        "name_en": matched_ticker,
                                        "name_ar": matched_ticker,
                                        "sector": "EGX Dynamic Discovery",
                                        "discovered_at": now_iso
                                    }
                                    await universe_col.update_one(
                                        {"ticker": matched_ticker},
                                        {"$set": new_ticker_doc},
                                        upsert=True
                                    )
                                    custom_universe[matched_ticker] = new_ticker_doc

                                item_doc = {
                                    "url": link,
                                    "headline": title,
                                    "summary": None,
                                    "outlet": "Mubasher Egypt",
                                    "published_at": now_iso,
                                    "ticker": matched_ticker,
                                    "lean": lean,
                                    "is_macro": is_macro
                                }
                                valid_items.append(item_doc)
                except Exception as e:
                    print(f"Error parsing Mubasher {sub_path}: {e}")

        # Deduplicate valid items by url
        unique_items = {}
        for it in valid_items:
            if it["url"] not in unique_items:
                unique_items[it["url"]] = it
        deduped = list(unique_items.values())

        if deduped:
            for item in deduped:
                await col.update_one(
                    {"url": item["url"]},
                    {"$set": item},
                    upsert=True
                )
            await feed_manager.record_sync_success(FEED_NEWS, len(deduped))
            return len(deduped)
        else:
            existing_count = await col.count_documents()
            if existing_count > 0:
                await feed_manager.record_sync_failure(FEED_NEWS, "Preserving cached records.")
            else:
                await feed_manager.record_sync_failure(FEED_NEWS, "Waiting for initial feed sync.")
            return existing_count

    async def scrape_insiders(self) -> int:
        col = storage.get_collection("insiders")
        valid_items: List[Dict[str, Any]] = []

        universe = SEED_UNIVERSE.copy()
        universe_col = storage.get_collection("tracked_universe")
        custom_universe_list = await (await universe_col.find()).to_list()
        if custom_universe_list:
            for item in custom_universe_list:
                universe[item["ticker"]] = item

        # Scrape official EGX & FRA announcements published on Mubasher
        disclosures_url = "https://www.mubasher.info/news/eg/now/announcements"
        content = await self._fetch_url(disclosures_url)
        if content:
            try:
                soup = BeautifulSoup(content, "html.parser")
                blocks = soup.find_all(["div", "article", "li"], class_=lambda c: c and any(k in str(c).lower() for k in ["item", "block", "announcement"]))
                for block in blocks:
                    a = block.find("a", href=True)
                    if not a:
                        continue
                    href = a["href"]
                    title = a.get_text(" ", strip=True)
                    link = f"https://www.mubasher.info{href}" if href.startswith("/") else href
                    if not is_host_allowed(link):
                        continue

                    # Extract relative date or timestamp if available
                    time_el = block.find(["time", "span", "div"], class_=lambda c: c and any(k in str(c).lower() for k in ["time", "date", "ago"]))
                    raw_date = time_el.get_text(strip=True) if time_el else ""
                    iso_date = parse_date_to_iso(raw_date) or datetime.now(timezone.utc).isoformat()

                    norm = normalize_arabic(title).lower()

                    is_insider = any(w in norm for w in [
                        "مجلس اداره", "مجلس الاداره", "قرارات مجلس", "داخليين", "مسؤولين",
                        "اسهم خزينه", "شراء اسهم خزينه", "بيع اسهم خزينه", "مطلعين", "تعامل داخلي",
                        "insider", "treasury shares", "board member", "executive", "بيان من الشركه",
                        "افصاح", "الرقابه الماليه"
                    ])
                    if not is_insider:
                        continue

                    ticker = extract_egx_ticker(title, universe)
                    if not ticker:
                        continue

                    tx_type = "Buy"
                    lean = 1
                    if "بيع" in norm or "sell" in norm:
                        tx_type = "Sell"
                        lean = -1
                    elif "خزينه" in norm or "treasury" in norm:
                        tx_type = "Treasury Buyback"
                        lean = 1
                    elif "قرارات مجلس" in norm or "مجلس" in norm:
                        tx_type = "Board Resolution"
                        lean = 1 if any(b in norm for b in ["زياده", "توزيع", "شراء", "ربح", "استحواذ"]) else 0

                    role = "Board / Executive"
                    if "رئيس مجلس" in norm:
                        role = "Chairman / Board"
                    elif "عضو مجلس" in norm:
                        role = "Board Member"
                    elif "خزينه" in norm:
                        role = "Treasury Shares Operation"
                    elif "قرارات مجلس" in norm:
                        role = "Board of Directors Resolutions"

                    item = {
                        "filing_id": link or f"{ticker}_{iso_date}_{tx_type}",
                        "ticker": ticker,
                        "company_name": universe.get(ticker, {}).get("name_ar", ticker),
                        "insider_name": "Disclosed Insider / Entity",
                        "insider_title": role,
                        "transaction_type": tx_type,
                        "share_count": None,
                        "omission_reason": "Share volume detail disclosed inside full FRA PDF filing notice.",
                        "filing_date": iso_date,
                        "source_url": link,
                        "lean": lean
                    }
                    valid_items.append(item)
            except Exception as e:
                print(f"Error scraping insiders: {e}")

        # Deduplicate
        unique_insiders = {it["filing_id"]: it for it in valid_items}
        deduped = list(unique_insiders.values())

        if deduped:
            for item in deduped:
                await col.update_one(
                    {"filing_id": item["filing_id"]},
                    {"$set": item},
                    upsert=True
                )
            await feed_manager.record_sync_success(FEED_INSIDERS, len(deduped))
            return len(deduped)
        else:
            existing = await col.count_documents()
            if existing == 0:
                await feed_manager.record_sync_failure(FEED_INSIDERS, "Waiting for initial insider disclosures sync.")
            else:
                await feed_manager.record_sync_failure(FEED_INSIDERS, "Preserving cached records.")
            return existing

    async def scrape_institutional(self) -> int:
        col = storage.get_collection("institutional")
        valid_items: List[Dict[str, Any]] = []

        universe = SEED_UNIVERSE.copy()

        # Scrape stock news & pulse analysis for institutional flows & fund transactions
        sources = [
            "https://www.mubasher.info/news/eg/pulse/stocks",
            "https://www.mubasher.info/news/eg/pulse/analysis",
            "https://www.mubasher.info/news/eg/now/announcements"
        ]

        for url in sources:
            content = await self._fetch_url(url)
            if not content:
                continue

            try:
                soup = BeautifulSoup(content, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if "/news/" in href and any(c.isdigit() for c in href):
                        title = a.get_text(" ", strip=True)
                        norm = normalize_arabic(title).lower()

                        is_inst = any(w in norm for w in [
                            "مؤسسات", "اجانب", "عرب", "مصريين", "صافي تعاملات", "نسبه مساهمه",
                            "افصاح ملكيه", "حصه", "هيكل ملكيه", "صندوق", "صناديق", "institutional",
                            "foreign", "stake", "shareholding"
                        ])
                        if not is_inst:
                            continue

                        link = f"https://www.mubasher.info{href}" if href.startswith("/") else href
                        if not is_host_allowed(link):
                            continue

                        ticker = extract_egx_ticker(title, universe)
                        lean = determine_sentiment_lean(title)
                        
                        tx_type = "Net Buy" if lean >= 0 else "Net Sell"
                        if "يبيع" in norm or "بيع" in norm:
                            tx_type = "Fund Sell"
                            lean = -1
                        elif "يشتري" in norm or "شراء" in norm:
                            tx_type = "Fund Buy"
                            lean = 1
                        elif "حصه" in norm or "نسبه" in norm:
                            tx_type = "Stake Disclosure (>5%)"

                        investor_entity = "Institutions (Market-Wide)"
                        if "اجانب" in norm or "foreign" in norm:
                            investor_entity = "Foreign Institutions"
                        elif "عرب" in norm or "arab" in norm:
                            investor_entity = "Arab Institutions"
                        elif "مصريين" in norm or "egyptian" in norm:
                            investor_entity = "Egyptian Institutions"
                        elif "صندوق" in norm or "صناديق" in norm:
                            investor_entity = "Institutional Investment Fund"

                        now_iso = datetime.now(timezone.utc).isoformat()
                        item = {
                            "id": link,
                            "ticker": ticker or "EGX_MARKET_WIDE",
                            "investor_entity": investor_entity,
                            "transaction_type": tx_type,
                            "volume_egp": None,
                            "omission_reason": "Aggregate EGP value available in EGX end-of-day market summary sheet / bulletin.",
                            "disclosure_date": now_iso,
                            "source_url": link,
                            "lean": lean
                        }
                        valid_items.append(item)
            except Exception as e:
                print(f"Error scraping institutional from {url}: {e}")

        # Deduplicate
        unique_inst = {it["id"]: it for it in valid_items}
        deduped = list(unique_inst.values())

        if deduped:
            for item in deduped:
                await col.update_one(
                    {"id": item["id"]},
                    {"$set": item},
                    upsert=True
                )
            await feed_manager.record_sync_success(FEED_INSTITUTIONAL, len(deduped))
            return len(deduped)
        else:
            existing = await col.count_documents()
            if existing == 0:
                await feed_manager.record_sync_failure(FEED_INSTITUTIONAL, "Waiting for initial institutional data sync.")
            else:
                await feed_manager.record_sync_failure(FEED_INSTITUTIONAL, "Preserving cached institutional records.")
            return existing

    async def scrape_macro(self) -> int:
        col = storage.get_collection("macro")
        valid_items: List[Dict[str, Any]] = []

        # 1. Scrape Enterprise Egypt & DNE for Macro news
        cbe_rss_urls = [
            ("Enterprise Egypt", "https://enterprise.news/feed/"),
            ("Daily News Egypt - Economy", "https://www.dailynewsegypt.com/category/economy/feed/")
        ]

        for src_name, url in cbe_rss_urls:
            content = await self._fetch_url(url)
            if not content:
                continue

            try:
                feed = feedparser.parse(content)
                for entry in feed.entries:
                    title = getattr(entry, "title", "").strip()
                    link = getattr(entry, "link", "").strip()
                    summary = getattr(entry, "summary", "").strip()
                    pub_raw = getattr(entry, "published", "") or getattr(entry, "updated", "")
                    iso_date = parse_date_to_iso(pub_raw) or datetime.now(timezone.utc).isoformat()

                    full_text = f"{title} {summary}"
                    norm = normalize_arabic(full_text).lower()

                    if is_macro_or_market_subject(full_text):
                        indicator = "Macro Policy / Economy"
                        if "فائده" in norm or "interest" in norm or "cbe" in norm or "مركزي" in norm or "monetary" in norm:
                            indicator = "CBE Monetary Policy"
                        elif "تضخم" in norm or "inflation" in norm or "capmas" in norm:
                            indicator = "CAPMAS Inflation"
                        elif "اذون" in norm or "treasury" in norm or "yield" in norm or "سندات" in norm or "debt" in norm:
                            indicator = "Treasury Yields / Debt"
                        elif "صرف" in norm or "جنيه" in norm or "دولار" in norm or "currency" in norm:
                            indicator = "Exchange Rates & FX Reserves"

                        item = {
                            "id": link or f"macro_{iso_date}",
                            "headline": title,
                            "indicator": indicator,
                            "source": f"{src_name} / CBE",
                            "published_at": iso_date,
                            "source_url": link,
                            "lean": determine_sentiment_lean(full_text)
                        }
                        valid_items.append(item)
            except Exception as e:
                print(f"Error scraping macro from {src_name}: {e}")

        # Deduplicate
        unique_macro = {it["id"]: it for it in valid_items}
        deduped = list(unique_macro.values())

        if deduped:
            for item in deduped:
                await col.update_one(
                    {"id": item["id"]},
                    {"$set": item},
                    upsert=True
                )
            await feed_manager.record_sync_success(FEED_MACRO, len(deduped))
            return len(deduped)
        else:
            existing = await col.count_documents()
            if existing == 0:
                await feed_manager.record_sync_failure(FEED_MACRO, "Waiting for initial macro sync.")
            else:
                await feed_manager.record_sync_failure(FEED_MACRO, "Preserving cached macro records.")
            return existing

scraper = EGXDataScraper()
