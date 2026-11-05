"""Batch prediction: point-in-time join, idempotent rerun, atomic publish.

Standard library only. Demonstrates three ideas from the chapter:
1. A naive "latest value" feature join leaks future information into a backfill.
2. A point-in-time (as-of) join uses only values known at the event time.
3. A run keyed by (snapshot, model version) is idempotent: rerunning it
   produces byte-identical output, and publication swaps a pointer atomically.
"""
import bisect
import hashlib
import json

# Feature history per customer: (valid_from_day, avg_spend_30d)
HISTORY = {
    "c1": [(1, 20.0), (10, 25.0), (20, 90.0)],
    "c2": [(1, 50.0), (15, 55.0)],
}
# Scoring events: (customer, event_day)
EVENTS = [("c1", 12), ("c1", 25), ("c2", 5), ("c2", 16)]


def latest_value(cust):
    return HISTORY[cust][-1][1]


def as_of_value(cust, day):
    rows = HISTORY[cust]
    days = [d for d, _ in rows]
    i = bisect.bisect_right(days, day) - 1
    return rows[i][1] if i >= 0 else None


def model(x):
    """Toy model v7: risk = min(1, x / 100)."""
    return min(1.0, x / 100.0)


def run(snapshot_id, model_version, use_as_of, store):
    run_key = f"{snapshot_id}|{model_version}|{'asof' if use_as_of else 'latest'}"
    if run_key in store["runs"]:
        return store["runs"][run_key], "reused (idempotent)"
    rows = []
    for cust, day in EVENTS:
        x = as_of_value(cust, day) if use_as_of else latest_value(cust)
        rows.append({"key": f"{cust}:{day}", "feature": x, "score": round(model(x), 3)})
    rows.sort(key=lambda r: r["key"])
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()[:12]
    store["runs"][run_key] = {"rows": rows, "digest": digest}
    return store["runs"][run_key], "computed"


def publish(store, run_key_result):
    # Atomic publish: consumers read store["current"]; one pointer swap.
    store["current"] = run_key_result["digest"]


store = {"runs": {}, "current": None}
naive, how1 = run("snap-2026-10-01", "v7", False, store)
pit, how2 = run("snap-2026-10-01", "v7", True, store)
again, how3 = run("snap-2026-10-01", "v7", True, store)

print("event        naive_score  pit_score")
for a, b in zip(naive["rows"], pit["rows"]):
    flag = "  <-- leakage" if a["score"] != b["score"] else ""
    print(f"{a['key']:<12} {a['score']:<12} {b['score']:<10}{flag}")
print("naive:", how1, naive["digest"])
print("pit  :", how2, pit["digest"])
print("rerun:", how3, again["digest"], "identical:", again["digest"] == pit["digest"])
publish(store, pit)
print("published pointer:", store["current"])
