"""Generic Cell Rate Algorithm (GCRA) with deterministic time."""

from dataclasses import dataclass


@dataclass
class GCRA:
    interval: float
    burst_tolerance: float
    theoretical_arrival: float

    def __post_init__(self) -> None:
        if self.interval <= 0 or self.burst_tolerance < 0:
            raise ValueError("interval must be positive and burst non-negative")

    def allow(self, now: float, cost: int = 1) -> tuple[bool, float]:
        if cost <= 0:
            raise ValueError("cost must be positive")
        earliest_allowed = self.theoretical_arrival - self.burst_tolerance
        if now < earliest_allowed:
            return False, earliest_allowed - now
        self.theoretical_arrival = max(self.theoretical_arrival, now) + cost * self.interval
        return True, 0.0


def main() -> None:
    limiter = GCRA(interval=1.0, burst_tolerance=2.0, theoretical_arrival=0.0)
    first = limiter.allow(0.0)
    second = limiter.allow(0.0)
    third = limiter.allow(0.0)
    fourth = limiter.allow(0.0)
    assert [item[0] for item in (first, second, third, fourth)] == [True, True, True, False]
    assert fourth[1] == 1.0

    after_wait = limiter.allow(1.0)
    assert after_wait[0]
    print("three immediate arrivals: admitted within burst tolerance")
    print(f"fourth arrival: rejected for {fourth[1]:.1f}s")
    print("arrival at next eligible time: admitted")


if __name__ == "__main__":
    main()