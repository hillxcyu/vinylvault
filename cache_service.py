import time
import logging
from typing import Any, Optional, Dict

logger = logging.getLogger("cache_service")

class SimpleTTLCache:
    def __init__(self, default_ttl_seconds: int = 86400):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            entry = self._cache[key]
            if time.time() < entry["expires_at"]:
                logger.info(f"Cache hit for key: {key}")
                return entry["value"]
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        self._cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl
        }
        logger.info(f"Cached key: {key} (TTL: {ttl}s)")

cache_service = SimpleTTLCache()
