"""CH22 Time Series Databases — Example 4: high-cardinality tag-explosion
cost simulator.

Demonstrates the chapter's Section 4.4 concretely: the number of distinct
time series a TSDB must track is the CARTESIAN PRODUCT of each tag's
distinct values, not a sum. This script builds increasingly realistic tag
sets and prints how fast the series count (and an approximated per-series
in-memory index cost) grows, including the classic "customer_id" or
"request_id" high-cardinality-tag mistake.

Run: python 04_high_cardinality_cost_simulator.py
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product


# Prometheus's real per-series memory overhead varies by version and
# workload; this constant is a deliberately simple, documented
# approximation (a few kilobytes per active series for the label set plus
# the in-memory chunk head) used only to make the growth curve concrete,
# not a benchmark result.
APPROX_BYTES_PER_ACTIVE_SERIES = 3_000


@dataclass
class TagSet:
    name: str
    tags: dict[str, list[str]]

    def series_count(self) -> int:
        count = 1
        for values in self.tags.values():
            count *= len(values)
        return count

    def approx_memory_bytes(self) -> int:
        return self.series_count() * APPROX_BYTES_PER_ACTIVE_SERIES


def make_bounded_tag_set() -> TagSet:
    """A well-bounded tag set: every tag has a small, closed set of values
    known in advance (this is the recommended pattern from Section 4.4)."""
    return TagSet(
        name="bounded (region x service x status_code x instance)",
        tags={
            "region": [f"region-{i}" for i in range(4)],
            "service": [f"service-{i}" for i in range(20)],
            "status_code": ["200", "301", "400", "404", "500", "503"],
            "instance": [f"instance-{i}" for i in range(50)],
        },
    )


def make_unbounded_tag_set(bounded: TagSet, unbounded_cardinality: int) -> TagSet:
    """The classic mistake: adding one UNBOUNDED tag (customer_id,
    request_id, a raw email address, a UUID) to an otherwise reasonable tag
    set. The series count multiplies by that tag's full cardinality,
    because every existing combination now also varies by every value of
    the new tag."""
    tags = dict(bounded.tags)
    tags["customer_id"] = [f"cust-{i}" for i in range(unbounded_cardinality)]
    return TagSet(
        name=f"unbounded (+ customer_id x {unbounded_cardinality:,})",
        tags=tags,
    )


def print_report(tag_set: TagSet) -> None:
    series_count = tag_set.series_count()
    memory_bytes = tag_set.approx_memory_bytes()
    memory_mb = memory_bytes / (1024 * 1024)
    print(f"Tag set:            {tag_set.name}")
    for tag_name, values in tag_set.tags.items():
        print(f"  - {tag_name}: {len(values):,} distinct values")
    print(f"  Series count:     {series_count:,}  (cartesian product)")
    print(f"  Approx. memory:   {memory_mb:,.1f} MB "
          f"(at ~{APPROX_BYTES_PER_ACTIVE_SERIES:,} bytes/series)\n")


def show_first_n_series(tag_set: TagSet, n: int = 3) -> None:
    """Materializes the first few concrete series identities so the
    cartesian-product multiplication is visible, not just a count."""
    tag_names = list(tag_set.tags.keys())
    value_lists = [tag_set.tags[name] for name in tag_names]
    print(f"  First {n} concrete series identities:")
    for i, combo in enumerate(product(*value_lists)):
        if i >= n:
            break
        labels = ", ".join(f'{name}="{value}"' for name, value in zip(tag_names, combo))
        print(f"    metric{{{labels}}}")
    print()


def main() -> None:
    print("=== High-cardinality tag-explosion cost simulator ===\n")

    bounded = make_bounded_tag_set()
    print_report(bounded)
    show_first_n_series(bounded)

    for customer_count in (1_000, 100_000, 5_000_000):
        unbounded = make_unbounded_tag_set(bounded, customer_count)
        print_report(unbounded)

    bounded_series = bounded.series_count()
    worst_case = make_unbounded_tag_set(bounded, 5_000_000)
    growth_factor = worst_case.series_count() / bounded_series
    print(
        f"Adding one 5,000,000-value unbounded tag multiplied the series "
        f"count by {growth_factor:,.0f}x — this is the concrete mechanism "
        f"behind Section 4.4's high-cardinality problem: it is always "
        f"multiplicative, never additive, across tags."
    )


if __name__ == "__main__":
    main()
