"""Cache-aside (lazy-loading) pattern in front of a database.

Demonstrates the read path (miss -> load -> populate -> hit) and the write
path (write to the database, then invalidate/delete the cache entry rather
than update it in place) discussed in CH09_Caching.md Section 4.2.

Run directly: python 01_cache_aside.py
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional


class FakeRedis:
    """Minimal stand-in for a Redis-like client: get/set(ex=)/delete."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[str, Optional[float]]] = {}

    def get(self, key: str) -> Optional[str]:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if expires_at is not None and time.monotonic() >= expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: str, ex: Optional[int] = None) -> None:
        expires_at = time.monotonic() + ex if ex is not None else None
        self._store[key] = (value, expires_at)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)


@dataclass
class FakeDatabase:
    """Simulated database with an artificial read/write latency."""

    rows: dict[int, str]
    read_latency_s: float = 0.05

    def get_product_name(self, product_id: int) -> str:
        time.sleep(self.read_latency_s)  # simulate a real query round trip
        return self.rows[product_id]

    def update_product_name(self, product_id: int, name: str) -> None:
        time.sleep(self.read_latency_s)
        self.rows[product_id] = name


CACHE_TTL_SECONDS = 30


def get_product_name_cache_aside(cache: FakeRedis, db: FakeDatabase, product_id: int) -> str:
    """Cache-aside read: application checks cache first, falls back to DB on miss."""
    key = f"product:{product_id}:name"

    cached = cache.get(key)
    if cached is not None:
        return cached  # cache hit — no database round trip

    # Cache miss: the application itself owns the fallback and populate step.
    value = db.get_product_name(product_id)
    cache.set(key, value, ex=CACHE_TTL_SECONDS)
    return value


def update_product_name_cache_aside(
    cache: FakeRedis, db: FakeDatabase, product_id: int, new_name: str
) -> None:
    """Cache-aside write: write the database first, then invalidate (not update) the cache.

    Deleting rather than overwriting the cache entry avoids a race where a
    slower write's stale value could overwrite a faster write's fresh value
    in the cache after both have already committed to the database.
    """
    key = f"product:{product_id}:name"
    db.update_product_name(product_id, new_name)
    cache.delete(key)


def demo() -> None:
    cache = FakeRedis()
    db = FakeDatabase(rows={101: "Wireless Mouse"})

    start = time.perf_counter()
    name = get_product_name_cache_aside(cache, db, 101)
    miss_latency_ms = (time.perf_counter() - start) * 1000
    print(f"First read (cache miss): {name!r} in {miss_latency_ms:.1f} ms")

    start = time.perf_counter()
    name = get_product_name_cache_aside(cache, db, 101)
    hit_latency_ms = (time.perf_counter() - start) * 1000
    print(f"Second read (cache hit): {name!r} in {hit_latency_ms:.1f} ms")

    update_product_name_cache_aside(cache, db, 101, "Wireless Mouse (2024 Edition)")
    print("Wrote new name to DB and invalidated cache entry.")

    start = time.perf_counter()
    name = get_product_name_cache_aside(cache, db, 101)
    reload_latency_ms = (time.perf_counter() - start) * 1000
    print(f"Read after invalidation (cache miss again): {name!r} in {reload_latency_ms:.1f} ms")


if __name__ == "__main__":
    demo()
