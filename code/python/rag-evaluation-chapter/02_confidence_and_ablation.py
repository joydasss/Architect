"""Confidence intervals, sample sizing, paired bootstrap and a 2x2 ablation.

Standard library only. Run: python 02_confidence_and_ablation.py
"""

import math
import random


def wilson(successes, n, z=1.96):
    """Wilson score interval for a proportion."""
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return centre - half, centre + half


def sample_size_for_margin(margin, p=0.5, z=1.96):
    return math.ceil(z * z * p * (1 - p) / (margin * margin))


def exact_mcnemar_p(b, c):
    """Two-sided exact binomial p-value on discordant pairs (b vs c)."""
    n = b + c
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def intervals_section():
    print("== Wilson 95% intervals for an observed 80% pass rate ==")
    for n in (50, 100, 400, 1000):
        lo, hi = wilson(int(0.8 * n), n)
        print(f"n={n:5d}  [{lo:.3f}, {hi:.3f}]  half-width={(hi - lo) / 2:.3f}")
    print()
    print("== Queries needed for a +/- margin at 95% (worst case p=0.5) ==")
    for m in (0.10, 0.05, 0.03, 0.02):
        print(f"margin {m:.2f}: n={sample_size_for_margin(m)}")


def paired_section():
    # 200 queries scored pass/fail on faithfulness for config A and config B.
    both_ok, both_bad, only_b, only_a = 130, 46, 18, 6
    pairs = (
        [(1, 1)] * both_ok + [(0, 0)] * both_bad + [(0, 1)] * only_b + [(1, 0)] * only_a
    )
    n = len(pairs)
    a_rate = sum(a for a, _ in pairs) / n
    b_rate = sum(b for _, b in pairs) / n
    print()
    print("== Paired comparison, 200 queries ==")
    print(f"A pass rate={a_rate:.3f}  B pass rate={b_rate:.3f}  diff={b_rate - a_rate:+.3f}")

    # Unpaired (wrong here, shown for contrast): two independent Wilson-style SEs.
    se_unpaired = math.sqrt(a_rate * (1 - a_rate) / n + b_rate * (1 - b_rate) / n)
    # Paired SE from the discordant counts.
    d = only_b - only_a
    var_paired = (only_b + only_a - d * d / n) / (n * n)
    se_paired = math.sqrt(var_paired)
    diff = b_rate - a_rate
    print(f"unpaired SE={se_unpaired:.4f}  95% CI [{diff - 1.96 * se_unpaired:+.3f}, {diff + 1.96 * se_unpaired:+.3f}]")
    print(f"paired   SE={se_paired:.4f}  95% CI [{diff - 1.96 * se_paired:+.3f}, {diff + 1.96 * se_paired:+.3f}]")
    print(f"exact McNemar p (b={only_b}, c={only_a}) = {exact_mcnemar_p(only_b, only_a):.4f}")

    rng = random.Random(7)
    diffs = []
    for _ in range(10000):
        sample = [pairs[rng.randrange(n)] for _ in range(n)]
        diffs.append(sum(b - a for a, b in sample) / n)
    diffs.sort()
    lo, hi = diffs[249], diffs[9749]
    print(f"paired bootstrap (10000 resamples, seed 7) 95% CI [{lo:+.3f}, {hi:+.3f}]")


def factorial_section():
    # Recall@10 on a fixed set for each cell of a 2x2 ablation (illustrative).
    cells = {
        ("small", "no_rerank"): 0.62,
        ("small", "rerank"): 0.74,
        ("large", "no_rerank"): 0.70,
        ("large", "rerank"): 0.73,
    }
    print()
    print("== 2x2 ablation: chunk size x reranker (illustrative recall@10) ==")
    for k, v in cells.items():
        print(f"{k[0]:5s} {k[1]:9s} {v:.2f}")
    rerank_gain_small = cells[("small", "rerank")] - cells[("small", "no_rerank")]
    rerank_gain_large = cells[("large", "rerank")] - cells[("large", "no_rerank")]
    chunk_gain_norerank = cells[("large", "no_rerank")] - cells[("small", "no_rerank")]
    chunk_gain_rerank = cells[("large", "rerank")] - cells[("small", "rerank")]
    print(f"reranker gain with small chunks = {rerank_gain_small:+.2f}")
    print(f"reranker gain with large chunks = {rerank_gain_large:+.2f}")
    print(f"large-chunk gain without reranker = {chunk_gain_norerank:+.2f}")
    print(f"large-chunk gain with reranker    = {chunk_gain_rerank:+.2f}")
    inter = rerank_gain_large - rerank_gain_small
    print(f"interaction (difference of differences) = {inter:+.2f}")
    one_at_a_time = cells[("large", "no_rerank")] - cells[("small", "no_rerank")]
    print(f"one-factor-at-a-time from baseline would say chunk effect = {one_at_a_time:+.2f}")


if __name__ == "__main__":
    intervals_section()
    paired_section()
    factorial_section()
