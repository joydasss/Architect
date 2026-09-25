"""
Join algorithm cost simulator.

Companion to 06_Databases_and_Storage/CH04_Query_Optimizers.md, Section 10.

Estimates the relative I/O cost of nested loop join, hash join, and
sort-merge join for two relations, given their cardinalities and whether an
index exists on the join key -- the same inputs a real cost-based optimizer
weighs when picking a join algorithm (Sections 4.6-4.8). This is a teaching
model, not a real optimizer: production optimizers also account for CPU
cost, memory pressure/spilling, and parallelism, but the *shape* of the
trade-off below is faithful to how PostgreSQL/MySQL/SQL Server reason about
join algorithm choice.
"""

from dataclasses import dataclass
from math import log2


@dataclass
class Relation:
    name: str
    row_count: int
    rows_per_page: int = 100  # how many rows fit in one I/O page


def pages(relation: Relation) -> int:
    return max(1, -(-relation.row_count // relation.rows_per_page))  # ceil div


def nested_loop_cost(outer: Relation, inner: Relation, inner_has_index: bool) -> float:
    """Cost model: outer table scanned once; inner probed once per outer ROW
    (index probe) or once per outer PAGE re-scanning the inner table fully
    (no index). This is why index selectivity on the inner side matters so
    much more for nested loop than for hash/merge join."""
    outer_pages = pages(outer)
    if inner_has_index:
        # One cheap index probe (~2-4 page reads for a B-tree) per outer row.
        index_probe_cost = 3
        return outer_pages + outer.row_count * index_probe_cost
    inner_pages = pages(inner)
    return outer_pages + outer.row_count * inner_pages


def hash_join_cost(build: Relation, probe: Relation, memory_pages: int) -> float:
    """Cost model: build a hash table over the smaller relation (build side),
    then stream the larger relation (probe side) through it once. Cheap when
    the build side fits in memory; if it doesn't, the optimizer must spill to
    disk in partitioned batches (grace hash join), which this model
    approximates with a partitioning-and-rehash penalty."""
    build_pages = pages(build)
    probe_pages = pages(probe)
    base_cost = build_pages + probe_pages
    if build_pages <= memory_pages:
        return base_cost  # single in-memory hash table, no spill
    # Doesn't fit: partition both sides to disk and rejoin partition by
    # partition -- roughly triples the I/O (write partitions, read them back
    # for build, read them back for probe).
    return base_cost * 3


def sort_merge_join_cost(left: Relation, right: Relation, left_sorted: bool, right_sorted: bool) -> float:
    """Cost model: sorting an unsorted relation of P pages costs roughly
    P * log2(P) (external merge sort); once both sides are sorted, the merge
    itself is a single linear pass over both."""
    def sort_cost(relation: Relation, already_sorted: bool) -> float:
        p = pages(relation)
        if already_sorted:
            return 0.0
        return p * max(1.0, log2(max(2, p)))

    left_pages, right_pages = pages(left), pages(right)
    return (
        sort_cost(left, left_sorted)
        + sort_cost(right, right_sorted)
        + left_pages
        + right_pages
    )


def choose_join_algorithm(
    outer: Relation,
    inner: Relation,
    *,
    inner_has_index: bool,
    memory_pages: int,
    outer_sorted: bool = False,
    inner_sorted: bool = False,
) -> None:
    build, probe = (inner, outer) if inner.row_count <= outer.row_count else (outer, inner)

    nl_cost = nested_loop_cost(outer, inner, inner_has_index)
    hj_cost = hash_join_cost(build, probe, memory_pages)
    smj_cost = sort_merge_join_cost(outer, inner, outer_sorted, inner_sorted)

    print(f"\n--- {outer.name} JOIN {inner.name} "
          f"({outer.row_count:,} rows vs {inner.row_count:,} rows) ---")
    print(f"  Nested Loop  estimated cost: {nl_cost:,.0f}"
          f"{'  (index-assisted)' if inner_has_index else '  (no usable index)'}")
    print(f"  Hash Join    estimated cost: {hj_cost:,.0f}"
          f"{'' if pages(build) <= memory_pages else '  (spills to disk, grace partitioning)'}")
    print(f"  Sort-Merge   estimated cost: {smj_cost:,.0f}"
          f"{'  (inputs already sorted)' if outer_sorted and inner_sorted else ''}")

    cheapest = min(
        ("Nested Loop", nl_cost),
        ("Hash Join", hj_cost),
        ("Sort-Merge Join", smj_cost),
        key=lambda pair: pair[1],
    )
    print(f"  => Optimizer would choose: {cheapest[0]}")


if __name__ == "__main__":
    small_lookup_table = Relation("customers", row_count=50_000)
    large_fact_table = Relation("orders", row_count=1_000_000)

    print("Scenario A: small dimension table, no useful index on the join key,")
    print("plenty of work_mem/buffer pool available.")
    choose_join_algorithm(
        large_fact_table, small_lookup_table,
        inner_has_index=False, memory_pages=2_000,
    )

    print("\nScenario B: same tables, but a B-tree index exists on "
          "orders.customer_id and only a handful of outer rows qualify "
          "after a selective WHERE filter (simulated via a smaller outer).")
    filtered_orders = Relation("orders_filtered", row_count=2_000)
    choose_join_algorithm(
        filtered_orders, small_lookup_table,
        inner_has_index=True, memory_pages=2_000,
    )

    print("\nScenario C: two large fact tables, neither pre-sorted, and a")
    print("memory budget too small to hold either side's hash table --")
    print("this is where sort-merge join often overtakes hash join.")
    huge_shipments = Relation("shipments", row_count=5_000_000)
    choose_join_algorithm(
        large_fact_table, huge_shipments,
        inner_has_index=False, memory_pages=500,
    )
