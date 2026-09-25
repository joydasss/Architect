"""Least Recently Used (LRU) eviction implemented from first principles.

CH09_Caching.md Section 4.9 describes LRU as a doubly-linked list plus a
hash map for O(1) get/put with O(1) eviction of the coldest entry. Python's
`OrderedDict.move_to_end` is used here specifically because it is backed by
that same doubly-linked-list-plus-dict structure internally, so this stays
a faithful illustration of the mechanism rather than hiding it behind a
generic container.

Run directly: python 03_lru_cache.py
"""

from __future__ import annotations

from collections import OrderedDict
from typing import Any, Optional


class LRUCache:
    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._data: "OrderedDict[Any, Any]" = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def get(self, key: Any) -> Optional[Any]:
        if key not in self._data:
            self.misses += 1
            return None
        self.hits += 1
        # Move to the most-recently-used end of the ordering.
        self._data.move_to_end(key, last=True)
        return self._data[key]

    def put(self, key: Any, value: Any) -> None:
        if key in self._data:
            self._data.move_to_end(key, last=True)
        self._data[key] = value
        if len(self._data) > self.capacity:
            # popitem(last=False) removes the least-recently-used entry —
            # the one at the front of the ordering.
            evicted_key, _ = self._data.popitem(last=False)
            self.evictions += 1
            print(f"  evicted {evicted_key!r} (least recently used)")


def demo() -> None:
    cache = LRUCache(capacity=3)

    for key in ["A", "B", "C"]:
        cache.put(key, f"value-{key}")
    print(f"After inserting A, B, C: order = {list(cache._data.keys())}")

    cache.get("A")  # touching A makes it most-recently-used
    print(f"After touching A: order = {list(cache._data.keys())}")

    cache.put("D", "value-D")  # capacity exceeded -> evict least-recently-used
    print(f"After inserting D (capacity=3): order = {list(cache._data.keys())}")

    print(f"hits={cache.hits} misses={cache.misses} evictions={cache.evictions}")


if __name__ == "__main__":
    demo()
