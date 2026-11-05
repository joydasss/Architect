"""Error compounding, pass@k versus pass^k, and cost/latency growth (standard library only).

Run: python 02_error_compounding.py
"""
from math import comb


def chain_success(p, n):
    return p ** n


def pass_at_k(c, n, k):
    """Unbiased estimator: probability at least one of k samples drawn from n (c correct) passes."""
    if n - c < k:
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


def pass_pow_k(p, k):
    """Probability that k independent attempts all succeed, given per-attempt success p."""
    return p ** k


def context_cost(steps, base_tokens=2000, added_per_step=800, price_in=3.0, price_out=15.0, out_per_step=250):
    """Re-sending the whole history every step. Prices are illustrative USD per million tokens."""
    total_in = sum(base_tokens + added_per_step * i for i in range(steps))
    total_out = out_per_step * steps
    cost = total_in * price_in / 1e6 + total_out * price_out / 1e6
    return total_in, total_out, cost


if __name__ == "__main__":
    print("Per-step success p, chain of n steps: p^n")
    for p in (0.99, 0.95, 0.90):
        print("  p=%.2f  " % p + "  ".join("n=%d: %.3f" % (n, chain_success(p, n)) for n in (5, 10, 20, 50)))

    print("\nSteps allowed per retry: step succeeds with prob 1-(1-p)^r after r tries")
    p = 0.90
    for r in (1, 2, 3):
        q = 1 - (1 - p) ** r
        print("  p=0.90 r=%d -> per-step %.3f, 10-step chain %.3f" % (r, q, q ** 10))

    print("\npass@k vs pass^k, per-attempt success 0.70 (independent attempts)")
    for k in (1, 3, 5, 8):
        print("  k=%d  pass@k=%.3f  pass^k=%.3f" % (k, 1 - (1 - 0.7) ** k, pass_pow_k(0.7, k)))

    print("\nUnbiased pass@k from n=10 samples, c=7 correct")
    for k in (1, 3, 5):
        print("  k=%d  %.3f" % (k, pass_at_k(7, 10, k)))

    print("\nCost of re-sending history (illustrative prices 3.00 in / 15.00 out per M tokens)")
    for steps in (5, 10, 20, 40):
        tin, tout, cost = context_cost(steps)
        print("  steps=%2d  input_tokens=%7d  output_tokens=%5d  cost=$%.3f" % (steps, tin, tout, cost))

    print("\nLatency: 20 steps x (2.5 s model + 0.8 s tool) =", 20 * (2.5 + 0.8), "s")
    print("Two 0.8 s tool calls per step: sequential", 20 * 1.6, "s of tool time, parallel", 20 * 0.8, "s, saving", 20 * 0.8, "s")
