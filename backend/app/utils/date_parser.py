import re
from datetime import datetime, timezone, timedelta
from typing import Optional
from dateutil import parser as du_parser

ARABIC_MONTHS = {
    "يناير": 1, "فبراير": 2, "مارس": 3, "ابريل": 4, "أبريل": 4,
    "مايو": 5, "يونيو": 6, "يوليو": 7, "اغسطس": 8, "أغسطس": 8,
    "سبتمبر": 9, "اكتوبر": 10, "أكتوبر": 10, "نوفمبر": 11, "ديسمبر": 12
}

def parse_arabic_relative_time(text: str) -> Optional[datetime]:
    if not text:
        return None
    now = datetime.now(timezone.utc)
    t = text.strip()
    # Normalize alef variations and teh marbuta for robust regex
    t_norm = re.sub(r"[إأآا]", "ا", t)
    t_norm = re.sub(r"ة", "ه", t_norm)

    m_hour = re.search(r"منذ\s+(\d+)\s+ساع", t_norm)
    if m_hour:
        hours = int(m_hour.group(1))
        return now - timedelta(hours=hours)
    if "منذ ساعتين" in t_norm or "منذ ساعتان" in t_norm:
        return now - timedelta(hours=2)
    if "منذ ساعه" in t_norm:
        return now - timedelta(hours=1)

    m_day = re.search(r"منذ\s+(\d+)\s+(يوم|ايام)", t_norm)
    if m_day:
        days = int(m_day.group(1))
        return now - timedelta(days=days)
    if "منذ يومين" in t_norm:
        return now - timedelta(days=2)
    if "منذ يوم" in t_norm or "امس" in t_norm:
        return now - timedelta(days=1)

    m_min = re.search(r"منذ\s+(\d+)\s+دقيق", t_norm)
    if m_min:
        mins = int(m_min.group(1))
        return now - timedelta(minutes=mins)

    m_week = re.search(r"منذ\s+(\d+)\s+(اسبوع|اسابيع)", t_norm)
    if m_week:
        weeks = int(m_week.group(1))
        return now - timedelta(weeks=weeks)

    return None

ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

def parse_date_to_iso(date_str: str) -> Optional[str]:
    if not date_str:
        return None
    
    cleaned = date_str.strip().translate(ARABIC_DIGITS)
    
    rel = parse_arabic_relative_time(cleaned)
    if rel:
        return rel.isoformat()

    # Replace Arabic AM/PM markers
    cleaned = re.sub(r"\b(مساءً|مساء|م)\b", "PM", cleaned)
    cleaned = re.sub(r"\b(صباحاً|صباح|ص)\b", "AM", cleaned)

    for ar_month, m_num in ARABIC_MONTHS.items():
        if ar_month in cleaned:
            cleaned = cleaned.replace(ar_month, f"/{m_num}/")
            break

    try:
        now_utc = datetime.now(timezone.utc)
        dt = du_parser.parse(cleaned, dayfirst=True, default=now_utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    except Exception:
        pass

    return None
