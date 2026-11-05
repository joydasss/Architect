"""Weighted qualification scorer with hard gates and weight sensitivity.

Dimensions are scored 1 (poor) to 5 (strong). Risk is scored so that 5 means
LOW residual risk, so a higher number is always better. A hard gate overrides
the weighted score: any gate dimension at 1 means "do not proceed".
Standard library only. Scores are illustrative.

Run: python 02_qualification_scorer.py
"""
import random

DIMS = ["value", "feasibility", "risk", "data", "operability"]
WEIGHTS = {"value": 0.30, "feasibility": 0.20, "risk": 0.20, "data": 0.15, "operability": 0.15}
GATES = ["value", "risk", "data"]  # a 1 here blocks the use case regardless of total

CANDIDATES = {
    "Support reply drafting (GenAI+RAG)":   dict(value=4, feasibility=4, risk=4, data=4, operability=3),
    "Invoice dispute triage (predictive)":  dict(value=4, feasibility=4, risk=4, data=4, operability=4),
    "Tax-rate lookup by region":            dict(value=1, feasibility=5, risk=5, data=5, operability=5),
    "Autonomous refund approval (agent)":   dict(value=5, feasibility=2, risk=1, data=3, operability=2),
    "Contract clause extraction":           dict(value=3, feasibility=3, risk=3, data=2, operability=3),
    "Executive chat over all documents":    dict(value=2, feasibility=3, risk=2, data=2, operability=2),
}


def total(scores, w=WEIGHTS):
    return sum(w[d] * scores[d] for d in DIMS)


def verdict(scores):
    if any(scores[g] <= 1 for g in GATES):
        return "STOP (gate)"
    t = total(scores)
    if t >= 3.8:
        return "PROCEED"
    if t >= 3.2:
        return "SPIKE"
    return "DEFER"


def random_weights(rng):
    raw = [rng.random() + 0.05 for _ in DIMS]
    s = sum(raw)
    return {d: r / s for d, r in zip(DIMS, raw)}


if __name__ == "__main__":
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9
    print("%-38s %6s  %s" % ("use case", "score", "verdict"))
    ranked = sorted(CANDIDATES.items(), key=lambda kv: -total(kv[1]))
    for name, s in ranked:
        print("%-38s %6.2f  %s" % (name, total(s), verdict(s)))
    rng = random.Random(7)
    trials = 2000
    wins = {n: 0 for n in CANDIDATES}
    top3 = {n: 0 for n in CANDIDATES}
    live = [n for n, s in CANDIDATES.items() if verdict(s) != "STOP (gate)"]
    for _ in range(trials):
        w = random_weights(rng)
        order = sorted(live, key=lambda n: -total(CANDIDATES[n], w))
        wins[order[0]] += 1
        for n in order[:3]:
            top3[n] += 1
    print()
    print("Rank stability over %d random weight vectors" % trials)
    print("%-38s %8s %8s" % ("use case", "first", "top-3"))
    for n in sorted(CANDIDATES, key=lambda n: -wins[n]):
        print("%-38s %7.1f%% %7.1f%%" % (n, 100 * wins[n] / trials, 100 * top3[n] / trials))
