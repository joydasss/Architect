"""Paired bootstrap comparison of two candidate models on one evaluation set.

Standard library only. The per-item scores are SYNTHETIC: they are generated
from fixed success probabilities with a shared item-difficulty effect, so the
two candidates are correlated the way real candidates are on the same items.
Replace `make_synthetic_scores` with your own graded results (1 = pass,
0 = fail, or a rubric score scaled to 0..1).

Prints: accuracy of each candidate, the paired difference, a 95 percent
bootstrap interval, the one-sided probability that B is not better than A, and
the unpaired interval for contrast.
"""
import random


def make_synthetic_scores(n, seed=7):
    rng = random.Random(seed)
    a, b = [], []
    for _ in range(n):
        difficulty = rng.random()  # shared by both candidates
        # A candidate passes when the item is easier than its ability, with a
        # little independent noise. B has slightly higher ability than A.
        a.append(1 if difficulty + rng.gauss(0, 0.08) < 0.72 else 0)
        b.append(1 if difficulty + rng.gauss(0, 0.08) < 0.78 else 0)
    return a, b


def mean(xs):
    return sum(xs) / len(xs)


def paired_bootstrap(a, b, resamples=10000, seed=11):
    rng = random.Random(seed)
    n = len(a)
    diffs = []
    for _ in range(resamples):
        idx = [rng.randrange(n) for _ in range(n)]
        diffs.append(mean([b[i] for i in idx]) - mean([a[i] for i in idx]))
    diffs.sort()
    lo = diffs[int(0.025 * resamples)]
    hi = diffs[int(0.975 * resamples) - 1]
    p_not_better = sum(1 for d in diffs if d <= 0) / resamples
    return lo, hi, p_not_better


def unpaired_bootstrap(a, b, resamples=10000, seed=13):
    rng = random.Random(seed)
    n = len(a)
    diffs = []
    for _ in range(resamples):
        ia = [rng.randrange(n) for _ in range(n)]
        ib = [rng.randrange(n) for _ in range(n)]
        diffs.append(mean([b[i] for i in ib]) - mean([a[i] for i in ia]))
    diffs.sort()
    return diffs[int(0.025 * resamples)], diffs[int(0.975 * resamples) - 1]


def main():
    n = 300
    a, b = make_synthetic_scores(n)
    diff = mean(b) - mean(a)
    lo, hi, p = paired_bootstrap(a, b)
    ulo, uhi = unpaired_bootstrap(a, b)
    only_a = sum(1 for x, y in zip(a, b) if x == 1 and y == 0)
    only_b = sum(1 for x, y in zip(a, b) if x == 0 and y == 1)
    print(f"items                : {n}")
    print(f"candidate A accuracy : {mean(a):.3f}")
    print(f"candidate B accuracy : {mean(b):.3f}")
    print(f"discordant items     : A-only {only_a}, B-only {only_b}")
    print(f"paired diff (B - A)  : {diff:+.3f}")
    print(f"paired 95% interval  : [{lo:+.3f}, {hi:+.3f}]")
    print(f"P(B not better than A): {p:.4f}")
    print(f"unpaired 95% interval: [{ulo:+.3f}, {uhi:+.3f}]")
    verdict = "B better" if lo > 0 else ("A better" if hi < 0 else "inconclusive")
    print(f"verdict              : {verdict}")


if __name__ == "__main__":
    main()
