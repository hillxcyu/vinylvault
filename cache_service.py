import time
import logging
import threading
from collections import OrderedDict
from typing import Any, Optional

logger = logging.getLogger("cache_service")

class SimpleTTLCache:
    def __init__(self, default_ttl_seconds: int = 86400, max_size: int = 1000):
        self._cache: OrderedDict[str, dict] = OrderedDict()
        self.default_ttl = default_ttl_seconds
        self.max_size = max_size
        self._lock = threading.Lock()

    def _prune_expired_unlocked(self):
        now = time.time()
        expired_keys = [k for k, v in self._cache.items() if now >= v["expires_at"]]
        for k in expired_keys:
            del self._cache[k]

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if time.time() < entry["expires_at"]:
                    self._cache.move_to_end(key)
                    logger.info(f"Cache hit for key: {key}")
                    return entry["value"]
                else:
                    del self._cache[key]
            return None

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        with self._lock:
            self._prune_expired_unlocked()
            if key in self._cache:
                del self._cache[key]
            elif len(self._cache) >= self.max_size:
                oldest_key, _ = self._cache.popitem(last=False)
                logger.info(f"Evicted oldest cache entry: {oldest_key}")

            ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
            self._cache[key] = {
                "value": value,
                "expires_at": time.time() + ttl
            }
            logger.info(f"Cached key: {key} (TTL: {ttl}s)")

cache_service = SimpleTTLCache()

