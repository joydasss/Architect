"""Estimate concurrency from arrival rate and protect a downstream pool."""


def required_concurrency(arrivals_per_second: float, duration_seconds: float) -> float:
    return arrivals_per_second * duration_seconds


def plan_concurrency(
    arrivals_per_second: float,
    duration_seconds: float,
    downstream_connection_budget: int,
    connections_per_invocation: int,
) -> tuple[float, int]:
    demand = required_concurrency(arrivals_per_second, duration_seconds)
    safe_limit = downstream_connection_budget // connections_per_invocation
    return demand, safe_limit


def main() -> None:
    demand, safe_limit = plan_concurrency(
        arrivals_per_second=240,
        duration_seconds=0.8,
        downstream_connection_budget=120,
        connections_per_invocation=2,
    )
    print(f"Estimated concurrency demand: {demand:.0f}")
    print(f"Safe function concurrency from downstream budget: {safe_limit}")
    print("Buffer excess demand or return controlled throttling responses.")


if __name__ == "__main__":
    main()