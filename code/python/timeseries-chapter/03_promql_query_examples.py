"""CH22 Time Series Databases — Example 3: PromQL query examples and a
minimal Prometheus HTTP API client.

This demonstrates Prometheus's pull-based query surface (chapter Section
4.7): PromQL selects and transforms time series already scraped and stored
in Prometheus's local TSDB, via a stateless HTTP `/api/v1/query` (instant)
or `/api/v1/query_range` (range) call. The network call is wrapped so this
file is import-safe (`python -m py_compile`) and runnable in a sandbox with
no live Prometheus server: `run_query()` only executes the HTTP request when
a `base_url` is supplied and reachable, otherwise it prints the query it
would have run.

Run: python 03_promql_query_examples.py [http://localhost:9090]
"""
from __future__ import annotations

import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Representative PromQL queries, each annotated with what it demonstrates.
# ---------------------------------------------------------------------------

ANNOTATED_QUERIES: list[tuple[str, str]] = [
    (
        # Instant vector: current value of every series matching the metric
        # name and tag ("label" in Prometheus terminology) selector.
        'up{job="node_exporter"}',
        "Instant vector: is each scrape target currently up (1) or down (0)? "
        "The {job=\"node_exporter\"} selector is Prometheus's label-matching "
        "syntax over the tag dimension described in Section 4.1.",
    ),
    (
        # rate() requires a range vector (the [5m] suffix) and computes the
        # per-second average rate of increase of a monotonically increasing
        # counter over that window — the standard way to turn a raw counter
        # into a meaningful rate without being fooled by counter resets.
        'rate(http_requests_total{status="500"}[5m])',
        "Range-vector rate(): per-second growth rate of a counter metric "
        "over a trailing 5-minute window, correctly handling counter resets "
        "(e.g. a process restart) by treating a decrease as a reset.",
    ),
    (
        # Aggregation across the cardinality dimension: sum by (job) collapses
        # every series that differs only in, say, instance/pod, down to one
        # series per job — directly relevant to Section 4.4's high-cardinality
        # discussion: aggregation is the standard way to make a
        # high-cardinality raw series usable in a dashboard.
        "sum by (job) (rate(http_requests_total[5m]))",
        "Aggregation collapsing per-instance cardinality down to per-job "
        "series — the query-time answer to Section 4.4's tag-explosion "
        "problem: aggregate away the dimension you don't need for this view.",
    ),
    (
        # histogram_quantile requires a histogram-type metric with
        # _bucket/_sum/_count series; this computes the p99 latency estimate
        # by interpolating within the bucket boundaries.
        "histogram_quantile(0.99, "
        "sum by (le) (rate(http_request_duration_seconds_bucket[5m])))",
        "p99 latency estimate from a Prometheus histogram metric's bucket "
        "series, illustrating why Prometheus ships pre-bucketed histograms "
        "client-side rather than computing quantiles over raw samples.",
    ),
    (
        # Alerting-style boolean comparison: this is exactly the expression
        # form used inside a Prometheus alerting rule.
        "avg_over_time(node_memory_MemAvailable_bytes[15m]) "
        "/ node_memory_MemTotal_bytes < 0.10",
        "Alerting-style boolean expression: fires when 15-minute average "
        "available memory drops below 10% of total — the query IS the "
        "alert condition, no separate alerting DSL.",
    ),
]


@dataclass
class PrometheusClient:
    """Minimal read-only client for Prometheus's HTTP query API."""

    base_url: str
    timeout_seconds: float = 5.0

    def instant_query(self, promql: str) -> dict:
        url = f"{self.base_url}/api/v1/query?" + urllib.parse.urlencode(
            {"query": promql, "time": str(time.time())}
        )
        return self._get(url)

    def range_query(
        self, promql: str, start: float, end: float, step_seconds: int
    ) -> dict:
        url = f"{self.base_url}/api/v1/query_range?" + urllib.parse.urlencode(
            {
                "query": promql,
                "start": str(start),
                "end": str(end),
                "step": str(step_seconds),
            }
        )
        return self._get(url)

    def _get(self, url: str) -> dict:
        request = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            import json

            return json.loads(response.read().decode("utf-8"))


def run_query(base_url: str | None, promql: str, annotation: str) -> None:
    print(f"PromQL:  {promql}")
    print(f"Purpose: {annotation}")
    if not base_url:
        print("(no --base-url given; not executing against a live server)\n")
        return
    try:
        client = PrometheusClient(base_url)
        result = client.instant_query(promql)
        status = result.get("status", "unknown")
        series_count = len(result.get("data", {}).get("result", []))
        print(f"Result:  status={status}, series_returned={series_count}\n")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"Result:  query not executed (Prometheus unreachable: {exc})\n")


def main() -> None:
    base_url = sys.argv[1] if len(sys.argv) > 1 else None
    print("=== PromQL query examples against Prometheus's pull-based TSDB ===\n")
    for promql, annotation in ANNOTATED_QUERIES:
        run_query(base_url, promql, annotation)


if __name__ == "__main__":
    main()
