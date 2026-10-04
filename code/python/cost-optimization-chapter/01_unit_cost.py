"""Allocate synthetic shared costs and compute cost per successful outcome."""


USAGE = {
    "orders": {"direct": 7200.0, "shared_units": 60, "successful_orders": 120_000},
    "catalog": {"direct": 4100.0, "shared_units": 40, "successful_orders": 500_000},
}
SHARED_COST = 2400.0


def allocate_costs(
    usage: dict[str, dict[str, float]], shared_cost: float
) -> dict[str, dict[str, float]]:
    total_units = sum(item["shared_units"] for item in usage.values())
    allocated = {}
    for name, item in usage.items():
        share = shared_cost * item["shared_units"] / total_units
        total = item["direct"] + share
        unit_cost = total / item["successful_orders"]
        allocated[name] = {"shared": share, "total": total, "per_success": unit_cost}
    return allocated


def main() -> None:
    for workload, cost in allocate_costs(USAGE, SHARED_COST).items():
        print(
            f"{workload}: total={cost['total']:.2f}, "
            f"shared={cost['shared']:.2f}, per success={cost['per_success']:.5f}"
        )


if __name__ == "__main__":
    main()