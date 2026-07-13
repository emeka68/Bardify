"""In-memory usage counters for the /stats endpoint."""

from collections import Counter
from threading import Lock


class Stats:
    def __init__(self):
        self._lock = Lock()
        self.style_usage = Counter()
        self.voice_usage = Counter()
        self.cache_hits = 0
        self.cache_misses = 0
        self.errors = Counter()  # keyed by endpoint

    def record_transform(self, style: str, cache_hit: bool):
        with self._lock:
            self.style_usage[style] += 1
            self.cache_hits += int(cache_hit)
            self.cache_misses += int(not cache_hit)

    def record_speak(self, voice: str, cache_hit: bool):
        with self._lock:
            self.voice_usage[voice] += 1
            self.cache_hits += int(cache_hit)
            self.cache_misses += int(not cache_hit)

    def record_error(self, endpoint: str):
        with self._lock:
            self.errors[endpoint] += 1

    def snapshot(self) -> dict:
        with self._lock:
            total = self.cache_hits + self.cache_misses
            return {
                "style_usage": dict(self.style_usage),
                "voice_usage": dict(self.voice_usage),
                "cache_hit_rate": round(self.cache_hits / total, 3) if total else None,
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "errors_by_endpoint": dict(self.errors),
            }

    def reset(self):
        with self._lock:
            self.style_usage.clear()
            self.voice_usage.clear()
            self.cache_hits = 0
            self.cache_misses = 0
            self.errors.clear()


stats = Stats()
