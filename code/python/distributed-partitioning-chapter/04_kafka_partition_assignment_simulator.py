"""
Kafka-style topic-partition assignment and consumer-group rebalancing,
simulated from scratch (no live broker required).

Models Section 4.6's non-database partitioning domain: a topic is split into
a fixed number of partitions at creation time (partition COUNT does not
auto-rebalance the way a consistent-hashing ring does -- growing partition
count is a deliberate, manual operation because it changes key-to-partition
mapping for keyed messages). Consumers in the same consumer group each own
a disjoint subset of the topic's partitions; when a consumer joins or
leaves, the group coordinator triggers a *rebalance* that reassigns
partition ownership across the remaining/new consumer set.

Two classic assignment strategies are modeled:
- Range assignor: partitions are assigned in contiguous ranges per consumer,
  simple but can leave a small remainder unevenly distributed.
- Round-robin assignor: partitions are dealt out one at a time in rotation,
  producing a more even split at the cost of losing any range locality.

Run: python 04_kafka_partition_assignment_simulator.py
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ConsumerGroupState:
    consumers: list[str] = field(default_factory=list)
    assignment: dict[str, list[int]] = field(default_factory=dict)  # consumer -> partitions
    generation: int = 0


def range_assign(partitions: list[int], consumers: list[str]) -> dict[str, list[int]]:
    """Split the partition list into contiguous chunks, one per consumer."""
    assignment: dict[str, list[int]] = {c: [] for c in consumers}
    if not consumers:
        return assignment
    base, remainder = divmod(len(partitions), len(consumers))
    cursor = 0
    for i, consumer in enumerate(consumers):
        chunk_size = base + (1 if i < remainder else 0)
        assignment[consumer] = partitions[cursor:cursor + chunk_size]
        cursor += chunk_size
    return assignment


def round_robin_assign(partitions: list[int], consumers: list[str]) -> dict[str, list[int]]:
    """Deal partitions out one at a time, rotating through the consumer list."""
    assignment: dict[str, list[int]] = {c: [] for c in consumers}
    if not consumers:
        return assignment
    for i, partition in enumerate(partitions):
        consumer = consumers[i % len(consumers)]
        assignment[consumer].append(partition)
    return assignment


def rebalance(
    state: ConsumerGroupState,
    partitions: list[int],
    strategy: str,
    joining: str | None = None,
    leaving: str | None = None,
) -> None:
    """
    A rebalance is triggered any time group membership changes. Real Kafka
    uses a group coordinator broker and a join/sync-group protocol with a
    rebalance timeout and (in modern "cooperative sticky" assignors) tries to
    avoid revoking partitions a consumer already owns unless truly necessary;
    this simulation models the simpler "stop-the-world" eager rebalance,
    where every partition is reassigned from scratch on every membership
    change, to make the mechanism explicit.
    """
    if joining:
        state.consumers.append(joining)
    if leaving:
        state.consumers.remove(leaving)
        state.assignment.pop(leaving, None)

    assigner = range_assign if strategy == "range" else round_robin_assign
    state.assignment = assigner(partitions, sorted(state.consumers))
    state.generation += 1


def print_assignment(state: ConsumerGroupState, label: str) -> None:
    print(f"\n{label} (generation {state.generation}):")
    for consumer, owned in sorted(state.assignment.items()):
        print(f"  {consumer}: partitions {owned}")


def main() -> None:
    # A topic created with 12 partitions -- fixed at creation time; growing
    # this count later is a manual operation with keyed-message re-mapping
    # consequences, unlike a consistent-hashing ring's automatic rebalance.
    partitions = list(range(12))

    print("=== Range assignor ===")
    state = ConsumerGroupState()
    rebalance(state, partitions, "range", joining="consumer-1")
    print_assignment(state, "3 partitions? no -- single consumer owns all 12")
    rebalance(state, partitions, "range", joining="consumer-2")
    rebalance(state, partitions, "range", joining="consumer-3")
    print_assignment(state, "After 2 more consumers join (3 total)")
    rebalance(state, partitions, "range", joining="consumer-4")
    print_assignment(state, "After a 4th consumer joins (12 / 4 = 3 each, even)")
    rebalance(state, partitions, "range", leaving="consumer-2")
    print_assignment(state, "After consumer-2 leaves (stop-the-world eager rebalance)")

    print("\n=== Round-robin assignor, same membership timeline ===")
    rr_state = ConsumerGroupState()
    rebalance(rr_state, partitions, "round_robin", joining="consumer-1")
    rebalance(rr_state, partitions, "round_robin", joining="consumer-2")
    rebalance(rr_state, partitions, "round_robin", joining="consumer-3")
    rebalance(rr_state, partitions, "round_robin", joining="consumer-4")
    print_assignment(rr_state, "After 4 consumers join")
    rebalance(rr_state, partitions, "round_robin", leaving="consumer-2")
    print_assignment(rr_state, "After consumer-2 leaves")

    # Uneven partition count vs. consumer count: 12 partitions, 5 consumers.
    print("\n=== Uneven split: 12 partitions, 5 consumers (range assignor) ===")
    uneven_state = ConsumerGroupState()
    for c in ["consumer-1", "consumer-2", "consumer-3", "consumer-4", "consumer-5"]:
        rebalance(uneven_state, partitions, "range", joining=c)
    print_assignment(uneven_state, "Range assignor leaves an idle consumer")
    for consumer, owned in uneven_state.assignment.items():
        if not owned:
            print(f"  NOTE: {consumer} owns zero partitions -- provisioned but idle, "
                  f"a direct consequence of partition count not dividing evenly.")


if __name__ == "__main__":
    main()
