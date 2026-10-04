"""Estimate instance count and normalized monthly cost from load inputs."""

from math import ceil


def estimate_fleet(
    peak_requests_per_second: int,
    requests_per_second_per_instance: int,
    headroom_factor: float,
    hourly_cost_units: float,
) -> tuple[int, float]:
    safe_capacity = requests_per_second_per_instance / headroom_factor
    instance_count = ceil(peak_requests_per_second / safe_capacity)
    monthly_cost = instance_count * hourly_cost_units * 24 * 30
    return instance_count, monthly_cost


def main() -> None:
    instance_count, monthly_cost = estimate_fleet(
        peak_requests_per_second=4800,
        requests_per_second_per_instance=400,
        headroom_factor=1.5,
        hourly_cost_units=0.8,
    )
    print(f"Instances required at peak: {instance_count}")
    print(f"Normalized monthly cost units: {monthly_cost:.1f}")
    print("Validate throughput with load tests; cost units are not provider prices.")


if __name__ == "__main__":
    main()