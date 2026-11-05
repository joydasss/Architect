"""Statistics for prompt A/B comparison on a golden set.

Standard library only. Wilson interval, sample size for a proportion, exact
McNemar-style sign test on paired outcomes, and run-to-run noise at
temperature > 0. Outcomes are simulated with a fixed seed.
Run: python 03_prompt_eval_stats.py
"""
import math
import random
from math import comb


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def n_for_halfwidth(p, hw, z=1.96):
    return math.ceil(z * z * p * (1 - p) / (hw * hw))


def sign_test_p(b, c):
    """Two-sided exact p-value on discordant pairs (b: A only right, c: B only right)."""
    n = b + c
    k = min(b, c)
    tail = sum(comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def main():
    print("== interval width on a golden set ==")
    for n in (50, 200, 500, 1000):
        k = round(0.84 * n)
        lo, hi = wilson(k, n)
        print(f"n={n:5d} acc={k / n:.3f} 95% CI [{lo:.3f}, {hi:.3f}] width {hi - lo:.3f}")
    print("\n== sample size for +/-3 points at p=0.85 ==", n_for_halfwidth(0.85, 0.03))

    rng = random.Random(5)
    n = 300
    # prompt A true accuracy 0.80, prompt B 0.85, positively correlated per item
    a_out, b_out = [], []
    for _ in range(n):
        difficulty = rng.random()
        a_out.append(difficulty < 0.80)
        b_out.append(difficulty < 0.85 if rng.random() < 0.9 else rng.random() < 0.85)
    a_acc, b_acc = sum(a_out) / n, sum(b_out) / n
    b_only = sum(1 for x, y in zip(a_out, b_out) if y and not x)
    a_only = sum(1 for x, y in zip(a_out, b_out) if x and not y)
    print(f"\n== paired comparison, n={n} ==")
    print(f"A acc {a_acc:.3f}, B acc {b_acc:.3f}, B-only right {b_only}, A-only right {a_only}")
    print(f"exact sign test p-value: {sign_test_p(a_only, b_only):.4f}")
    la, ha = wilson(sum(a_out), n)
    lb, hb = wilson(sum(b_out), n)
    print(f"unpaired CIs overlap: A [{la:.3f},{ha:.3f}] B [{lb:.3f},{hb:.3f}]")

    print("\n== run-to-run noise at temperature > 0 (same prompt, 20 reruns, n=200) ==")
    accs = []
    for _ in range(20):
        correct = 0
        for i in range(200):
            p_item = 0.97 if i < 140 else (0.5 if i < 180 else 0.1)   # easy / ambiguous / hard
            correct += rng.random() < p_item
        accs.append(correct / 200)
    mean = sum(accs) / len(accs)
    sd = math.sqrt(sum((a - mean) ** 2 for a in accs) / (len(accs) - 1))
    print(f"mean {mean:.3f} sd {sd:.4f} min {min(accs):.3f} max {max(accs):.3f}")

    print("\n== discordant pairs needed ==")
    for diff_b in (10, 15, 20, 30):
        print(f"b={diff_b + 10}, c=10 -> p={sign_test_p(10, diff_b + 10):.4f}")


if __name__ == "__main__":
    main()
