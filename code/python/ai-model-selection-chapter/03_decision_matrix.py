"""Hard-constraint filter plus weighted decision matrix with sensitivity check.

Standard library only. Candidates, ratings (1-5), and weights are ILLUSTRATIVE
inputs for a worked example, not measurements of real products. The script:
1. removes candidates that fail a hard constraint,
2. scores the rest with normalized weights,
3. perturbs the weights randomly 2000 times and reports how often each
   candidate wins, which shows whether the ranking is fragile.
"""
import random

WEIGHTS = {"quality": 0.35, "latency": 0.15, "cost": 0.20,
           "control": 0.15, "ops_burden": 0.15}

CANDIDATES = {
    "hosted-frontier": {"hard_ok": True, "quality": 5, "latency": 3,
                        "cost": 2, "control": 2, "ops_burden": 5},
    "hosted-mid":      {"hard_ok": True, "quality": 4, "latency": 4,
                        "cost": 4, "control": 2, "ops_burden": 5},
    "open-weight-self": {"hard_ok": True, "quality": 4, "latency": 4,
                         "cost": 3, "control": 5, "ops_burden": 2},
    "small-self":      {"hard_ok": True, "quality": 3, "latency": 5,
                        "cost": 5, "control": 5, "ops_burden": 3},
    "hosted-eu-gap":   {"hard_ok": False, "quality": 5, "latency": 4,
                        "cost": 3, "control": 2, "ops_burden": 5},
}


def score(c, w):
    total = sum(w.values())
    return sum(w[k] / total * c[k] for k in w)


def main():
    eligible = {k: v for k, v in CANDIDATES.items() if v["hard_ok"]}
    removed = [k for k in CANDIDATES if k not in eligible]
    print("removed by hard constraints:", ", ".join(removed))
    print("\nbase weighted scores:")
    for name, c in sorted(eligible.items(), key=lambda kv: -score(kv[1], WEIGHTS)):
        print(f"  {name:17s} {score(c, WEIGHTS):.2f}")
    rng = random.Random(5)
    wins = {k: 0 for k in eligible}
    trials = 2000
    for _ in range(trials):
        w = {k: v * rng.uniform(0.6, 1.4) for k, v in WEIGHTS.items()}
        best = max(eligible, key=lambda n: score(eligible[n], w))
        wins[best] += 1
    print(f"\nwin share under +/-40% weight perturbation ({trials} trials):")
    for name, n in sorted(wins.items(), key=lambda kv: -kv[1]):
        print(f"  {name:17s} {n / trials:.3f}")


if __name__ == "__main__":
    main()
