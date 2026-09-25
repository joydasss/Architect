# Example 3 — Quorum Simulation: Why the Minority Side Cannot Commit

Referenced from [CH05_CAP_Theorem.md, Section 10](../../../07_System_Design_and_Distributed_Systems/CH05_CAP_Theorem.md#10-complete-code-examples).

A small, self-contained Python simulation of a 5-node cluster that models
`W+R>N` quorum arithmetic (recapped from
[Replication](../../../06_Databases_and_Storage/CH07_Replication.md#43-quorum-based-replication-dynamo-style)),
injects a partition, and prints exactly the moment each side's write
behavior diverges — a runnable illustration of Section 4.2's proof sketch.

```python
class Cluster:
    """Models N nodes split into two groups by an injected partition."""

    def __init__(self, node_count: int, write_quorum: int):
        self.node_count = node_count
        self.write_quorum = write_quorum
        self.groups: list[set[int]] = [set(range(node_count))]  # no partition initially

    def partition(self, group_a: set[int], group_b: set[int]) -> None:
        """Split the cluster into two groups that cannot exchange messages."""
        assert group_a | group_b == set(range(self.node_count))
        assert not (group_a & group_b)
        self.groups = [group_a, group_b]

    def heal(self) -> None:
        self.groups = [set(range(self.node_count))]

    def attempt_write(self, requesting_group: set[int]) -> bool:
        """A write can only commit if the group it's issued in can reach
        a majority quorum of the WHOLE cluster - not just of itself."""
        return len(requesting_group) >= self.write_quorum


def describe(cluster: Cluster, group: set[int], label: str) -> None:
    ok = cluster.attempt_write(group)
    verdict = "COMMITS (quorum reached)" if ok else "REFUSED (quorum unreachable)"
    print(f"{label} (size={len(group)} of {cluster.node_count}): {verdict}")


if __name__ == "__main__":
    # 5 nodes, majority quorum = 3
    cluster = Cluster(node_count=5, write_quorum=3)

    print("-- Normal operation --")
    describe(cluster, set(range(5)), "Full cluster")

    print("\n-- Partition: 3-node majority vs 2-node minority --")
    majority, minority = {0, 1, 2}, {3, 4}
    cluster.partition(majority, minority)
    describe(cluster, majority, "Majority side")
    describe(cluster, minority, "Minority side")

    print("\n-- Partition heals --")
    cluster.heal()
    describe(cluster, set(range(5)), "Full cluster")
```

**Expected output:**

```
-- Normal operation --
Full cluster (size=5 of 5): COMMITS (quorum reached)

-- Partition: 3-node majority vs 2-node minority --
Majority side (size=3 of 5): COMMITS (quorum reached)
Minority side (size=2 of 5): REFUSED (quorum unreachable)

-- Partition heals --
Full cluster (size=5 of 5): COMMITS (quorum reached)
```

The `attempt_write` method is the entire CP mechanism in miniature: it has
no special-cased "if partitioned, refuse" branch anywhere in it — the
refusal on the minority side falls directly out of comparing the reachable
group's size against the fixed `write_quorum` threshold, exactly as
Section 5 describes for a real Raft-based cluster. Changing
`write_quorum` to `1` and re-running turns this same simulation into an
AP-posture model, where both the 3-node and 2-node groups would commit
independently — reproducing Section 4.4's AP behavior and setting up the
exact conflicting-write scenario Section 5's sequence diagram walks
through.
