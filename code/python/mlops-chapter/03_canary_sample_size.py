"""Canary / A/B sample-size calculator and a Thompson-sampling router simulation.

Standard library only. Illustrative numbers.
  * n per arm for a two-proportion z-test (two-sided alpha, power 1 - beta).
  * Time to collect n given daily traffic and the canary split.
  * Thompson sampling over three model variants with Bernoulli reward.
"""
import math
import random

Z = {0.05: 1.959964, 0.10: 1.644854}  # two-sided alpha -> z_{1-alpha/2}
ZB = {0.80: 0.841621, 0.90: 1.281552}  # power -> z_power


def n_per_arm(p1, p2, alpha=0.05, power=0.80):
    za, zb = Z[alpha], ZB[power]
    pbar = (p1 + p2) / 2
    num = (za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return math.ceil(num / (p1 - p2) ** 2)


def days_needed(n_canary, daily_requests, canary_fraction):
    return n_canary / (daily_requests * canary_fraction)


def thompson(true_rates, rounds=20_000, seed=3):
    rng = random.Random(seed)
    a = [1] * len(true_rates)
    b = [1] * len(true_rates)
    pulls = [0] * len(true_rates)
    for _ in range(rounds):
        draws = [rng.betavariate(a[i], b[i]) for i in range(len(true_rates))]
        k = draws.index(max(draws))
        pulls[k] += 1
        if rng.random() < true_rates[k]:
            a[k] += 1
        else:
            b[k] += 1
    return pulls


if __name__ == "__main__":
    print("Sample size per arm (alpha=0.05 two-sided, power=0.80)")
    for p1, p2 in [(0.050, 0.055), (0.050, 0.060), (0.020, 0.024), (0.0100, 0.0120)]:
        n = n_per_arm(p1, p2)
        print(f"  baseline {p1:.4f} -> {p2:.4f}: n per arm = {n:,}")
    n = n_per_arm(0.05, 0.06)
    print("\nCanary duration for n =", f"{n:,}", "per arm at 200,000 requests/day")
    for f in (0.01, 0.05, 0.10, 0.50):
        print(f"  canary {f:>4.0%}: {days_needed(n, 200_000, f):6.2f} days")
    print("\nThompson sampling, 3 variants with true rates 0.050 / 0.055 / 0.065, 20,000 requests")
    pulls = thompson([0.050, 0.055, 0.065])
    for i, p in enumerate(pulls):
        print(f"  variant {i}: {p:,} requests ({p / sum(pulls):.1%})")
