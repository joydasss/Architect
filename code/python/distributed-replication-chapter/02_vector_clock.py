"""Vector clock implementation for causality tracking across replicas.

A vector clock is a map from replica-id to a local logical counter. Comparing
two vector clocks tells you whether one event *causally happened-before*
another, happened-after, or is *concurrent* with it (neither side observed
the other) — exactly the information a leaderless/multi-leader replicated
store needs to detect write-write conflicts that a single Lamport scalar
timestamp cannot distinguish from true causal ordering.
"""

from __future__ import annotations

from enum import Enum


class ClockOrder(Enum):
    BEFORE = "happened-before"
    AFTER = "happened-after"
    EQUAL = "equal"
    CONCURRENT = "concurrent"  # neither observed the other -> real conflict


class VectorClock:
    def __init__(self, replica_id: str) -> None:
        self.replica_id = replica_id
        self.counters: dict[str, int] = {}

    def tick(self) -> "VectorClock":
        """Increment this replica's own slot before a local write; returns self."""
        self.counters[self.replica_id] = self.counters.get(self.replica_id, 0) + 1
        return self

    def merge_after_receive(self, other: "VectorClock") -> None:
        """On receiving a replicated write, take the element-wise max, then tick."""
        all_replicas = set(self.counters) | set(other.counters)
        for replica_id in all_replicas:
            self.counters[replica_id] = max(
                self.counters.get(replica_id, 0), other.counters.get(replica_id, 0)
            )
        self.tick()

    def snapshot(self) -> dict[str, int]:
        return dict(self.counters)

    @staticmethod
    def compare(left: "VectorClock", right: "VectorClock") -> ClockOrder:
        replicas = set(left.counters) | set(right.counters)
        left_leq_right = all(left.counters.get(r, 0) <= right.counters.get(r, 0) for r in replicas)
        right_leq_left = all(right.counters.get(r, 0) <= left.counters.get(r, 0) for r in replicas)

        if left_leq_right and right_leq_left:
            return ClockOrder.EQUAL
        if left_leq_right:
            return ClockOrder.BEFORE
        if right_leq_left:
            return ClockOrder.AFTER
        return ClockOrder.CONCURRENT


def _demo_linear_history_is_ordered() -> None:
    """Write on replica A, replicate to B, write again on B -> strictly ordered."""
    a = VectorClock("A").tick()          # A: {A:1}  -- shopping-cart write "add item X"
    b = VectorClock("B")
    b.merge_after_receive(a)             # B: {A:1, B:1} -- B receives + acks A's write

    order = VectorClock.compare(a, b)
    print(f"Linear history: A={a.snapshot()} vs B={b.snapshot()} -> {order.value}")
    assert order == ClockOrder.BEFORE


def _demo_concurrent_writes_are_detected_as_a_conflict() -> None:
    """Two replicas both accept a write before either sees the other's -> concurrent."""
    shared_origin = VectorClock("A").tick()   # {A:1}, both replicas start from this base

    replica_a = VectorClock("A")
    replica_a.counters = shared_origin.snapshot()
    replica_a.tick()                          # {A:2} -- e.g. "set shipping address to Home"

    replica_b = VectorClock("B")
    replica_b.counters = shared_origin.snapshot()
    replica_b.tick()                          # {A:1, B:1} -- e.g. "set shipping address to Work"

    order = VectorClock.compare(replica_a, replica_b)
    print(f"Concurrent writes: A={replica_a.snapshot()} vs B={replica_b.snapshot()} -> {order.value}")
    assert order == ClockOrder.CONCURRENT, "Application must run its conflict-resolution policy here"


if __name__ == "__main__":
    _demo_linear_history_is_ordered()
    _demo_concurrent_writes_are_detected_as_a_conflict()
