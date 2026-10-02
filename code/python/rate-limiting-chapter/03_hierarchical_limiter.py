"""Atomic in-process tenant and route token budgets."""

from dataclasses import dataclass
from threading import Lock
from typing import Callable


@dataclass
class Bucket:
    capacity: float
    refill_per_second: float
    tokens: float
    updated_at: float

    def projected(self, now: float) -> float:
        elapsed = max(0.0, now - self.updated_at)
        return min(self.capacity, self.tokens + elapsed * self.refill_per_second)


class HierarchicalLimiter:
    def __init__(self, clock: Callable[[], float]) -> None:
        self.clock = clock
        self.lock = Lock()
        self.tenants: dict[str, Bucket] = {}
        self.routes: dict[tuple[str, str], Bucket] = {}

    def add_tenant(self, tenant: str, capacity: float, refill: float) -> None:
        now = self.clock()
        self.tenants[tenant] = Bucket(capacity, refill, capacity, now)

    def add_route(self, tenant: str, route: str, capacity: float, refill: float) -> None:
        now = self.clock()
        self.routes[(tenant, route)] = Bucket(capacity, refill, capacity, now)

    def allow(self, tenant: str, route: str, cost: float = 1.0) -> bool:
        now = self.clock()
        with self.lock:
            tenant_bucket = self.tenants[tenant]
            route_bucket = self.routes[(tenant, route)]
            tenant_tokens = tenant_bucket.projected(now)
            route_tokens = route_bucket.projected(now)
            if tenant_tokens < cost or route_tokens < cost:
                return False

            tenant_bucket.tokens = tenant_tokens - cost
            tenant_bucket.updated_at = now
            route_bucket.tokens = route_tokens - cost
            route_bucket.updated_at = now
            return True


def main() -> None:
    now = [0.0]
    limiter = HierarchicalLimiter(lambda: now[0])
    limiter.add_tenant("acme", capacity=3, refill=1)
    limiter.add_route("acme", "/search", capacity=1, refill=0.1)

    assert limiter.allow("acme", "/search")
    tenant_tokens = limiter.tenants["acme"].tokens
    assert not limiter.allow("acme", "/search")
    assert limiter.tenants["acme"].tokens == tenant_tokens

    now[0] = 10.0
    assert limiter.allow("acme", "/search")
    print("first tenant+route request: admitted")
    print("route exhausted: rejected without debiting tenant budget")
    print("after route refill: admitted")


if __name__ == "__main__":
    main()