"""Simple in-memory TTL cache with max-size eviction."""

import hashlib
import time
from dataclasses import dataclass
from threading import Lock
from typing import Any, Optional


@dataclass
class _Entry:
    value: Any
    expires_at: float
    inserted_at: float


class TTLCache:
    def __init__(self, ttl_seconds: int, max_entries: int = 500):
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._store: dict[str, _Entry] = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if entry is None or entry.expires_at < time.time():
                self._store.pop(key, None)
                return None
            return entry.value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            if len(self._store) >= self.max_entries and key not in self._store:
                oldest = min(self._store, key=lambda k: self._store[k].inserted_at)
                del self._store[oldest]
            now = time.time()
            self._store[key] = _Entry(value, now + self.ttl_seconds, now)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def __len__(self) -> int:
        return len(self._store)


def make_key(*parts: str) -> str:
    """Hash arbitrary string parts into a stable cache key."""
    joined = "\x1f".join(parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


# Global cache instances
transform_cache = TTLCache(ttl_seconds=3600, max_entries=500)   # 1 hour
tts_cache = TTLCache(ttl_seconds=86400, max_entries=200)         # 24 hours, bigger payloads → smaller cap
