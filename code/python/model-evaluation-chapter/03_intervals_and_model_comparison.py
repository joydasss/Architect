"""Wilson and bootstrap intervals, McNemar, paired bootstrap, corrected t-test,
and sample-size arithmetic.

Standard library only. Run: python 03_intervals_and_model_comparison.py
"""
import math
import random
import statistics

Z95 = 1.959964


def wilson(k, n, z=Z95):
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return centre - half, centre + half


def wald(k, n, z=Z95):
    p = k / n
    h = z * math.sqrt(p * (1 - p) / n)
    return p - h, p + h


def mcnemar_exact(b, c):
    """Two-sided exact binomial p-value on discordant pairs (b, c)."""
    n = b + c
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2**n
    return min(1.0, 2 * tail)


def simulate_pair(n, rng):
    """Model A ~ 0.86 accurate, model B ~ 0.88 accurate, correlated errors."""
    a_ok, b_ok = [], []
    for _ in range(n):
        hard = rng.random() < 0.15           # shared hard cases
        if hard:
            a_ok.append(rng.random() < 0.1)
            b_ok.append(rng.random() < 0.15)
        else:
            a_ok.append(rng.random() < 0.99)
            b_ok.append(rng.random() < 0.995)
    return a_ok, b_ok


def paired_bootstrap(a_ok, b_ok, rng, reps=2000):
    n = len(a_ok)
    diffs = []
    for _ in range(reps):
        idx = [rng.randrange(n) for _ in range(n)]
        diffs.append(sum(b_ok[i] - a_ok[i] for i in idx) / n)
    diffs.sort()
    return diffs[int(0.025 * reps)], diffs[int(0.975 * reps)]


def corrected_resampled_t(diffs, n_train, n_test):
    """Nadeau-Bengio corrected statistic for J resampled differences."""
    j = len(diffs)
    mean = statistics.mean(diffs)
    var = statistics.variance(diffs)
    se = math.sqrt((1 / j + n_test / n_train) * var)
    return mean / se, mean / math.sqrt(var / j)


def n_for_halfwidth(p, h, z=Z95):
    return math.ceil(z**2 * p * (1 - p) / h**2)


def n_for_paired_difference(delta, discordant_rate, alpha_z=Z95, power_z=0.841621):
    """Approximate n for McNemar-style comparison.

    delta: true accuracy difference (b - c)/n; discordant_rate: (b + c)/n.
    """
    return math.ceil((alpha_z * math.sqrt(discordant_rate)
                      + power_z * math.sqrt(discordant_rate - delta**2)) ** 2 / delta**2)


if __name__ == "__main__":
    print("== Interval for 9 successes out of 10 and 90 of 100 ==")
    for k, n in ((9, 10), (90, 100), (0, 50)):
        w = wilson(k, n)
        d = wald(k, n)
        print(f"k={k} n={n}: Wilson=({w[0]:.3f}, {w[1]:.3f}) "
              f"Wald=({d[0]:.3f}, {d[1]:.3f})")
    print()

    rng = random.Random(3)
    a_ok, b_ok = simulate_pair(1000, rng)
    acc_a, acc_b = sum(a_ok) / 1000, sum(b_ok) / 1000
    b = sum(1 for x, y in zip(a_ok, b_ok) if (not x) and y)   # only B right
    c = sum(1 for x, y in zip(a_ok, b_ok) if x and (not y))   # only A right
    print("== Paired comparison on 1000 shared test cases ==")
    print(f"accuracy A={acc_a:.3f} B={acc_b:.3f} diff={acc_b - acc_a:+.3f}")
    print(f"discordant: only-B-correct={b} only-A-correct={c}")
    print(f"McNemar exact p-value: {mcnemar_exact(b, c):.3f}")
    lo, hi = paired_bootstrap(a_ok, b_ok, random.Random(9))
    print(f"paired bootstrap 95% CI for B-A: ({lo:+.4f}, {hi:+.4f})")
    print()

    print("== Corrected resampled t-test (10 splits, 80/20 of n=1000) ==")
    diffs = [0.012, 0.020, -0.004, 0.015, 0.008, 0.018, 0.002, 0.011, 0.016, 0.007]
    t_corr, t_naive = corrected_resampled_t(diffs, 800, 200)
    print(f"mean diff={statistics.mean(diffs):.4f} naive t={t_naive:.2f} corrected t={t_corr:.2f}")
    print("two-sided 5% critical value, 9 degrees of freedom: 2.262\n")

    print("== Sample size arithmetic ==")
    print(f"n for +/-2% half-width on p=0.9: {n_for_halfwidth(0.9, 0.02)}")
    print(f"n for +/-2% half-width on p=0.5: {n_for_halfwidth(0.5, 0.02)}")
    print(f"positives needed for recall CI +/-5% at recall 0.8: {n_for_halfwidth(0.8, 0.05)}")
    print(f"paired n to detect +2% accuracy with 10% discordant rate: "
          f"{n_for_paired_difference(0.02, 0.10)}")
