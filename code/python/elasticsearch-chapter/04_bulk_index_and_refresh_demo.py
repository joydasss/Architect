"""
Section 4.7 companion example: bulk-indexes a batch of documents and
demonstrates the near-real-time visibility gap between indexing and
searchability (refresh interval + translog, Section 4.7 of
CH20_ElasticSearch.md).

Requires: pip install elasticsearch
Assumes a local ElasticSearch instance reachable at http://localhost:9200.
"""

import time

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

INDEX_NAME = "nrt-demo"


def build_bulk_actions(count: int):
    """Yield bulk index actions - the standard high-throughput ingestion
    pattern (Section 9), batching many operations into one _bulk request
    rather than one HTTP round trip per document."""
    for i in range(count):
        yield {
            "_index": INDEX_NAME,
            "_source": {"sequence": i, "message": f"log line {i}"},
        }


def demonstrate_refresh_gap(client: Elasticsearch) -> None:
    if client.indices.exists(index=INDEX_NAME):
        client.indices.delete(index=INDEX_NAME)
    # Explicit refresh_interval of 30s so the visibility gap is obvious
    # rather than hidden by the 1s default (Section 4.7).
    client.indices.create(
        index=INDEX_NAME,
        body={"settings": {"refresh_interval": "30s"}},
    )

    success_count, _ = bulk(client, build_bulk_actions(1000))
    print(f"Bulk-indexed {success_count} documents (not yet refreshed).")

    # Query immediately: with a 30s refresh interval, these documents are
    # very unlikely to be searchable yet - this is expected NRT behavior,
    # not a bug (the mistake Section 17 warns against).
    immediate = client.count(index=INDEX_NAME)
    print(f"Visible immediately after bulk index: {immediate['count']} docs")

    # Force a refresh explicitly rather than waiting up to 30s - the
    # refresh=wait_for pattern Section 4.7 recommends for callers that
    # genuinely need immediate post-write visibility (e.g. this demo,
    # or a test suite asserting search results right after indexing).
    client.indices.refresh(index=INDEX_NAME)
    after_refresh = client.count(index=INDEX_NAME)
    print(f"Visible after explicit refresh: {after_refresh['count']} docs")


if __name__ == "__main__":
    es = Elasticsearch("http://localhost:9200")
    start = time.monotonic()
    demonstrate_refresh_gap(es)
    print(f"Completed in {time.monotonic() - start:.2f}s")
