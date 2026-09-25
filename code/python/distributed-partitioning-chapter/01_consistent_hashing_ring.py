"""
Consistent hashing ring with virtual nodes (vnodes), built from scratch.

Demonstrates the canonical mechanism this chapter teaches in Section 4.2-4.3:
- Keys and nodes are hashed onto the same circular numeric space (the ring).
- Each physical node owns many vnodes (typically 100-200) scattered around
  the ring, so load is spread evenly instead of each node owning one large
  contiguous arc.
- Adding/removing a node only remaps the keys that fall between the
  departing/arriving vnodes and their neighbors -- roughly 1/N of the
  keyspace -- instead of the ~(N-1)/N a naive modulo scheme would remap.

Run: python 01_consistent_hashing_ring.py
"""

from __future__ import annotations

import bisect
import hashlib
from collections import defaultdict


def _hash(value: str) -> int:
    """Stable 64-bit hash used to place both nodes and keys on the ring."""
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big")


class ConsistentHashRing:
    """A consistent-hashing ring with virtual nodes per physical node."""

    def __init__(self, vnodes_per_node: int = 150) -> None:
        self.vnodes_per_node = vnodes_per_node
        self._ring: dict[int, str] = {}          # ring position -> physical node
        self._sorted_positions: list[int] = []    # kept sorted for binary search
        self._nodes: set[str] = set()

    def add_node(self, node: str) -> None:
        if node in self._nodes:
            raise ValueError(f"node {node!r} already present")
        self._nodes.add(node)
        for i in range(self.vnodes_per_node):
            position = _hash(f"{node}#vnode-{i}")
            self._ring[position] = node
            bisect.insort(self._sorted_positions, position)

    def remove_node(self, node: str) -> None:
        if node not in self._nodes:
            raise ValueError(f"node {node!r} not present")
        self._nodes.discard(node)
        for i in range(self.vnodes_per_node):
            position = _hash(f"{node}#vnode-{i}")
            del self._ring[position]
            index = bisect.bisect_left(self._sorted_positions, position)
            self._sorted_positions.pop(index)

    def get_node(self, key: str) -> str:
        """Walk clockwise from the key's ring position to the first vnode."""
        if not self._sorted_positions:
            raise RuntimeError("ring is empty -- no nodes added")
        position = _hash(key)
        index = bisect.bisect_right(self._sorted_positions, position)
        if index == len(self._sorted_positions):
            index = 0  # wrap around the ring
        return self._ring[self._sorted_positions[index]]

    def distribution(self, keys: list[str]) -> dict[str, int]:
        counts: dict[str, int] = defaultdict(int)
        for key in keys:
            counts[self.get_node(key)] += 1
        return dict(counts)


def naive_modulo_owner(node_list: list[str], key: str) -> str:
    """The naive alternative: key -> hash(key) % len(nodes)."""
    return node_list[_hash(key) % len(node_list)]


def main() -> None:
    keys = [f"key-{i}" for i in range(20_000)]

    # --- Load distribution across 5 nodes, with and without vnodes ---
    ring_with_vnodes = ConsistentHashRing(vnodes_per_node=150)
    for node in ["A", "B", "C", "D", "E"]:
        ring_with_vnodes.add_node(node)
    dist_with_vnodes = ring_with_vnodes.distribution(keys)

    ring_single_vnode = ConsistentHashRing(vnodes_per_node=1)
    for node in ["A", "B", "C", "D", "E"]:
        ring_single_vnode.add_node(node)
    dist_single_vnode = ring_single_vnode.distribution(keys)

    print("Distribution across 5 nodes, 150 vnodes/node:")
    for node, count in sorted(dist_with_vnodes.items()):
        print(f"  {node}: {count:5d} keys ({count / len(keys):.1%})")

    print("\nDistribution across 5 nodes, 1 vnode/node (no load balancing):")
    for node, count in sorted(dist_single_vnode.items()):
        print(f"  {node}: {count:5d} keys ({count / len(keys):.1%})")

    # --- Remap cost when scaling from 5 to 6 nodes: consistent hashing ---
    before = {key: ring_with_vnodes.get_node(key) for key in keys}
    ring_with_vnodes.add_node("F")
    after = {key: ring_with_vnodes.get_node(key) for key in keys}
    moved = sum(1 for key in keys if before[key] != after[key])
    print(
        f"\nConsistent hashing, 5 -> 6 nodes: {moved}/{len(keys)} keys moved "
        f"({moved / len(keys):.1%}, theoretical minimum is 1/6 = 16.7%)"
    )

    # --- Remap cost when scaling from 5 to 6 nodes: naive modulo ---
    nodes_5 = ["A", "B", "C", "D", "E"]
    nodes_6 = ["A", "B", "C", "D", "E", "F"]
    before_mod = {key: naive_modulo_owner(nodes_5, key) for key in keys}
    after_mod = {key: naive_modulo_owner(nodes_6, key) for key in keys}
    moved_mod = sum(1 for key in keys if before_mod[key] != after_mod[key])
    print(
        f"Naive modulo hashing, 5 -> 6 nodes: {moved_mod}/{len(keys)} keys "
        f"moved ({moved_mod / len(keys):.1%}, theoretical worst case is "
        f"(N-1)/N = 83.3%)"
    )


if __name__ == "__main__":
    main()
