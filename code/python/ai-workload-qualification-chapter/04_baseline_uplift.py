"""Measure uplift over baselines on a paired evaluation set.

Compares three systems on the same cases: the current process, a simple
heuristic, and a candidate model. Reports accuracy, a paired bootstrap 95%
interval for uplift over the best baseline, and the sample size needed to
detect a given uplift. Data are synthetic. Standard library only.

Run: python 04_baseline_uplift.py
"""
import math
import random


def make_cases(n, seed=3):
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        hard = rng.random() < 0.35
        # probability each system is right depends on case difficulty
        p_cur = 0.72 if not hard else 0.55
        p_heur = 0.78 if not hard else 0.50
        p_model = 0.88 if not hard else 0.68
        rows.append((rng.random() < p_cur, rng.random() < p_heur, rng.random() < p_model))
    return rows


def acc(rows, k):
    return sum(r[k] for r in rows) / len(rows)


def boot_diff(rows, a, b, reps=4000, seed=5):
    rng = random.Random(seed)
    n = len(rows)
    diffs = []
    for _ in range(reps):
        s = [rows[rng.randrange(n)] for _ in range(n)]
        diffs.append(acc(s, a) - acc(s, b))
    diffs.sort()
    return diffs[int(0.025 * reps)], diffs[int(0.975 * reps)]


def sample_size(p1, p2, z_a=1.96, z_b=0.8416):
    """Per-arm n for two proportions, two-sided alpha 0.05, power 0.80."""
    pbar = (p1 + p2) / 2
    num = (z_a * math.sqrt(2 * pbar * (1 - pbar))
           + z_b * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return math.ceil(num / (p1 - p2) ** 2)


if __name__ == "__main__":
    for n in (150, 600):
        rows = make_cases(n)
        names = ["current process", "simple heuristic", "candidate model"]
        accs = [acc(rows, k) for k in range(3)]
        best_base = 0 if accs[0] >= accs[1] else 1
        lo, hi = boot_diff(rows, 2, best_base)
        print("n = %d" % n)
        for nm, a in zip(names, accs):
            print("  %-18s accuracy %.3f" % (nm, a))
        print("  uplift over %s: %+.3f, 95%% bootstrap CI [%+.3f, %+.3f]"
              % (names[best_base], accs[2] - accs[best_base], lo, hi))
    print()
    print("Cases per arm needed (alpha 0.05, power 0.80):")
    for p1, p2 in [(0.72, 0.80), (0.72, 0.76), (0.72, 0.74)]:
        print("  %.2f vs %.2f -> %d" % (p1, p2, sample_size(p1, p2)))
