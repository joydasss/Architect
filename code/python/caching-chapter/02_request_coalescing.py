"""Cache stampede (thundering herd) and request-coalescing mitigation.

CH09_Caching.md Section 4.8: when a hot key expires, N concurrent readers
can all miss the cache simultaneously and hammer the database with N
redundant queries at once. This script demonstrates the failure with a
naive cache-aside reader, then fixes it with a per-key mutex ("singleflight"
style) so only one thread performs the database fetch while the rest wait
for and reuse its result.

Run directly: python 02_request_coalescing.py
"""

from __future__ import annotations

import threading
import time
from typing import Optional


class SimpleCache:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[str]:
        with self._lock:
            return self._store.get(key)

    def set(self, key: str, value: str) -> None:
        with self._lock:
            self._store[key] = value

    def clear(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)


class CountingDatabase:
    """Counts how many times the expensive query actually ran."""

    def __init__(self, latency_s: float = 0.2) -> None:
        self.latency_s = latency_s
        self.query_count = 0
        self._count_lock = threading.Lock()

    def expensive_query(self, key: str) -> str:
        with self._count_lock:
            self.query_count += 1
        time.sleep(self.latency_s)
        return f"value-for-{key}"


def naive_read(cache: SimpleCache, db: CountingDatabase, key: str) -> str:
    """No stampede protection: every miss independently queries the database."""
    value = cache.get(key)
    if value is not None:
        return value
    value = db.expensive_query(key)
    cache.set(key, value)
    return value


class CoalescingReader:
    """Ensures only one in-flight database fetch per key at any moment.

    Concurrent callers for the same key during a miss all block on the same
    per-key lock and then re-check the cache, so exactly one of them performs
    the database query and the rest reuse its result — the "singleflight"
    pattern (named after Go's golang.org/x/sync/singleflight package).
    """

    def __init__(self, cache: SimpleCache, db: CountingDatabase) -> None:
        self._cache = cache
        self._db = db
        self._key_locks: dict[str, threading.Lock] = {}
        self._key_locks_guard = threading.Lock()

    def _lock_for(self, key: str) -> threading.Lock:
        with self._key_locks_guard:
            if key not in self._key_locks:
                self._key_locks[key] = threading.Lock()
            return self._key_locks[key]

    def read(self, key: str) -> str:
        value = self._cache.get(key)
        if value is not None:
            return value

        key_lock = self._lock_for(key)
        with key_lock:
            # Re-check: another thread may have already populated the cache
            # while we were waiting for this lock.
            value = self._cache.get(key)
            if value is not None:
                return value
            value = self._db.expensive_query(key)
            self._cache.set(key, value)
            return value


def run_concurrent_misses(read_fn, thread_count: int = 20) -> None:
    threads = [threading.Thread(target=read_fn) for _ in range(thread_count)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def demo() -> None:
    hot_key = "product:101:price"

    naive_cache = SimpleCache()
    naive_db = CountingDatabase()
    run_concurrent_misses(lambda: naive_read(naive_cache, naive_db, hot_key))
    print(f"Naive cache-aside under 20 concurrent misses: {naive_db.query_count} DB queries fired")

    coalesced_cache = SimpleCache()
    coalesced_db = CountingDatabase()
    reader = CoalescingReader(coalesced_cache, coalesced_db)
    run_concurrent_misses(lambda: reader.read(hot_key))
    print(f"Coalescing reader under 20 concurrent misses: {coalesced_db.query_count} DB query fired")


if __name__ == "__main__":
    demo()
