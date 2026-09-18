import asyncio
import time
from typing import Dict, Any
from urllib.parse import urlparse

class HostRateLimiter:
    """
    Rate limiter that enforces ONE shared async limiter per host.
    CRITICAL: asyncio.Lock() instances are created lazily inside the active event loop
    to prevent loop-binding exceptions.
    """
    def __init__(self, default_interval: float = 1.0):
        self.default_interval = default_interval
        self._states: Dict[str, Dict[str, Any]] = {}

    def _extract_host(self, host_or_url: str) -> str:
        if not host_or_url:
            return "default"
        s = host_or_url.strip().lower()
        if "://" in s:
            try:
                parsed = urlparse(s)
                s = parsed.netloc or "default"
            except Exception:
                pass
        if ":" in s:
            s = s.split(":")[0]
        return s or "default"

    async def acquire(self, host_or_url: str, min_interval: float = None) -> float:
        host = self._extract_host(host_or_url)
        interval = min_interval if min_interval is not None else self.default_interval

        # Lazy creation inside active event loop
        if host not in self._states:
            self._states[host] = {
                "lock": asyncio.Lock(),
                "last_time": 0.0
            }
        
        state = self._states[host]
        async with state["lock"]:
            now = time.monotonic()
            elapsed = now - state["last_time"]
            wait_time = interval - elapsed
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            state["last_time"] = time.monotonic()
            return max(0.0, wait_time)

limiter = HostRateLimiter(default_interval=1.0)
