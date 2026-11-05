"""Staged RAG evaluation: probability chain and a diagnosis of a quality drop.

Standard library only. Run: python 04_staged_diagnosis.py
"""


def chain_section():
    stages = [
        ("parsing preserved the evidence", 0.97),
        ("chunking kept the answer intact", 0.95),
        ("retrieval found a relevant chunk", 0.90),
        ("reranking kept it in the context", 0.93),
        ("context assembly kept it and its source", 0.97),
        ("generation used it faithfully and completely", 0.92),
        ("citations point to the supporting span", 0.96),
    ]
    print("== Probability chain (illustrative, independence assumed) ==")
    prod = 1.0
    for name, p in stages:
        prod *= p
        print(f"{name:48s} p={p:.2f}  cumulative={prod:.4f}")
    # Marginal value of fixing each stage to 0.99
    print()
    print("Cumulative success if one stage is raised to 0.99:")
    for i, (name, p) in enumerate(stages):
        alt = 1.0
        for j, (_, q) in enumerate(stages):
            alt *= 0.99 if i == j else q
        print(f"  fix {name:46s} -> {alt:.4f} (gain {alt - prod:+.4f})")


def diagnosis_section():
    # Per-stage metrics before and after a release, 400 answerable queries.
    before = {
        "recall@10": 0.88, "ndcg@10": 0.71, "context_precision": 0.62,
        "faithfulness": 0.93, "answer_correct": 0.80, "citation_support": 0.94,
    }
    after = {
        "recall@10": 0.87, "ndcg@10": 0.70, "context_precision": 0.61,
        "faithfulness": 0.92, "answer_correct": 0.70, "citation_support": 0.93,
    }
    print()
    print("== Staged metrics before and after the release (400 queries) ==")
    for k in before:
        print(f"{k:18s} {before[k]:.2f} -> {after[k]:.2f}  ({after[k] - before[k]:+.2f})")

    # Per-segment answer_correct: segment -> (n, before_correct, after_correct)
    seg = {
        "policy": (160, 136, 134),
        "pricing_tables": (80, 66, 36),
        "troubleshooting": (100, 76, 74),
        "legal_pdf": (60, 42, 36),
    }
    print()
    print("answer_correct by segment (n, before, after)")
    tot_b = tot_a = 0
    for name, (n, b, a) in seg.items():
        tot_b += b
        tot_a += a
        print(f"{name:16s} n={n:3d} {b / n:.3f} -> {a / n:.3f}  ({(a - b) / n:+.3f})")
    n_all = sum(v[0] for v in seg.values())
    print(f"overall          n={n_all:3d} {tot_b / n_all:.3f} -> {tot_a / n_all:.3f}")

    # Table-content queries: oracle-context test isolates generation from retrieval
    print()
    print("Oracle-context test on the 80 pricing_tables queries")
    print("  gold chunk supplied directly to the generator: correct 66/80 before, 35/80 after")
    print("  retrieval is not the cause. Cause: parser change flattened table rows.")


if __name__ == "__main__":
    chain_section()
    diagnosis_section()
