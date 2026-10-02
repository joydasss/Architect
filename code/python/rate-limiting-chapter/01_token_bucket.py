"""Deterministic token-bucket example with weighted request cost."""

from dataclasses import dataclass
from typing import Callable


@dataclass
class TokenBucket:
    capacity: float
    refill_per_second: float
    clock: Callable[[], float]
    tokens: float
    updated_at: float

    @classmethod
    def full(
        cls,
        capacity: float,
        refill_per_second: float,
        clock: Callable[[], float],
    ) -> "TokenBucket":
        if capacity <= 0 or refill_per_second <= 0:
            raise ValueError("capacity and refill rate must be positive")
        now = clock()
        return cls(capacity, refill_per_second, clock, capacity, now)

    def allow(self, cost: float = 1.0) -> tuple[bool, float]:
        if cost <= 0 or cost > self.capacity:
            raise ValueError("cost must be positive and no greater than capacity")
        now = self.clock()
        elapsed = max(0.0, now - self.updated_at)
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_per_second)
        self.updated_at = max(self.updated_at, now)
        if self.tokens >= cost:
            self.tokens -= cost
            return True, 0.0
        wait = (cost - self.tokens) / self.refill_per_second
        return False, wait


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def main() -> None:
    clock = FakeClock()
    bucket = TokenBucket.full(5, 2, clock)
    outcomes = [bucket.allow() for _ in range(5)]
    assert all(allowed for allowed, _ in outcomes)

    denied, wait = bucket.allow(cost=2)
    assert not denied and wait == 1.0
    clock.advance(wait)
    allowed, _ = bucket.allow(cost=2)
    assert allowed

    print("five initial unit requests: admitted")
    print(f"weighted request rejected; retry after {wait:.1f}s")
    print("weighted request after refill: admitted")


if __name__ == "__main__":
    main()