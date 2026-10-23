import time
from typing import Any, Dict, Optional
from threading import Lock

class SimpleTTLCache:
    """
    A simple thread-safe In-Memory Cache with Time-To-Live (TTL).
    Used as a lightweight alternative to Redis to prevent repeated DB 
    queries for identical rolling windows within the same minute.
    """
    def __init__(self, ttl_seconds: int = 60):
        self.ttl = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            entry = self.cache.get(key)
            if not entry:
                return None
            if time.time() > entry['expiry']:
                del self.cache[key]
                return None
            return entry['value']

    def set(self, key: str, value: Any):
        with self.lock:
            self.cache[key] = {
                'value': value,
                'expiry': time.time() + self.ttl
            }

    def clear(self):
        with self.lock:
            self.cache.clear()

# Global cache instance for telemetry
telemetry_cache = SimpleTTLCache(ttl_seconds=30)
