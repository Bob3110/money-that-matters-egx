import re
from typing import Optional, Dict, Any, List

TASHKEEL_REGEX = re.compile(r'[\u064B-\u065F\u0670]')
TATWEEL_CHAR = '\u0640'

def normalize_arabic(text: str) -> str:
    """
    Normalizes Arabic text for robust search and entity matching:
    - Removes tashkeel / diacritics
    - Removes tatweel (kashida)
    - Unifies Alef variations (إ, أ, آ, ا -> ا)
    - Unifies Teh Marbuta and Heh (ة -> ه)
    - Unifies Yaa and Alef Maksura (ى, ي -> ي)
    """
    if not text:
        return ""
    
    s = TASHKEEL_REGEX.sub("", text)
    s = s.replace(TATWEEL_CHAR, "")

    s = re.sub(r"[إأآا]", "ا", s)
    s = re.sub(r"ة", "ه", s)
    s = re.sub(r"[ىي]", "ي", s)
    s = re.sub(r"[ؤ]", "و", s)
    s = re.sub(r"[ئ]", "ي", s)

    s = re.sub(r"\s+", " ", s)
    return s.strip()

STOCK_ALIASES: Dict[str, List[str]] = {
    "COMI.CA": ["comi", "cib", "البنك التجاري الدولي", "التجاري الدولي"],
    "FWRY.CA": ["fwry", "fawry", "فوري", "مدفوعات فوري"],
    "TMGH.CA": ["tmgh", "tmg", "طلعت مصطفي", "طلعت مصطفى", "مجموعه طلعت مصطفي"],
    "SWDY.CA": ["swdy", "elsewedy", "sewedy", "السويدي", "السويدي اليكتريك"],
    "HRHO.CA": ["hrho", "efg", "hermes", "اي اف جي", "هيرميس", "المجموعه الماليه هيرميس"],
    "ABUK.CA": ["abuk", "abu qir", "ابو قير", "ابوقير للاسمده", "ابو قير للاسمدة"],
    "EKHO.CA": ["ekho", "egypt kuwait", "المصريه الكويتيه", "القابضه المصريه الكويتيه"],
    "ETEL.CA": ["etel", "telecom egypt", "المصريه للاتصالات", "وي", "we"],
    "ESRS.CA": ["esrs", "ezz steel", "حديد عز", "عز للصلب"],
    "AMOC.CA": ["amoc", "اموك", "الاسكندريه للزيوت المعدنيه"],
    "SKPC.CA": ["skpc", "sidpec", "سيدي كرير", "سيدي كرير للبتروكيماويات"],
    "HELI.CA": ["heli", "heliopolis", "مصر الجديده", "مصر الجديده للاسكان"],
    "MASR.CA": ["masr", "mnhd", "madinet masr", "مدينه مصر", "مدينه نصر للاسكان"],
    "ORAS.CA": ["oras", "orascom construction", "اوراسكوم كونستراكشون", "اوراسكوم للانشاء"],
    "PHDC.CA": ["phdc", "palm hills", "بالم هيلز", "بالم هيلز للتعمير"],
    "EAST.CA": ["east", "eastern company", "ايسترن كومباني", "الشرقيه للدخان", "الشرقيه ايسترن"],
    "JUFO.CA": ["jufo", "juhayna", "جهينه", "جهينه للصناعات الغذائيه"],
    "ISPH.CA": ["isph", "ibnsina", "ابن سينا", "ابن سينا فارما"],
    "CIEB.CA": ["cieb", "credit agricole", "كريدي اجريكول", "بنك كريدي اجريكول"],
    "ADIB.CA": ["adib", "abu dhabi islamic", "مصرف ابو ظبي الاسلامي", "ابو ظبي الاسلامي"],
    "BINV.CA": ["binv", "b investments", "بي انفستمنتس", "بي إنفستمنتس", "gourmet", "جورميه", "gour"],
    "GOUR.CA": ["gour", "gourmet", "جورميه", "جورميه ايجيبت", "gourmet egypt", "gourmet egypt.com foods"]
}

