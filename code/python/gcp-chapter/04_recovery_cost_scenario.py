"""Compare synthetic recovery options against explicit objectives."""


OPTIONS = (
    {"name": "Backup and restore", "rto_hours": 10, "rpo_hours": 4, "cost_units": 1},
    {"name": "Warm standby", "rto_hours": 1, "rpo_hours": 0.25, "cost_units": 4},
    {"name": "Active-active", "rto_hours": 0.1, "rpo_hours": 0.05, "cost_units": 9},
)


def evaluate_options(rto_target: float, rpo_target: float) -> list[dict[str, object]]:
    results = []
    for option in OPTIONS:
        meets = option["rto_hours"] <= rto_target and option["rpo_hours"] <= rpo_target
        results.append({**option, "meets_objectives": meets})
    return sorted(results, key=lambda item: (not item["meets_objectives"], item["cost_units"]))


def main() -> None:
    rto_target = 2
    rpo_target = 0.5
    print(f"Targets: RTO <= {rto_target}h, RPO <= {rpo_target}h")
    for option in evaluate_options(rto_target, rpo_target):
        status = "meets" if option["meets_objectives"] else "misses"
        print(
            f"{option['name']}: {status}; RTO={option['rto_hours']}h, "
            f"RPO={option['rpo_hours']}h, normalized cost={option['cost_units']}"
        )
    print("Normalized costs are illustrative, not current Google Cloud prices.")


if __name__ == "__main__":
    main()