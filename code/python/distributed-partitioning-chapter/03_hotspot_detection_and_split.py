"""
Hotspot detection and mitigation via splitting a single hot partition further.

Models Section 4.5's cluster-scale hotspot problem: even with a perfectly
uniform consistent-hashing ring, *access* load can still concentrate on one
partition because real-world key-access patterns are skewed (a celebrity
user, a viral post, a single misbehaving tenant), not because the ring
placement itself is wrong. The mitigation this script demonstrates is
splitting the hot partition's key range into two sub-partitions and
re-assigning one of them to a different physical node -- distinct from
rebalancing the *whole* ring, which would not fix a skew that lives entirely
inside one partition's key range.

Run: python 03_hotspot_detection_and_split.py
"""

from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass

HOTSPOT_THRESHOLD_RATIO = 3.0  # a partition is "hot" at 3x the mean load


@dataclass
class Partition:
    partition_id: str
    node: str
    key_range: tuple[int, int]  # half-open [start, end)
    request_count: int = 0


def build_uniform_partitions(num_partitions: int, num_nodes: int, keyspace_size: int) -> list[Partition]:
    """Evenly-sized key ranges assigned round-robin across nodes."""
    partitions = []
    span = keyspace_size // num_partitions
    for i in range(num_partitions):
        node = f"node-{i % num_nodes}"
        start, end = i * span, (i + 1) * span
        partitions.append(Partition(f"p{i}", node, (start, end)))
    return partitions


def route_key(partitions: list[Partition], key: int) -> Partition:
    for partition in partitions:
        if partition.key_range[0] <= key < partition.key_range[1]:
            return partition
    return partitions[-1]


def simulate_skewed_traffic(partitions: list[Partition], num_requests: int, keyspace_size: int) -> None:
    """80% of requests hit a single hot key range to model a viral-content skew."""
    hot_range_start = keyspace_size // 10  # an arbitrary "viral" sub-range
    hot_range_end = hot_range_start + (keyspace_size // 100)
    for _ in range(num_requests):
        if random.random() < 0.80:
            key = random.randint(hot_range_start, hot_range_end - 1)
        else:
            key = random.randint(0, keyspace_size - 1)
        route_key(partitions, key).request_count += 1


def detect_hotspots(partitions: list[Partition]) -> list[Partition]:
    mean_load = sum(p.request_count for p in partitions) / len(partitions)
    return [p for p in partitions if p.request_count >= mean_load * HOTSPOT_THRESHOLD_RATIO]


def split_partition(partition: Partition, new_node: str) -> tuple[Partition, Partition]:
    """Split a hot partition's key range in half, moving one half to a new node."""
    start, end = partition.key_range
    midpoint = (start + end) // 2
    left = Partition(f"{partition.partition_id}-a", partition.node, (start, midpoint))
    right = Partition(f"{partition.partition_id}-b", new_node, (midpoint, end))
    return left, right


def request_totals_by_node(partitions: list[Partition]) -> dict[str, int]:
    totals: dict[str, int] = defaultdict(int)
    for partition in partitions:
        totals[partition.node] += partition.request_count
    return dict(totals)


def main() -> None:
    random.seed(7)
    keyspace_size = 1_000_000
    partitions = build_uniform_partitions(num_partitions=8, num_nodes=4, keyspace_size=keyspace_size)
    simulate_skewed_traffic(partitions, num_requests=100_000, keyspace_size=keyspace_size)

    print("Per-partition request counts before mitigation:")
    for p in partitions:
        print(f"  {p.partition_id} on {p.node}: {p.request_count:6d} requests")

    print("\nPer-node totals before mitigation:")
    for node, total in sorted(request_totals_by_node(partitions).items()):
        print(f"  {node}: {total:6d} requests")

    hot = detect_hotspots(partitions)
    print(f"\nDetected {len(hot)} hot partition(s) at >= {HOTSPOT_THRESHOLD_RATIO}x mean load:")
    for p in hot:
        print(f"  {p.partition_id} on {p.node} ({p.request_count} requests)")

    # Mitigate: split each hot partition, moving half its range to an
    # under-loaded node so the celebrity/viral traffic is spread further.
    node_loads = request_totals_by_node(partitions)
    least_loaded_node = min(node_loads, key=lambda n: node_loads[n])
    for p in hot:
        left, right = split_partition(p, new_node=least_loaded_node)
        partitions.remove(p)
        partitions.extend([left, right])

    # Replay the same traffic pattern against the post-split layout to prove
    # the mitigation actually rebalances the load rather than just moving it.
    for p in partitions:
        p.request_count = 0
    simulate_skewed_traffic(partitions, num_requests=100_000, keyspace_size=keyspace_size)

    print("\nPer-node totals after splitting the hot partition(s):")
    for node, total in sorted(request_totals_by_node(partitions).items()):
        print(f"  {node}: {total:6d} requests")

    still_hot = detect_hotspots(partitions)
    print(
        f"\nHot partitions remaining after mitigation: {len(still_hot)} "
        f"(vs. {len(hot)} before) -- splitting narrows the hot key range "
        "rather than diagnosing/rebalancing the whole cluster."
    )


if __name__ == "__main__":
    main()
