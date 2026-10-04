"""Estimate data exposure from replication lag at a simulated failure."""


def estimate_rpo_seconds(
    observed_lag_seconds: float, failure_detection_seconds: float
) -> float:
    return observed_lag_seconds + failure_detection_seconds


def estimate_unreplicated_records(
    write_rate_per_second: float, rpo_seconds: float
) -> int:
    return int(write_rate_per_second * rpo_seconds)


def main() -> None:
    write_rate = 120
    observed_lag = 8
    detection_delay = 5
    rpo = estimate_rpo_seconds(observed_lag, detection_delay)
    records_at_risk = estimate_unreplicated_records(write_rate, rpo)
    print(f"Estimated RPO: {rpo:.1f} seconds")
    print(f"Approximate records not yet replicated: {records_at_risk}")
    print("Real recovery behavior depends on service consistency and failover semantics.")


if __name__ == "__main__":
    main()