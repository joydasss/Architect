"""Estimate normalized monthly cost from synthetic telemetry volumes."""


def estimate_cost(
    metric_gb_per_day: float,
    log_gb_per_day: float,
    trace_gb_per_day: float,
    retention_days: int,
    metric_rate: float,
    log_rate: float,
    trace_rate: float,
) -> dict[str, float]:
    daily_cost = (
        metric_gb_per_day * metric_rate
        + log_gb_per_day * log_rate
        + trace_gb_per_day * trace_rate
    )
    return {
        "daily": daily_cost,
        "monthly_ingest": daily_cost * 30,
        "retained_gb": (metric_gb_per_day + log_gb_per_day + trace_gb_per_day)
        * retention_days,
    }


def main() -> None:
    result = estimate_cost(2, 35, 12, 30, 0.2, 1.0, 0.5)
    for name, value in result.items():
        print(f"{name}: {value:.1f} normalized units")
    print("Exclude compression, query, export, and provider-specific pricing effects.")


if __name__ == "__main__":
    main()