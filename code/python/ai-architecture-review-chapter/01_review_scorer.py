"""Weighted lens scorer with hard gates for an AI architecture review.

Standard library only. Run: python 01_review_scorer.py

Each of the 14 lenses is scored 0-4 by the review panel from evidence:
  0 = no evidence or lens ignored      1 = claims only
  2 = partial evidence                 3 = adequate evidence, gaps tracked
  4 = strong evidence, tested, owned

Weights sum to 100. Hard gates are independent of the weighted total: a
failed gate caps the outcome regardless of score.
"""

LENSES = {
    "value_baseline": 8,
    "workload_qualification": 5,
    "data": 9,
    "model_selection": 5,
    "composition": 5,
    "inference_serving": 5,
    "gateway_fallback": 6,
    "human_oversight": 8,
    "platform_lifecycle": 5,
    "eval_observability": 9,
    "safety_security_privacy": 12,
    "reliability": 6,
    "cost_perf_sustainability": 7,
    "operability_ownership": 10,
}
assert sum(LENSES.values()) == 100

# Hard gate: (lens, minimum score). Failing any gate caps the outcome.
HARD_GATES = {
    "data": 2,
    "human_oversight": 2,
    "eval_observability": 2,
    "safety_security_privacy": 3,
    "operability_ownership": 2,
}


def weighted_score(scores):
    """Return a 0-100 score: sum(weight * score / 4)."""
    return sum(LENSES[k] * scores[k] / 4 for k in LENSES)


def failed_gates(scores):
    return [f"{k} < {m} (got {scores[k]})" for k, m in HARD_GATES.items() if scores[k] < m]


def outcome(scores):
    total = weighted_score(scores)
    gates = failed_gates(scores)
    if any(scores[k] == 0 for k in LENSES):
        return total, gates, "defer (a lens has no evidence)"
    if gates and total < 50:
        return total, gates, "reject"
    if gates:
        return total, gates, "defer (hard gate failed)"
    if total >= 80:
        return total, gates, "approve"
    if total >= 65:
        return total, gates, "approve with conditions"
    if total >= 50:
        return total, gates, "defer"
    return total, gates, "reject"


SAMPLE = {
    "support_rag_first_review": dict(
        value_baseline=3, workload_qualification=3, data=2, model_selection=3,
        composition=3, inference_serving=3, gateway_fallback=2, human_oversight=3,
        platform_lifecycle=2, eval_observability=2, safety_security_privacy=2,
        reliability=2, cost_perf_sustainability=3, operability_ownership=3),
    "support_rag_after_redesign": dict(
        value_baseline=3, workload_qualification=3, data=3, model_selection=3,
        composition=4, inference_serving=3, gateway_fallback=3, human_oversight=3,
        platform_lifecycle=3, eval_observability=3, safety_security_privacy=4,
        reliability=3, cost_perf_sustainability=3, operability_ownership=3),
    "demo_driven_agent": dict(
        value_baseline=1, workload_qualification=2, data=2, model_selection=2,
        composition=2, inference_serving=2, gateway_fallback=1, human_oversight=1,
        platform_lifecycle=1, eval_observability=1, safety_security_privacy=1,
        reliability=1, cost_perf_sustainability=1, operability_ownership=1),
}

if __name__ == "__main__":
    for name, s in SAMPLE.items():
        total, gates, result = outcome(s)
        print(f"{name}: score={total:.1f} outcome={result}")
        for g in gates:
            print(f"  GATE FAILED: {g}")
