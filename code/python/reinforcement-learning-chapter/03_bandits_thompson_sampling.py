"""Bernoulli bandits: epsilon-greedy, UCB1, and Thompson sampling (stdlib only).

Part 1 reproduces the chapter's hand-worked Thompson sampling posterior update.
Part 2 compares cumulative regret over 2,000 rounds, averaged over 200 seeds,
for three arms with click rates 0.04, 0.05, and 0.06 (illustrative).
Run: python 03_bandits_thompson_sampling.py
"""
import math
import random

TRUE_P = [0.04, 0.05, 0.06]
T = 2000
SEEDS = 200


def part1():
    # Beta(1,1) prior. Arm X: 3 clicks in 20. Arm Y: 1 click in 4.
    for name, clicks, shows in (("X", 3, 20), ("Y", 1, 4)):
        a, b = 1 + clicks, 1 + shows - clicks
        mean = a / (a + b)
        var = a * b / ((a + b) ** 2 * (a + b + 1))
        print(f"arm {name}: Beta({a},{b}) mean={mean:.4f} sd={math.sqrt(var):.4f}")
    rng = random.Random(7)
    wins = sum(rng.betavariate(2, 4) > rng.betavariate(4, 18) for _ in range(100000))
    print(f"P(theta_Y > theta_X) by Monte Carlo = {wins / 100000:.3f}")


def pull(rng, p):
    return 1 if rng.random() < p else 0


def run(policy, seed):
    rng = random.Random(seed)
    k = len(TRUE_P)
    n = [0] * k
    s = [0] * k
    best = max(TRUE_P)
    regret = 0.0
    for t in range(1, T + 1):
        if policy == "eps":
            if rng.random() < 0.1 or 0 in n:
                arm = rng.randrange(k)
            else:
                arm = max(range(k), key=lambda i: s[i] / n[i])
        elif policy == "ucb":
            if 0 in n:
                arm = n.index(0)
            else:
                arm = max(range(k),
                          key=lambda i: s[i] / n[i] + math.sqrt(2 * math.log(t) / n[i]))
        else:  # thompson
            arm = max(range(k),
                      key=lambda i: rng.betavariate(1 + s[i], 1 + n[i] - s[i]))
        reward = pull(rng, TRUE_P[arm])
        n[arm] += 1
        s[arm] += reward
        regret += best - TRUE_P[arm]
    return regret, n[2] / T


def part2():
    print("\nCumulative expected regret after", T, "rounds (mean of", SEEDS, "seeds)")
    for policy, label in (("eps", "epsilon-greedy 0.1"), ("ucb", "UCB1"),
                          ("ts", "Thompson sampling")):
        res = [run(policy, sd) for sd in range(SEEDS)]
        reg = sum(r for r, _ in res) / SEEDS
        frac = sum(f for _, f in res) / SEEDS
        print(f"  {label:<20} regret={reg:6.2f}  share of pulls on best arm={frac:.2f}")


if __name__ == "__main__":
    part1()
    part2()
