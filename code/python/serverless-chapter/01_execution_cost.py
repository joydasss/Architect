"""Estimate normalized function execution cost from synthetic inputs."""


def estimate_cost(
    invocations: int,
    average_duration_ms: float,
    memory_gib: float,
    request_rate_per_million: float,
    compute_rate_per_gib_second: float,
) -> dict[str, float]:
    gib_seconds = invocations * (average_duration_ms / 1000) * memory_gib
    request_cost = invocations / 1_000_000 * request_rate_per_million
    compute_cost = gib_seconds * compute_rate_per_gib_second
    return {
        "gib_seconds": gib_seconds,
        "request_cost_units": request_cost,
        "compute_cost_units": compute_cost,
        "total_cost_units": request_cost + compute_cost,
    }


def main() -> None:
    result = estimate_cost(
        invocations=8_000_000,
        average_duration_ms=180,
        memory_gib=0.5,
        request_rate_per_million=0.2,
        compute_rate_per_gib_second=0.00002,
    )
    for name, value in result.items():
        print(f"{name}: {value:.2f}")
    print("Normalized rates are illustrative, not provider prices.")


if __name__ == "__main__":
    main()