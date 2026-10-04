"""Score migration readiness from explicit evidence fields."""


REQUIRED_EVIDENCE = (
    "owner",
    "dependencies",
    "target_controls",
    "data_validation",
    "monitoring",
    "rollback_plan",
)


def score_readiness(evidence):
    """Return a percentage and names of missing evidence items."""
    missing = [name for name in REQUIRED_EVIDENCE if not evidence.get(name, False)]
    score = round(100 * (len(REQUIRED_EVIDENCE) - len(missing)) / len(REQUIRED_EVIDENCE))
    return {"score": score, "missing": missing, "ready": not missing}


if __name__ == "__main__":
    complete = {name: True for name in REQUIRED_EVIDENCE}
    incomplete = dict(complete, monitoring=False, rollback_plan=False)
    assert score_readiness(complete) == {"score": 100, "missing": [], "ready": True}
    result = score_readiness(incomplete)
    assert result["score"] == 67 and not result["ready"]
    print("Incomplete readiness:", result)