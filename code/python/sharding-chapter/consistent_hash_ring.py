"""Consistent-hashing ring with virtual nodes for shard routing.

Demonstrates the core data structure referenced in CH06_Sharding.md
Section 4.5/4.6: a sorted ring of virtual-node hash positions mapped back to
physical shards, so adding/removing a shard only remaps the slice of keys
between two ring positions instead of ~(N-1)/N of all keys (the hash-mod
catastrophe this ring exists to avoid).
"""

from __future__ import annotations

import bisect
import hashlib
from collections import defaultdict
from typing import Dict, List


def _hash(key: str) -> int:
    """Stable 64-bit hash position on the ring (independent of Python's salted hash())."""
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big")


class ConsistentHashRing:
    """Maps arbitrary keys to shards using virtual nodes for load smoothing.

    Each physical shard is placed at `virtual_nodes` positions on the ring.
    More virtual nodes -> better load balance across shards, at the cost of
    more ring entries to search (O(log N) either way, N = shards * vnodes).
    """

    def __init__(self, virtual_nodes: int = 150) -> None:
        self.virtual_nodes = virtual_nodes
        self._ring: Dict[int, str] = {}
        self._sorted_positions: List[int] = []
        self._shards: set[str] = set()

    def add_shard(self, shard_id: str) -> None:
        if shard_id in self._shards:
            return
        self._shards.add(shard_id)
        for replica in range(self.virtual_nodes):
            position = _hash(f"{shard_id}#{replica}")
            self._ring[position] = shard_id
            bisect.insort(self._sorted_positions, position)

    def remove_shard(self, shard_id: str) -> None:
        if shard_id not in self._shards:
            return
        self._shards.discard(shard_id)
        for replica in range(self.virtual_nodes):
            position = _hash(f"{shard_id}#{replica}")
            del self._ring[position]
            idx = bisect.bisect_left(self._sorted_positions, position)
            del self._sorted_positions[idx]

    def get_shard(self, key: str) -> str:
        if not self._sorted_positions:
            raise RuntimeError("Ring has no shards registered")
        position = _hash(key)
        idx = bisect.bisect(self._sorted_positions, position)
        if idx == len(self._sorted_positions):
            idx = 0  # wrap around the ring
        return self._ring[self._sorted_positions[idx]]

    def key_distribution(self, keys: List[str]) -> Dict[str, int]:
        """Utility used to verify load-balance quality before/after a topology change."""
        counts: Dict[str, int] = defaultdict(int)
        for key in keys:
            counts[self.get_shard(key)] += 1
        return dict(counts)


def demo_minimal_remap_on_scale_out() -> None:
    """Shows that adding a shard only remaps ~1/N of keys, not ~(N-1)/N."""
    ring = ConsistentHashRing(virtual_nodes=150)
    for shard in ("shard-a", "shard-b", "shard-c"):
        ring.add_shard(shard)

    sample_keys = [f"customer-{i}" for i in range(20_000)]
    before = {key: ring.get_shard(key) for key in sample_keys}

    ring.add_shard("shard-d")  # scale-out event
    after = {key: ring.get_shard(key) for key in sample_keys}

    remapped = sum(1 for key in sample_keys if before[key] != after[key])
    fraction = remapped / len(sample_keys)
    print(f"Keys remapped after adding a 4th shard: {remapped}/{len(sample_keys)} "
          f"({fraction:.1%}) -- naive key % N would remap ~75% of keys")


if __name__ == "__main__":
    demo_minimal_remap_on_scale_out()
