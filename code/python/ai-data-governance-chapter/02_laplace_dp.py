"""Laplace mechanism for a counting query, with epsilon intuition.

Standard library only. A counting query has sensitivity 1 (adding or removing
one person changes the count by at most 1). The Laplace mechanism adds noise
with scale b = sensitivity / epsilon. We print the analytic error, an
empirical check, the likelihood-ratio bound that defines epsilon, and basic
composition.
"""
import math
import random

random.seed(7)
TRUE_COUNT = 1_000  # e.g. tickets mentioning a medical condition
SENS = 1.0


def laplace(b):
    """Sample Laplace(0, b) as the difference of two exponentials."""
    return random.expovariate(1 / b) - random.expovariate(1 / b)


def main():
    print("epsilon | scale b | mean |error| analytic | empirical | P(|err|>10)")
    for eps in (0.1, 0.5, 1.0, 2.0, 5.0):
        b = SENS / eps
        n = 100_000
        emp = sum(abs(laplace(b)) for _ in range(n)) / n
        tail = math.exp(-10 / b)  # P(|X|>t) = exp(-t/b) for Laplace
        print(f"{eps:7.1f} | {b:7.2f} | {b:20.2f} | {emp:9.2f} | {tail:.4f}")

    eps = 1.0
    b = SENS / eps
    out = 1000.5
    p0 = math.exp(-abs(out - 1000) / b) / (2 * b)
    p1 = math.exp(-abs(out - 1001) / b) / (2 * b)
    print(f"\nWith eps=1, density ratio for neighbours at output {out}: {p0 / p1:.3f}"
          f" (bound e^eps = {math.e:.3f})")
    out = 999.0
    p0 = math.exp(-abs(out - 1000) / b) / (2 * b)
    p1 = math.exp(-abs(out - 1001) / b) / (2 * b)
    print(f"At output {out}: ratio {p0 / p1:.3f} (bound reached: outputs outside the two counts)")

    for eps in (0.1, 1.0, 5.0):
        odds_bound = math.exp(eps)
        post = odds_bound / (1 + odds_bound)
        print(f"eps={eps}: worst-case posterior after one release, prior 0.5 -> {post:.3f}")

    print("\nBasic composition: 12 monthly releases at eps=0.5 each -> total eps =", 12 * 0.5)

    print("\nRelative error at eps=1 (mean |err| = 1):")
    for n in (10, 100, 1_000, 100_000):
        print(f"  true count {n:>7}: {100 * 1.0 / n:7.3f} percent")


if __name__ == "__main__":
    main()
