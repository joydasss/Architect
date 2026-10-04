"""Compare synthetic recovery options against explicit RTO/RPO objectives."""


OPTIONS = (
    {"name": "Backup and restore", "rto_hours": 12, "rpo_hours": 4, "cost_units": 1},
    {"name": "Warm standby", "rto_hours": 1, "rpo_hours": 0.25, "cost_units": 4},
    {"name": "Active-active", "rto_hours": 0.1, "rpo_hours": 0.05, "cost_units": 8},
)


def evaluate_options(
    rto_target_hours: float, rpo_target_hours: float
) -> list[dict[str, object]]:
    evaluated = []
    for option in OPTIONS:
        meets_objectives = (
            option["rto_hours"] <= rto_target_hours
            and option["rpo_hours"] <= rpo_target_hours
        )
        evaluated.append({**option, "meets_objectives": meets_objectives})
    return sorted(
        evaluated,
        key=lambda item: (not item["meets_objectives"], item["cost_units"]),
    )


def main() -> None:
    rto_target_hours = 2
    rpo_target_hours = 0.5
    print(f"Targets: RTO <= {rto_target_hours}h, RPO <= {rpo_target_hours}h")
    for option in evaluate_options(rto_target_hours, rpo_target_hours):
        status = "meets" if option["meets_objectives"] else "misses"
        print(
            f"{option['name']}: {status} objectives; "
            f"RTO={option['rto_hours']}h, RPO={option['rpo_hours']}h, "
            f"normalized cost={option['cost_units']}"
        )
    print("Normalized costs are illustrative, not Azure prices.")


if __name__ == "__main__":
    main()