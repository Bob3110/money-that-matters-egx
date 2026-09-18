import os
from urllib.parse import urlparse

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'money_matters_egx')

# Exact allow-listed domains
ALLOWED_HOSTS = {
    'reuters.com',
    'bloomberg.com',
    'cnbcarabia.com',
    'enterprise.press',
    'enterprise.news',
    'mubasher.info',
    'almalnews.com',
    'alborsaanews.com',
    'dailynewsegypt.com',
    'egx.com.eg',
    'fra.gov.eg',
    'cbe.org.eg'
}

def is_host_allowed(url_or_host: str) -> bool:
    if not url_or_host:
        return False
    host = url_or_host.strip().lower()
    if '://' in host:
        try:
            parsed = urlparse(host)
            host = parsed.netloc
        except Exception:
            return False
    # Strip port if present
    if ':' in host:
        host = host.split(':')[0]
    
    # Strict boundary match
    for allowed in ALLOWED_HOSTS:
        if host == allowed or host.endswith('.' + allowed):
            return True
    return False

from app.egx_universe import EGX_FULL_UNIVERSE

# Complete EGX Universe (all ~230+ companies listed on the Egyptian Exchange)
SEED_UNIVERSE = EGX_FULL_UNIVERSE

STALE_HOURS_THRESHOLD = 24
