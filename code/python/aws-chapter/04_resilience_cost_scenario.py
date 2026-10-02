"""Compare normalized resilience patterns without using live AWS prices."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Pattern:
    name: str
    monthly_cost_units: int
    recovery_minutes: int
    data_loss_minutes: int


def meets(pattern: Pattern, recovery_objective: int, loss_objective: int) -> bool:
    return pattern.recovery_minutes <= recovery_objective and pattern.data_loss_minutes <= loss_objective


def main() -> None:
    patterns = [
        Pattern("backup and restore", monthly_cost_units=1, recovery_minutes=360, data_loss_minutes=60),
        Pattern("pilot light", monthly_cost_units=3, recovery_minutes=90, data_loss_minutes=15),
        Pattern("warm standby", monthly_cost_units=7, recovery_minutes=20, data_loss_minutes=5),
        Pattern("active-active", monthly_cost_units=14, recovery_minutes=2, data_loss_minutes=1),
    ]
    recovery_objective = 30
    data_loss_objective = 5
    eligible = [p for p in patterns if meets(p, recovery_objective, data_loss_objective)]
    selected = min(eligible, key=lambda pattern: pattern.monthly_cost_units)

    for pattern in patterns:
        print(
            f"{pattern.name}: cost-units={pattern.monthly_cost_units}, "
            f"RTO={pattern.recovery_minutes}m, RPO={pattern.data_loss_minutes}m, "
            f"meets-objectives={meets(pattern, recovery_objective, data_loss_objective)}"
        )
    print("lowest-cost eligible pattern:", selected.name)
    assert selected.name == "warm standby"


if __name__ == "__main__":
    main()
