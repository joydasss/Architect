"""Retrieval metrics for RAG evaluation (standard library only).

Implements recall@k, precision@k, hit rate, reciprocal rank, average
precision, R-precision, and nDCG with graded relevance, then reproduces the
hand-worked example from CH19 and a small two-system comparison.

Run: python 01_retrieval_metrics.py
"""

import math


def relevant_set(qrels, threshold=1):
    """Doc ids whose grade is at least `threshold` (binary view of graded qrels)."""
    return {d for d, g in qrels.items() if g >= threshold}


def recall_at_k(ranking, qrels, k, threshold=1):
    rel = relevant_set(qrels, threshold)
    if not rel:
        return None  # undefined: caller decides how to treat no-answer queries
    return len(rel & set(ranking[:k])) / len(rel)


def precision_at_k(ranking, qrels, k, threshold=1):
    rel = relevant_set(qrels, threshold)
    return sum(1 for d in ranking[:k] if d in rel) / k


def hit_rate_at_k(ranking, qrels, k, threshold=1):
    rel = relevant_set(qrels, threshold)
    return 1.0 if any(d in rel for d in ranking[:k]) else 0.0


def reciprocal_rank(ranking, qrels, threshold=1):
    rel = relevant_set(qrels, threshold)
    for i, d in enumerate(ranking, start=1):
        if d in rel:
            return 1.0 / i
    return 0.0


def average_precision(ranking, qrels, threshold=1):
    """Mean of precision at each relevant rank, divided by ALL relevant docs."""
    rel = relevant_set(qrels, threshold)
    if not rel:
        return None
    hits, total = 0, 0.0
    for i, d in enumerate(ranking, start=1):
        if d in rel:
            hits += 1
            total += hits / i
    return total / len(rel)


def r_precision(ranking, qrels, threshold=1):
    rel = relevant_set(qrels, threshold)
    r = len(rel)
    if r == 0:
        return None
    return sum(1 for d in ranking[:r] if d in rel) / r


def dcg_at_k(grades, k):
    """Exponential gain (2^g - 1) with log2(rank + 1) discount."""
    return sum((2 ** g - 1) / math.log2(i + 1) for i, g in enumerate(grades[:k], start=1))


def ndcg_at_k(ranking, qrels, k):
    gains = [qrels.get(d, 0) for d in ranking]
    ideal = sorted(qrels.values(), reverse=True)
    idcg = dcg_at_k(ideal, k)
    if idcg == 0:
        return None
    return dcg_at_k(gains, k) / idcg


def mean_ignoring_none(values):
    vals = [v for v in values if v is not None]
    return sum(vals) / len(vals) if vals else float("nan")


def worked_example():
    # One query. Graded judgments: 3 = fully answers, 2 = strong, 1 = partial.
    qrels = {"d1": 3, "d3": 2, "d6": 1, "d12": 2}  # d12 is never retrieved
    ranking = [f"d{i}" for i in range(1, 11)]  # system returns d1..d10 in order
    print("== Worked example (one query, 4 relevant docs, d12 never retrieved) ==")
    print(f"recall@5      = {recall_at_k(ranking, qrels, 5):.4f}")
    print(f"precision@5   = {precision_at_k(ranking, qrels, 5):.4f}")
    print(f"recall@10     = {recall_at_k(ranking, qrels, 10):.4f}")
    print(f"precision@10  = {precision_at_k(ranking, qrels, 10):.4f}")
    print(f"hit rate@5    = {hit_rate_at_k(ranking, qrels, 5):.4f}")
    print(f"RR            = {reciprocal_rank(ranking, qrels):.4f}")
    print(f"AP            = {average_precision(ranking, qrels):.4f}")
    print(f"R-precision   = {r_precision(ranking, qrels):.4f}")
    print(f"DCG@10        = {dcg_at_k([qrels.get(d, 0) for d in ranking], 10):.4f}")
    print(f"IDCG@10       = {dcg_at_k(sorted(qrels.values(), reverse=True), 10):.4f}")
    print(f"nDCG@10       = {ndcg_at_k(ranking, qrels, 10):.4f}")
    # Same list with a different top: relevant doc moved from rank 1 to rank 4
    worse = ["d2", "d4", "d5", "d1", "d3", "d6", "d7", "d8", "d9", "d10"]
    print(f"nDCG@10 when d1 drops to rank 4 = {ndcg_at_k(worse, qrels, 10):.4f}")
    print(f"RR      when d1 drops to rank 4 = {reciprocal_rank(worse, qrels):.4f}")


def two_system_comparison():
    # Six queries. Query q6 has no relevant document (unanswerable): scored None
    # for recall/AP/nDCG and handled separately as an abstention test.
    qrels = {
        "q1": {"a": 2, "b": 1},
        "q2": {"c": 3},
        "q3": {"d": 1, "e": 1, "f": 1},
        "q4": {"g": 2, "h": 2},
        "q5": {"i": 1},
        "q6": {},
    }
    sys_a = {
        "q1": ["a", "x", "b", "y", "z"],
        "q2": ["x", "y", "c", "z", "w"],
        "q3": ["d", "x", "e", "y", "f"],
        "q4": ["x", "y", "z", "g", "w"],
        "q5": ["x", "y", "z", "w", "v"],
        "q6": ["x", "y", "z", "w", "v"],
    }
    sys_b = {
        "q1": ["x", "a", "y", "z", "b"],
        "q2": ["c", "x", "y", "z", "w"],
        "q3": ["x", "d", "y", "e", "z"],
        "q4": ["g", "h", "x", "y", "z"],
        "q5": ["x", "y", "i", "z", "w"],
        "q6": ["x", "y", "z", "w", "v"],
    }
    print()
    print("== Two systems, six queries (q6 has no relevant doc) ==")
    for name, run in (("A", sys_a), ("B", sys_b)):
        r5 = [recall_at_k(run[q], qrels[q], 5) for q in qrels]
        p5 = [precision_at_k(run[q], qrels[q], 5) for q in qrels if qrels[q]]
        rr = [reciprocal_rank(run[q], qrels[q]) for q in qrels if qrels[q]]
        ap = [average_precision(run[q], qrels[q]) for q in qrels]
        nd = [ndcg_at_k(run[q], qrels[q], 5) for q in qrels]
        print(
            f"system {name}: recall@5={mean_ignoring_none(r5):.3f} "
            f"P@5={mean_ignoring_none(p5):.3f} MRR={mean_ignoring_none(rr):.3f} "
            f"MAP={mean_ignoring_none(ap):.3f} nDCG@5={mean_ignoring_none(nd):.3f}"
        )


if __name__ == "__main__":
    worked_example()
    two_system_comparison()
