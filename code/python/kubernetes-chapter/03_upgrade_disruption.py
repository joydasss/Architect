"""Check planned Pod evictions against a simplified disruption budget."""


def assess_upgrade(
    replicas: int, max_unavailable: int, planned_evictions: int
) -> dict[str, int | bool]:
    if replicas < 1 or max_unavailable < 0 or planned_evictions < 0:
        raise ValueError("replicas and disruption counts must be non-negative")
    allowed = min(max_unavailable, replicas)
    remaining = max(0, replicas - planned_evictions)
    return {
        "remaining_replicas": remaining,
        "planned_evictions": planned_evictions,
        "within_budget": planned_evictions <= allowed,
    }


def main() -> None:
    for planned_evictions in (1, 2, 4):
        result = assess_upgrade(
            replicas=12,
            max_unavailable=2,
            planned_evictions=planned_evictions,
        )
        print(
            f"evictions={planned_evictions}: remaining={result['remaining_replicas']}, "
            f"within budget={result['within_budget']}"
        )
    print("Real upgrades also depend on scheduling, topology, and spare capacity.")


if __name__ == "__main__":
    main()