"""Drift monitor: Population Stability Index (PSI) and two-sample KS statistic.

Standard library only. Part 1 reproduces the hand-worked PSI table in the
chapter (five equal-frequency reference bins). Part 2 simulates a numeric
feature that shifts and reports PSI, KS and an alert level per day.
All data are synthetic and illustrative.
"""
import math
import random
from bisect import bisect_right


def psi_from_fractions(expected, actual, eps=1e-6):
    """PSI = sum_i (a_i - e_i) * ln(a_i / e_i). Fractions are clipped at eps."""
    total = 0.0
    rows = []
    for e, a in zip(expected, actual):
        e, a = max(e, eps), max(a, eps)
        term = (a - e) * math.log(a / e)
        rows.append((e, a, a - e, math.log(a / e), term))
        total += term
    return total, rows


def quantile_edges(reference, bins):
    s = sorted(reference)
    n = len(s)
    return [s[min(n - 1, int(n * i / bins))] for i in range(1, bins)]


def fractions(values, edges):
    counts = [0] * (len(edges) + 1)
    for v in values:
        counts[bisect_right(edges, v)] += 1
    return [c / len(values) for c in counts]


def psi_numeric(reference, current, bins=10):
    """Bin edges are reference quantiles, so each reference bin holds about 1/bins."""
    edges = quantile_edges(reference, bins)
    return psi_from_fractions(fractions(reference, edges), fractions(current, edges))[0]


def ks_statistic(x, y):
    """Maximum distance between the two empirical CDFs."""
    x, y = sorted(x), sorted(y)
    best = 0.0
    for v in x + y:
        cx = bisect_right(x, v) / len(x)
        cy = bisect_right(y, v) / len(y)
        best = max(best, abs(cx - cy))
    return best


def ks_critical(n, m, alpha=0.05):
    """Large-sample critical value c(alpha) * sqrt((n+m)/(n*m))."""
    c = math.sqrt(-0.5 * math.log(alpha / 2))
    return c * math.sqrt((n + m) / (n * m))


def level(psi):
    return "stable" if psi < 0.10 else "investigate" if psi < 0.25 else "action"


def main():
    print("Part 1: worked PSI table (5 bins)")
    expected = [0.20, 0.20, 0.20, 0.20, 0.20]
    actual = [0.10, 0.15, 0.20, 0.25, 0.30]
    total, rows = psi_from_fractions(expected, actual)
    print("bin   e     a     a-e    ln(a/e)   term")
    for i, (e, a, d, l, t) in enumerate(rows, 1):
        print(f"{i}   {e:.2f}  {a:.2f}  {d:+.2f}  {l:+.4f}  {t:.4f}")
    print(f"PSI = {total:.4f} -> {level(total)}")

    print("\nPart 2: simulated daily drift of one feature")
    rng = random.Random(7)
    ref = [rng.gauss(100, 20) for _ in range(20_000)]
    print("day  mean_shift  PSI     level        KS      KS_crit  KS_reject")
    for day, shift in enumerate([0, 0, 2, 5, 10, 20], 1):
        cur = [rng.gauss(100 + shift, 20) for _ in range(5_000)]
        p = psi_numeric(ref, cur)
        ks = ks_statistic(ref, cur)
        crit = ks_critical(len(ref), len(cur))
        print(f"{day}    {shift:>3}        {p:.4f}  {level(p):<11}  {ks:.4f}  {crit:.4f}   {ks > crit}")


if __name__ == "__main__":
    main()
