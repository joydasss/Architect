"""Speculative decoding: expected speedup formula, Monte Carlo check, batch-size effect.

Standard library only. All costs are normalized so that one target-model decode
step at small batch costs 1.0.

Formulas (independent acceptance probability alpha per drafted token, k drafts):
    E[tokens per round] = (1 - alpha**(k+1)) / (1 - alpha)
    speedup             = E / (1 + k*c)        c = draft step cost / target step cost
Batch effect: verifying B*(k+1) tokens costs max(1, B*(k+1)/R) target steps, with
R an illustrative compute-ridge batch (R = 150 here); the plain baseline costs max(1, B/R).
"""
import random


def expected_tokens(alpha, k):
    if alpha == 1.0:
        return k + 1
    return (1 - alpha ** (k + 1)) / (1 - alpha)


def speedup(alpha, k, c):
    return expected_tokens(alpha, k) / (1 + k * c)


def simulate_round(alpha, k, rng):
    """Tokens produced by one draft-then-verify round (accepted prefix + 1 target token)."""
    accepted = 0
    while accepted < k and rng.random() < alpha:
        accepted += 1
    return accepted + 1


def monte_carlo(alpha, k, rounds=200000, seed=3):
    rng = random.Random(seed)
    return sum(simulate_round(alpha, k, rng) for _ in range(rounds)) / rounds


def batch_speedup(alpha, k, c, batch, ridge=150.0):
    base = max(1.0, batch / ridge)
    verify = max(1.0, batch * (k + 1) / ridge)
    return expected_tokens(alpha, k) * base / (verify + k * c)


def main():
    c = 0.05
    print("== Expected tokens per round: closed form vs Monte Carlo ==")
    for alpha, k in ((0.7, 4), (0.8, 4), (0.8, 8), (0.9, 4)):
        print(f"alpha={alpha} k={k}: formula {expected_tokens(alpha, k):.3f}  simulated {monte_carlo(alpha, k):.3f}")

    print(f"\n== Speedup at c={c} (draft costs 5% of a target step) ==")
    print("alpha \\ k " + "".join(f"{k:>7}" for k in range(1, 9)))
    for alpha in (0.5, 0.6, 0.7, 0.8, 0.9):
        row = [speedup(alpha, k, c) for k in range(1, 9)]
        best = max(range(8), key=lambda i: row[i]) + 1
        print(f"{alpha:>9} " + "".join(f"{v:>7.2f}" for v in row) + f"   best k={best}")

    print("\n== Effect of draft cost c at alpha=0.8, k=4 ==")
    for cc in (0.02, 0.05, 0.10, 0.20, 0.40):
        print(f"c={cc:<5} speedup {speedup(0.8, 4, cc):.2f}")

    print("\n== Effect of batch size (alpha=0.8, c=0.05, ridge R=150) ==")
    print(f"{'batch':>6} {'k=2':>7} {'k=4':>7} {'k=8':>7}")
    for b in (1, 8, 32, 64, 128, 256):
        print(f"{b:>6} " + "".join(f"{batch_speedup(0.8, k, c, b):>7.2f}" for k in (2, 4, 8)))

    print("\n== Break-even acceptance rate for k=4, c=0.05 ==")
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if speedup(mid, 4, 0.05) < 1.0:
            lo = mid
        else:
            hi = mid
    print(f"speedup = 1 at alpha = {hi:.3f}")


if __name__ == "__main__":
    main()
