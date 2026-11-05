"""Error-cost asymmetry, acceptable error rate and abstention bands.

Part 1: derive the single-threshold decision point from error costs.
Part 2: with a calibrated score, search two thresholds (lo, hi) that split
cases into auto-clear, human review and auto-block, and compare expected cost
per case with the all-human and single-threshold alternatives.
Scores are synthetic and assumed calibrated. Standard library only.

Run: python 03_error_cost_bands.py
"""
import random

C_FN = 400.0   # missed bad case that is auto-cleared (e.g. confirmed fraud)
C_FP = 25.0    # good case auto-blocked (customer friction, support contact)
C_REV = 12.0   # human review cost per case
REV_ERR = 0.03  # share of reviewed cases a human gets wrong (cost = the wrong side)
PREV_ALPHA, PREV_BETA = 0.5, 6.0  # Beta prior for synthetic score distribution


def synth(n, seed=11):
    rng = random.Random(seed)
    scores = [rng.betavariate(PREV_ALPHA, PREV_BETA) for _ in range(n)]
    return scores  # score = true probability of "bad" (calibrated by construction)


def case_cost(p, action):
    """Expected cost of an action for a case whose true bad-probability is p."""
    if action == "clear":
        return p * C_FN
    if action == "block":
        return (1 - p) * C_FP
    # review: pay review cost, human wrong REV_ERR of the time
    wrong = REV_ERR * (p * C_FN + (1 - p) * C_FP)
    return C_REV + wrong


def policy_cost(scores, lo, hi):
    tot = 0.0
    for p in scores:
        a = "clear" if p < lo else ("block" if p >= hi else "review")
        tot += case_cost(p, a)
    return tot / len(scores)


if __name__ == "__main__":
    t_star = C_FP / (C_FP + C_FN)
    print("Single-threshold cost-optimal point p* = C_FP/(C_FP+C_FN) = %.4f" % t_star)
    print("Break-even: auto-clear only if P(bad) < %.4f; mistakes cost %.0fx more on the miss side"
          % (t_star, C_FN / C_FP))
    scores = synth(100_000)
    prev = sum(scores) / len(scores)
    print("Synthetic prevalence of bad cases: %.3f" % prev)
    all_human = sum(case_cost(p, "review") for p in scores) / len(scores)
    all_clear = sum(case_cost(p, "clear") for p in scores) / len(scores)
    single = policy_cost(scores, t_star, t_star)
    best = None
    grid = [i / 200 for i in range(1, 40)] + [i / 20 for i in range(4, 20)]
    for lo in grid:
        for hi in [h for h in grid if h > lo]:
            c = policy_cost(scores[:3_000], lo, hi)
            if best is None or c < best[0]:
                best = (c, lo, hi)
    _, lo, hi = best
    banded = policy_cost(scores, lo, hi)
    n = len(scores)
    n_clear = sum(1 for p in scores if p < lo)
    n_block = sum(1 for p in scores if p >= hi)
    n_rev = n - n_clear - n_block
    print()
    print("%-34s %s" % ("policy", "expected cost per case"))
    print("%-34s $%.3f" % ("auto-clear everything", all_clear))
    print("%-34s $%.3f" % ("human reviews everything", all_human))
    print("%-34s $%.3f" % ("single threshold at p*", single))
    print("%-34s $%.3f" % ("bands lo=%.3f hi=%.3f" % (lo, hi), banded))
    print()
    print("Band shares: clear %.1f%%, review %.1f%%, block %.1f%%"
          % (100 * n_clear / n, 100 * n_rev / n, 100 * n_block / n))
    print("Review workload at 40,000 cases/month: %.0f reviews" % (40_000 * n_rev / n))
    print()
    print("Miscalibration stress: true P(bad) = min(1, k x score), thresholds unchanged")
    print("%-6s %-22s %-22s" % ("k", "banded policy", "human reviews all"))
    for k in (1.0, 1.5, 2.0):
        tb = th = 0.0
        for p in scores:
            q = min(1.0, k * p)
            a = "clear" if p < lo else ("block" if p >= hi else "review")
            tb += case_cost(q, a)
            th += case_cost(q, "review")
        print("%-6.1f $%-21.3f $%-21.3f" % (k, tb / n, th / n))
