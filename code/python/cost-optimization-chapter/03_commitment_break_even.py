"""Compare pay-as-you-go and committed cost at different utilization rates."""


def compare_costs(
    commitment_capacity_hours: float,
    on_demand_rate: float,
    commitment_rate: float,
    utilization: float,
) -> tuple[float, float]:
    used_hours = commitment_capacity_hours * utilization
    on_demand_cost = used_hours * on_demand_rate
    fixed_commitment_cost = commitment_capacity_hours * commitment_rate
    return on_demand_cost, fixed_commitment_cost


def main() -> None:
    hours = 720
    commitment_capacity_hours = 8 * hours
    for utilization in (0.55, 0.8, 1.0):
        on_demand, committed = compare_costs(
            commitment_capacity_hours=commitment_capacity_hours,
            on_demand_rate=1.0,
            commitment_rate=0.68,
            utilization=utilization,
        )
        print(
            f"utilization={utilization:.0%}: on-demand={on_demand:.0f}, "
            f"commitment={committed:.0f} normalized units"
        )
    print("Model product eligibility, term, scope, and unused capacity before buying.")


if __name__ == "__main__":
    main()