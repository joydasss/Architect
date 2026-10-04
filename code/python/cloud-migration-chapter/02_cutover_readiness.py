"""Evaluate synthetic replication and cutover guardrails."""


def check_readiness(replication_lag_seconds, rpo_seconds, checks):
    """Return readiness and blocking reasons for a proposed cutover."""
    blockers = []
    if replication_lag_seconds < 0:
        blockers.append("replication lag cannot be negative")
    elif replication_lag_seconds > rpo_seconds:
        blockers.append("replication lag exceeds the RPO limit")
    for name, passed in checks.items():
        if not passed:
            blockers.append(f"required check failed: {name}")
    return {"ready": not blockers, "blockers": blockers}


if __name__ == "__main__":
    ready = check_readiness(
        replication_lag_seconds=8,
        rpo_seconds=15,
        checks={"write freeze": True, "data validation": True, "rollback owner": True},
    )
    blocked = check_readiness(
        replication_lag_seconds=30,
        rpo_seconds=15,
        checks={"write freeze": True, "business approval": False},
    )
    assert ready["ready"]
    assert not blocked["ready"] and len(blocked["blockers"]) == 2
    print("Ready:", ready)
    print("Blocked:", blocked)