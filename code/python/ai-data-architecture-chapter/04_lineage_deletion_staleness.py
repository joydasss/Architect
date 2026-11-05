"""Lineage graph deletion impact and staleness arithmetic (standard library).

Run: python 04_lineage_deletion_staleness.py
"""

from collections import deque

# edge: producer -> consumers (derived artifacts)
LINEAGE = {
    "src:doc-123": ["chunk:doc-123#1", "chunk:doc-123#2"],
    "chunk:doc-123#1": ["emb:doc-123#1:v3"],
    "chunk:doc-123#2": ["emb:doc-123#2:v3"],
    "emb:doc-123#1:v3": ["index:kb-prod:v12", "cache:answer-77"],
    "emb:doc-123#2:v3": ["index:kb-prod:v12"],
    "index:kb-prod:v12": ["log:trace-2026-10-01"],
    "src:cust-9": ["row:train-snap-2026-09#4411", "feat:cust-9:online"],
    "row:train-snap-2026-09#4411": ["model:churn-v7"],
}


def impact(root):
    seen, order, q = {root}, [], deque([root])
    while q:
        node = q.popleft()
        for nxt in LINEAGE.get(node, []):
            if nxt not in seen:
                seen.add(nxt)
                order.append(nxt)
                q.append(nxt)
    return order


def staleness(batch_interval_h, pipeline_lag_h, index_swap_h):
    """Worst-case age of a source change when a query reads it."""
    return round(batch_interval_h + pipeline_lag_h + index_swap_h, 2)


if __name__ == "__main__":
    for root in ("src:doc-123", "src:cust-9"):
        print(f"delete {root} -> {len(impact(root))} derived artifacts")
        for n in impact(root):
            kind = n.split(":")[0]
            action = {"chunk": "delete", "emb": "delete vector", "index": "rebuild/tombstone",
                      "cache": "purge", "log": "redact", "row": "exclude from next snapshot",
                      "feat": "delete", "model": "assess retrain"}[kind]
            print(f"   {n:<32} {action}")
    print("worst-case staleness hours (nightly):", staleness(24, 2, 1))
    print("worst-case staleness hours (hourly):", staleness(1, 0.5, 0.25))
    print("worst-case staleness hours (event-driven):", staleness(0, 0.1, 0.05))
