"""
Cluster-scale rebalancing simulation: online vs. offline, and the cost of
adding/removing nodes under consistent hashing vs. naive modulo hashing.

This extends 01_consistent_hashing_ring.py's single before/after snapshot
into a full multi-step rebalance timeline, and models the two operational
strategies described in Section 4.4:
- Offline rebalance: stop writes, migrate the affected key ranges, resume.
  Simple and safe but incurs a visible write-availability gap.
- Online rebalance: dual-write to the old and new owner for the affected
  key range while a background copy catches up, then cut over and drop the
  old owner -- no availability gap, but requires the dual-write/cutover/
  drain machinery to be correct under concurrent writes.

Run: python 02_rebalancing_simulation.py
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from importlib import import_module

_ring_module = import_module("01_consistent_hashing_ring")
ConsistentHashRing = _ring_module.ConsistentHashRing


@dataclass
class RebalanceEvent:
    step: str
    keys_moved: int
    total_keys: int
    duration_ms: float
    write_unavailable: bool


@dataclass
class RebalanceTimeline:
    events: list[RebalanceEvent] = field(default_factory=list)

    def record(self, event: RebalanceEvent) -> None:
        self.events.append(event)

    def report(self) -> None:
        for event in self.events:
            pct = event.keys_moved / event.total_keys if event.total_keys else 0.0
            mode = "OFFLINE (writes blocked)" if event.write_unavailable else "ONLINE (dual-write)"
            print(
                f"  [{mode:24s}] {event.step:32s} moved={event.keys_moved:5d} "
                f"({pct:5.1%})  took={event.duration_ms:6.1f}ms"
            )


def simulate_offline_rebalance(ring: ConsistentHashRing, keys: list[str], new_node: str) -> RebalanceEvent:
    """Simplification: block writes for the whole migration window."""
    start = time.perf_counter()
    before = {key: ring.get_node(key) for key in keys}
    ring.add_node(new_node)
    after = {key: ring.get_node(key) for key in keys}
    moved_keys = [key for key in keys if before[key] != after[key]]
    # Simulate migration I/O cost: ~0.01ms per moved key.
    time.sleep(len(moved_keys) * 0.00001)
    duration_ms = (time.perf_counter() - start) * 1000
    return RebalanceEvent("add_node (offline)", len(moved_keys), len(keys), duration_ms, True)


def simulate_online_rebalance(ring: ConsistentHashRing, keys: list[str], new_node: str) -> RebalanceEvent:
    """
    Dual-write phase: for the affected keys only, writes would go to both the
    old and new owner while a background copy runs; reads keep serving from
    the old owner until the copy is verified caught-up, then routing cuts
    over atomically. The simulation only measures the affected-key set and
    the (much smaller, since it overlaps steady-state traffic) added latency
    of the dual-write window -- no write-unavailability window at all.
    """
    start = time.perf_counter()
    before = {key: ring.get_node(key) for key in keys}
    ring.add_node(new_node)
    after = {key: ring.get_node(key) for key in keys}
    moved_keys = [key for key in keys if before[key] != after[key]]
    # Dual-write overhead is much cheaper per key than a full offline copy
    # because it overlaps normal request traffic instead of blocking it.
    time.sleep(len(moved_keys) * 0.000002)
    duration_ms = (time.perf_counter() - start) * 1000
    return RebalanceEvent("add_node (online, dual-write)", len(moved_keys), len(keys), duration_ms, False)


def main() -> None:
    keys = [f"key-{i}" for i in range(50_000)]
    timeline = RebalanceTimeline()

    # Cluster starts at 4 nodes, scales out to 7 one node at a time.
    ring = ConsistentHashRing(vnodes_per_node=150)
    for node in ["A", "B", "C", "D"]:
        ring.add_node(node)

    for i, new_node in enumerate(["E", "F", "G"]):
        if i % 2 == 0:
            event = simulate_offline_rebalance(ring, keys, new_node)
        else:
            event = simulate_online_rebalance(ring, keys, new_node)
        timeline.record(event)

    # Scale back in: remove a node, observe how many keys must move back.
    before = {key: ring.get_node(key) for key in keys}
    ring.remove_node("G")
    after = {key: ring.get_node(key) for key in keys}
    moved = sum(1 for key in keys if before[key] != after[key])
    timeline.record(
        RebalanceEvent("remove_node G (online)", moved, len(keys), 0.0, False)
    )

    print(f"Rebalance timeline across {len(keys)} keys, 4 -> 7 -> 6 nodes:")
    timeline.report()

    total_moved = sum(e.keys_moved for e in timeline.events)
    print(
        f"\nTotal key-movement events across the whole timeline: {total_moved} "
        f"(consistent hashing keeps each step close to the 1/N theoretical "
        f"minimum instead of reshuffling the whole keyspace every step)."
    )


if __name__ == "__main__":
    main()
