"""Simulate a canary rollout with a latency/error-rate health gate."""


def assess_canary(
    error_rate: float, latency_ms: float, max_error_rate: float, max_latency_ms: float
) -> tuple[bool, list[str]]:
    failures = []
    if error_rate > max_error_rate:
        failures.append(f"error rate {error_rate:.2%} exceeds {max_error_rate:.2%}")
    if latency_ms > max_latency_ms:
        failures.append(f"latency {latency_ms:.0f}ms exceeds {max_latency_ms:.0f}ms")
    return not failures, failures


def main() -> None:
    observations = [
        {"name": "canary-1", "error_rate": 0.004, "latency_ms": 180},
        {"name": "canary-2", "error_rate": 0.031, "latency_ms": 240},
    ]
    for observation in observations:
        healthy, failures = assess_canary(
            observation["error_rate"],
            observation["latency_ms"],
            max_error_rate=0.01,
            max_latency_ms=220,
        )
        print(f"{observation['name']}: {'continue' if healthy else 'halt rollout'}")
        for failure in failures:
            print(f"  {failure}")


if __name__ == "__main__":
    main()