"""Off-policy evaluation of a logged contextual bandit, plus a GAE worked example.

Standard library only. A logging policy picks one of 3 actions in 2 contexts.
We estimate the value of a new policy from the logs with the direct method,
inverse propensity scoring (IPS), self-normalised IPS, and doubly robust (DR),
and compare against the true value computed from the known reward table.
Run: python 04_off_policy_evaluation_and_gae.py
"""
import random

# True mean reward r[context][action] (illustrative).
R = {0: [0.30, 0.50, 0.10], 1: [0.20, 0.10, 0.60]}
LOG = {0: [0.70, 0.20, 0.10], 1: [0.50, 0.40, 0.10]}   # logging policy mu
NEW = {0: [0.10, 0.80, 0.10], 1: [0.10, 0.10, 0.80]}   # target policy pi


def true_value():
    return sum(0.5 * sum(NEW[x][a] * R[x][a] for a in range(3)) for x in (0, 1))


def sample_log(n, rng):
    data = []
    for _ in range(n):
        x = rng.randrange(2)
        a = rng.choices(range(3), weights=LOG[x])[0]
        r = 1.0 if rng.random() < R[x][a] else 0.0
        data.append((x, a, r))
    return data


def estimates(data):
    # Reward model fit on the logs: mean reward per (context, action) cell.
    sums, cnt = {}, {}
    for x, a, r in data:
        sums[(x, a)] = sums.get((x, a), 0.0) + r
        cnt[(x, a)] = cnt.get((x, a), 0) + 1
    rhat = {k: sums[k] / cnt[k] for k in sums}

    def model(x, a):
        return rhat.get((x, a), 0.0)

    n = len(data)
    w = [NEW[x][a] / LOG[x][a] for x, a, _ in data]
    ips = sum(wi * r for wi, (_, _, r) in zip(w, data)) / n
    snips = sum(wi * r for wi, (_, _, r) in zip(w, data)) / sum(w)
    dm = sum(sum(NEW[x][a] * model(x, a) for a in range(3)) for x, _, _ in data) / n
    dr = 0.0
    for wi, (x, a, r) in zip(w, data):
        dr += sum(NEW[x][b] * model(x, b) for b in range(3)) + wi * (r - model(x, a))
    dr /= n
    ess = sum(w) ** 2 / sum(wi * wi for wi in w)
    return {"direct": dm, "ips": ips, "snips": snips, "dr": dr}, max(w), ess


def ope_demo():
    print("True value of new policy:", round(true_value(), 4))
    for n in (500, 5000):
        runs = [estimates(sample_log(n, random.Random(s))) for s in range(200)]
        print(f"\nn={n} logged rounds, 200 repetitions (mean +/- sd of estimate)")
        for key in ("direct", "ips", "snips", "dr"):
            vals = [r[0][key] for r in runs]
            m = sum(vals) / len(vals)
            sd = (sum((v - m) ** 2 for v in vals) / len(vals)) ** 0.5
            print(f"  {key:<7} {m:.4f} +/- {sd:.4f}")
        print(f"  max importance weight {max(r[1] for r in runs):.1f},"
              f" mean effective sample size {sum(r[2] for r in runs) / len(runs):.0f}")


def gae(rewards, values, gamma, lam):
    """values has len(rewards)+1 entries (bootstrap value last)."""
    adv, last = [0.0] * len(rewards), 0.0
    for t in reversed(range(len(rewards))):
        delta = rewards[t] + gamma * values[t + 1] - values[t]
        last = delta + gamma * lam * last
        adv[t] = last
    return adv


def gae_demo():
    rewards = [0.0, 0.0, 1.0]
    values = [0.5, 0.6, 0.8, 0.0]
    print("\nGAE worked example: rewards", rewards, "values", values)
    for lam in (0.0, 0.5, 1.0):
        adv = gae(rewards, values, 0.9, lam)
        print(f"  lambda={lam}: advantages =", [round(a, 4) for a in adv])


if __name__ == "__main__":
    ope_demo()
    gae_demo()
