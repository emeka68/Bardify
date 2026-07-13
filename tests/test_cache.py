"""Unit tests for the TTLCache."""

import time

from cache import TTLCache, make_key


def test_set_and_get_round_trip():
    cache = TTLCache(ttl_seconds=60)
    cache.set("a", {"value": 1})
    assert cache.get("a") == {"value": 1}


def test_missing_key_returns_none():
    cache = TTLCache(ttl_seconds=60)
    assert cache.get("missing") is None


def test_expired_entry_returns_none():
    cache = TTLCache(ttl_seconds=0.05)
    cache.set("a", "value")
    time.sleep(0.1)
    assert cache.get("a") is None


def test_max_entries_evicts_oldest():
    cache = TTLCache(ttl_seconds=60, max_entries=2)
    cache.set("a", 1)
    time.sleep(0.01)
    cache.set("b", 2)
    time.sleep(0.01)
    cache.set("c", 3)  # should evict "a"

    assert cache.get("a") is None
    assert cache.get("b") == 2
    assert cache.get("c") == 3
    assert len(cache) == 2


def test_clear_empties_cache():
    cache = TTLCache(ttl_seconds=60)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.clear()
    assert len(cache) == 0
    assert cache.get("a") is None


def test_make_key_is_stable_and_order_sensitive():
    assert make_key("a", "b") == make_key("a", "b")
    assert make_key("a", "b") != make_key("b", "a")
    assert make_key("a", "b") != make_key("ab")