MACRO_KEYWORDS = [
    "egx", "egx30", "egx70", "البورصه المصريه", "البورصه", "البنك المركزي",
    "مركزي", "cbe", "مركزي مصري", "الفائده", "اسعار الفائده", "لجنه السياسه النقديه",
    "الجنيه المصري", "الدولار", "اذون الخزانه", "سندات الخزانه", "التضخم",
    "تضخم", "capmas", "الجهاز المركزي للتعبئه العامه والاحصاء", "الرقابه الماليه", "fra"
]

def extract_egx_ticker(text: str, custom_universe: Optional[Dict[str, Any]] = None) -> Optional[str]:
    if not text:
        return None
    
    text_norm = normalize_arabic(text).lower()

    # 1. Explicit EGX ticker symbol e.g. COMI.CA, NINH.CA, MEPA.CA
    explicit_ca = re.search(r"\b([A-Z]{3,5})\.CA\b", text.upper())
    if explicit_ca:
        return explicit_ca.group(1) + ".CA"

    # 2. Known alias or symbol without .CA
    for cand_match in re.finditer(r"\b([A-Z]{3,5})\b", text.upper()):
        cand = cand_match.group(1) + ".CA"
        if cand in STOCK_ALIASES or (custom_universe and cand in custom_universe):
            return cand

    # Check aliases
    for ticker, aliases in STOCK_ALIASES.items():
        for alias in aliases:
            norm_alias = normalize_arabic(alias).lower()
            pattern = r"\b" + re.escape(norm_alias) + r"\b"
            if re.search(pattern, text_norm):
                return ticker

    if custom_universe:
        for ticker, data in custom_universe.items():
            base = ticker.replace(".CA", "").lower()
            if base in text_norm:
                return ticker
            if "name_en" in data and data["name_en"].lower() in text_norm:
                return ticker
            if "name_ar" in data and normalize_arabic(data["name_ar"]).lower() in text_norm:
                return ticker

    return None

def is_macro_or_market_subject(text: str) -> bool:
    if not text:
        return False
    text_norm = normalize_arabic(text).lower()
    for kw in MACRO_KEYWORDS:
        norm_kw = normalize_arabic(kw).lower()
        if norm_kw in text_norm:
            return True
    return False

BULLISH_KEYWORDS_AR = [
    "صعود", "ارتفاع", "نمو", "ارباح", "شراء", "توزيعات", "قفزه", "زياده", "ارباح قياسيه",
    "مكاسب", "استحواذ", "تدفقات نقديه", "صافي شراء", "انتعاش", "طرح", "صفقه"
]
BEARISH_KEYWORDS_AR = [
    "هبوط", "تراجع", "خسائر", "انخفاض", "بيع", "هبوط حاد", "خساره", "تقليص",
    "تخفيض", "غرامه", "صافي بيع", "نزول", "تراجع ارباح", "دعوي قضائيه"
]

BULLISH_KEYWORDS_EN = [
    "profit", "surge", "jump", "gain", "buy", "acquired", "acquisition", "net buy",
    "revenue growth", "bullish", "dividend", "upgrade", "rally", "soar", "outperform"
]
BEARISH_KEYWORDS_EN = [
    "drop", "plunge", "loss", "losses", "decline", "fall", "sell", "net sell",
    "slump", "loss-making", "bearish", "downgrade", "penalty", "fine", "underperform"
]

def determine_sentiment_lean(headline_or_text: str) -> int:
    if not headline_or_text:
        return 0
    
    text_norm = normalize_arabic(headline_or_text).lower()
    bull_count = 0
    bear_count = 0

    for kw in BULLISH_KEYWORDS_AR:
        if kw in text_norm:
            bull_count += 1
    for kw in BULLISH_KEYWORDS_EN:
        if kw in text_norm:
            bull_count += 1

    for kw in BEARISH_KEYWORDS_AR:
        if kw in text_norm:
            bear_count += 1
    for kw in BEARISH_KEYWORDS_EN:
        if kw in text_norm:
            bear_count += 1

    if bull_count > bear_count:
        return 1
    elif bear_count > bull_count:
        return -1
    return 0
