"""
02_consistency_level_quorum_demo.py

Self-contained in-memory simulation of Cassandra's tunable per-query
consistency levels and the N/R/W quorum overlap rule -- no live cluster or
`cassandra-driver` dependency required, so it runs anywhere with plain
Python. See CH18_Cassandra.md Sections 4.1-4.2 for the mechanism this
demonstrates: how ONE, QUORUM, ALL, and LOCAL_QUORUM map onto how many of a
row's N replicas must acknowledge a read or write before the coordinator
replies to the client.

Run with: python 02_consistency_level_quorum_demo.py
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum


class ConsistencyLevel(Enum):
    ONE = "ONE"
    TWO = "TWO"
    QUORUM = "QUORUM"
    ALL = "ALL"
    LOCAL_QUORUM = "LOCAL_QUORUM"


@dataclass
class Replica:
    node_id: str
    datacenter: str
    # value, write-timestamp pairs; None means the replica never got the write
    value: object | None = None
    write_ts: int = 0
    reachable: bool = True


@dataclass
class ReplicaSet:
    """The N replicas owning one partition, per the replication factor."""

    replicas: list[Replica] = field(default_factory=list)

    @property
    def n(self) -> int:
        return len(self.replicas)

    def replicas_in_dc(self, dc: str) -> list[Replica]:
        return [r for r in self.replicas if r.datacenter == dc]


def required_acks(cl: ConsistencyLevel, replica_set: ReplicaSet, local_dc: str) -> int:
    """Translate a named consistency level into a concrete replica count --
    the W (for writes) or R (for reads) in the N/R/W quorum formula."""
    n = replica_set.n
    if cl is ConsistencyLevel.ONE:
        return 1
    if cl is ConsistencyLevel.TWO:
        return 2
    if cl is ConsistencyLevel.ALL:
        return n
    if cl is ConsistencyLevel.QUORUM:
        # Cluster-wide majority across every datacenter's replicas.
        return n // 2 + 1
    if cl is ConsistencyLevel.LOCAL_QUORUM:
        # Majority of only the local datacenter's replicas -- cross-DC
        # network round trips never sit on this request's critical path.
        local_n = len(replica_set.replicas_in_dc(local_dc))
        return local_n // 2 + 1
    raise ValueError(f"unsupported consistency level: {cl}")


def coordinate_write(
    replica_set: ReplicaSet, cl: ConsistencyLevel, value: object, ts: int, local_dc: str
) -> bool:
    """Simulate a coordinator fanning a write out to all N replicas and
    waiting only for the CL-required number of acknowledgments. Replicas
    that are unreachable at write time would instead receive a hint via
    hinted handoff (CH18_Cassandra.md Section 4.4) -- omitted here to keep
    this script focused purely on the quorum-overlap arithmetic."""
    acks = 0
    needed = required_acks(cl, replica_set, local_dc)
    for r in replica_set.replicas:
        if r.reachable:
            r.value = value
            r.write_ts = ts
            acks += 1
    return acks >= needed


def coordinate_read(
    replica_set: ReplicaSet, cl: ConsistencyLevel, local_dc: str
) -> tuple[object | None, bool]:
    """Simulate a coordinator querying CL-required replicas and returning
    the value with the highest write-timestamp (last-write-wins). Returns
    (value, saw_conflicting_versions) -- the second flag models what would
    trigger a foreground read repair (Section 4.4) in real Cassandra."""
    needed = required_acks(cl, replica_set, local_dc)
    reachable = [r for r in replica_set.replicas if r.reachable]
    sampled = reachable[:needed]
    if len(sampled) < needed:
        raise RuntimeError(
            f"cannot satisfy {cl.value}: needed {needed} reachable replicas, "
            f"found {len(sampled)} (this is the failure mode Section 4.2 "
            "calls an UnavailableException)"
        )
    versions = {(r.value, r.write_ts) for r in sampled}
    winner = max(sampled, key=lambda r: r.write_ts)
    return winner.value, len(versions) > 1


def demo_overlap_guarantee() -> None:
    """N=3, W=QUORUM(2), R=QUORUM(2): W+R=4 > N=3, so every read quorum is
    mathematically guaranteed to overlap the write quorum on at least one
    replica -- the correctness rule underlying tunable consistency."""
    print("=== W=QUORUM, R=QUORUM (safe: W+R > N) ===")
    rs = ReplicaSet(
        replicas=[
            Replica("node-1", "dc1"),
            Replica("node-2", "dc1"),
            Replica("node-3", "dc1"),
        ]
    )
    rs.replicas[1].reachable = False  # node-2 is briefly down during the write
    ok = coordinate_write(rs, ConsistencyLevel.QUORUM, "order-status=SHIPPED", ts=100, local_dc="dc1")
    print(f"write acknowledged at QUORUM: {ok}")
    rs.replicas[1].reachable = True  # node-2 recovers before the read (still stale)
    value, saw_conflict = coordinate_read(rs, ConsistencyLevel.QUORUM, local_dc="dc1")
    print(f"QUORUM read returned: {value!r}, saw stale replica in quorum: {saw_conflict}")


def demo_unsafe_configuration() -> None:
    """N=3, W=ONE, R=ONE: W+R=2 <= N=3, so a read can land entirely on
    replicas the write never reached -- a stale read, by design of the
    weaker consistency levels, not a bug."""
    print("\n=== W=ONE, R=ONE (unsafe: W+R <= N, stale read possible) ===")
    rs = ReplicaSet(
        replicas=[
            Replica("node-1", "dc1"),
            Replica("node-2", "dc1"),
            Replica("node-3", "dc1"),
        ]
    )
    coordinate_write(rs, ConsistencyLevel.ONE, "order-status=SHIPPED", ts=200, local_dc="dc1")
    written_to = [r.node_id for r in rs.replicas if r.value is not None]
    print(f"CL.ONE write landed only on: {written_to}")
    # A subsequent CL.ONE read is free to pick any replica at random,
    # including one the write never touched.
    random.shuffle(rs.replicas)
    value, _ = coordinate_read(rs, ConsistencyLevel.ONE, local_dc="dc1")
    print(f"CL.ONE read returned: {value!r} (may be None -- stale)")


def demo_local_quorum_multi_dc() -> None:
    """LOCAL_QUORUM (Section 4.2): majority of the LOCAL datacenter's
    replicas only. A remote-DC outage does not block local reads/writes,
    at the cost of not being globally strongly consistent across DCs."""
    print("\n=== LOCAL_QUORUM across two datacenters ===")
    rs = ReplicaSet(
        replicas=[
            Replica("dc1-a", "dc1"),
            Replica("dc1-b", "dc1"),
            Replica("dc1-c", "dc1"),
            Replica("dc2-a", "dc2", reachable=False),
            Replica("dc2-b", "dc2", reachable=False),
            Replica("dc2-c", "dc2", reachable=False),
        ]
    )
    ok = coordinate_write(rs, ConsistencyLevel.LOCAL_QUORUM, "inventory=42", ts=300, local_dc="dc1")
    print(f"LOCAL_QUORUM write succeeded despite dc2 being fully unreachable: {ok}")


if __name__ == "__main__":
    demo_overlap_guarantee()
    demo_unsafe_configuration()
    demo_local_quorum_multi_dc()
