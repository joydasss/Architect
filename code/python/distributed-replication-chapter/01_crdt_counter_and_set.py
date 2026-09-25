"""CRDT (Conflict-free Replicated Data Type) reference implementations.

Demonstrates two state-based CRDTs (CvRDTs):
  1. GCounter  - a grow-only counter that merges via per-replica max().
  2. ORSet     - an Observed-Remove Set that merges add-wins semantics
                 using per-element unique tags instead of plain booleans.

Both types satisfy the CRDT convergence property: merge is commutative,
associative, and idempotent, so any two replicas that have (eventually)
seen the same set of updates converge to the same value regardless of
the order or number of times those updates were merged.
"""

from __future__ import annotations

import itertools
import uuid
from dataclasses import dataclass, field


class GCounter:
    """Grow-only counter CRDT: each replica only increments its own slot."""

    def __init__(self, replica_id: str) -> None:
        self.replica_id = replica_id
        self._counts: dict[str, int] = {replica_id: 0}

    def increment(self, amount: int = 1) -> None:
        if amount < 0:
            raise ValueError("GCounter only supports non-negative increments")
        self._counts[self.replica_id] = self._counts.get(self.replica_id, 0) + amount

    def value(self) -> int:
        return sum(self._counts.values())

    def merge(self, other: "GCounter") -> None:
        """Merge is a per-replica-slot max(): commutative, associative, idempotent."""
        for replica_id, count in other._counts.items():
            self._counts[replica_id] = max(self._counts.get(replica_id, 0), count)

    def state(self) -> dict[str, int]:
        return dict(self._counts)


@dataclass
class ORSet:
    """Observed-Remove Set CRDT: add-wins conflict resolution.

    Each add() tags the element with a fresh unique id instead of a bare
    boolean, so a concurrent add and remove of the same element resolves
    to "present" (add-wins) rather than silently losing one side's intent.
    """

    replica_id: str
    _adds: dict[str, set[str]] = field(default_factory=dict)   # element -> set of add-tags
    _removes: dict[str, set[str]] = field(default_factory=dict)  # element -> set of removed tags

    def add(self, element: str) -> None:
        tag = f"{self.replica_id}:{uuid.uuid4().hex[:8]}"
        self._adds.setdefault(element, set()).add(tag)

    def remove(self, element: str) -> None:
        # Removing only tombstones the tags currently observed locally.
        # A concurrent add on another replica carries a *new* tag that this
        # remove never observed, so it survives the merge (add-wins).
        observed_tags = self._adds.get(element, set())
        self._removes.setdefault(element, set()).update(observed_tags)

    def contains(self, element: str) -> bool:
        live_tags = self._adds.get(element, set()) - self._removes.get(element, set())
        return len(live_tags) > 0

    def values(self) -> set[str]:
        return {el for el in self._adds if self.contains(el)}

    def merge(self, other: "ORSet") -> None:
        for element, tags in other._adds.items():
            self._adds.setdefault(element, set()).update(tags)
        for element, tags in other._removes.items():
            self._removes.setdefault(element, set()).update(tags)


def _demo_gcounter_converges_regardless_of_merge_order() -> None:
    a = GCounter("replica-a")
    b = GCounter("replica-b")
    c = GCounter("replica-c")

    a.increment(5)   # e.g. 5 page views recorded on replica A
    b.increment(3)   # 3 recorded on replica B while partitioned from A
    c.increment(2)   # 2 recorded on replica C, partitioned from both

    # Merge in one order on node X ...
    x = GCounter("replica-a")
    x._counts = a.state()
    x.merge(b)
    x.merge(c)

    # ... and a different order on node Y.
    y = GCounter("replica-c")
    y._counts = c.state()
    y.merge(a)
    y.merge(b)

    assert x.value() == y.value() == 10, "GCounter must converge regardless of merge order"
    print(f"GCounter converged: total={x.value()} (state={x.state()})")


def _demo_orset_add_wins_under_concurrent_add_remove() -> None:
    replica1 = ORSet("replica-1")
    replica2 = ORSet("replica-2")

    replica1.add("feature-flag:dark-mode")
    replica2.merge(replica1)  # replica-2 observes the add before the partition

    # Network partition happens here. Both replicas keep operating independently.
    replica2.remove("feature-flag:dark-mode")           # replica-2 removes what it saw
    replica1.add("feature-flag:dark-mode")               # replica-1 concurrently re-adds (new tag!)

    # Partition heals; merge in both directions.
    merged_at_1 = ORSet("replica-1")
    merged_at_1._adds, merged_at_1._removes = dict(replica1._adds), dict(replica1._removes)
    merged_at_1.merge(replica2)

    merged_at_2 = ORSet("replica-2")
    merged_at_2._adds, merged_at_2._removes = dict(replica2._adds), dict(replica2._removes)
    merged_at_2.merge(replica1)

    assert merged_at_1.contains("feature-flag:dark-mode")
    assert merged_at_2.contains("feature-flag:dark-mode")
    print("ORSet add-wins: concurrent add survived the concurrent remove on both replicas")


if __name__ == "__main__":
    _demo_gcounter_converges_regardless_of_merge_order()
    _demo_orset_add_wins_under_concurrent_add_remove()
