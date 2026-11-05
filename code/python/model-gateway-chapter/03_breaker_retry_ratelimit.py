"""Circuit breaker simulation, retry amplification, and token-bucket arithmetic.

Standard library only; deterministic (seeded). Run: python 03_breaker_retry_ratelimit.py
"""
from __future__ import annotations

import random


class Breaker:
    """closed -> open (on failure rate) -> half_open (after cooldown) -> closed."""

    def __init__(self, window=20, min_calls=10, threshold=0.5, cooldown=15, probes=3):
        self.window, self.min_calls, self.threshold = window, min_calls, threshold
        self.cooldown, self.probes = cooldown, probes
        self.state, self.results, self.opened_at = "closed", [], 0
        self.probe_ok = 0

    def allow(self, t):
        if self.state == "open" and t - self.opened_at >= self.cooldown:
            self.state, self.probe_ok = "half_open", 0
        return self.state != "open"

    def record(self, t, ok):
        if self.state == "half_open":
            if not ok:
                self.state, self.opened_at = "open", t
            else:
                self.probe_ok += 1
                if self.probe_ok >= self.probes:
                    self.state, self.results = "closed", []
            return
        self.results = (self.results + [ok])[-self.window:]
        if len(self.results) >= self.min_calls:
            fail = 1 - sum(self.results) / len(self.results)
            if fail >= self.threshold:
                self.state, self.opened_at = "open", t


def simulate():
    rng = random.Random(7)
    b = Breaker()
    sent_with, sent_without, log, last = 0, 0, [], "closed"
    for t in range(0, 90):                      # one request per second
        outage = 20 <= t < 50                   # provider fails 100% in this window
        sent_without += 1
        if b.allow(t):
            sent_with += 1
            ok = (not outage) and rng.random() > 0.01
            b.record(t, ok)
        if b.state != last:
            log.append((t, b.state))
            last = b.state
    print("breaker transitions (t, state):", log)
    print(f"calls reaching provider: with breaker {sent_with}, without {sent_without}")


def retry_amplification():
    # Two layers each retrying up to 3 attempts total (1 + 2 retries)
    attempts = 3
    layers = 2
    worst = attempts ** layers
    print(f"\nretry amplification: {attempts} attempts per layer x {layers} layers = {worst}x worst case")
    # With failure probability p at the provider, expected calls per user request
    for p in (0.05, 0.5, 1.0):
        per_layer = sum(p ** k for k in range(attempts))   # 1 + p + p^2
        print(f"  p={p:.2f}: expected provider calls per request, 1 layer {per_layer:.3f}, 2 layers {per_layer ** 2:.3f}")
    # Retry budget: allow retries only up to 10% of first attempts
    first, budget = 1000, 0.10
    print(f"  retry budget {budget:.0%}: at most {int(first * budget)} retries per {first} first attempts")


class TokenBucket:
    def __init__(self, rate_per_s, burst):
        self.rate, self.burst, self.tokens, self.t = rate_per_s, burst, burst, 0.0

    def take(self, t, cost):
        self.tokens = min(self.burst, self.tokens + (t - self.t) * self.rate)
        self.t = t
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False


def bucket_demo():
    # 600,000 tokens/minute = 10,000 tokens/s refill, burst 60,000 tokens
    tb = TokenBucket(10_000, 60_000)
    print("\ntoken bucket: refill 10,000 tok/s, burst 60,000 tok")
    events = [(0.0, 20_000), (0.1, 20_000), (0.2, 20_000), (0.3, 20_000),
              (2.3, 20_000), (4.3, 20_000)]
    for t, c in events:
        print(f"  t={t:4.1f}s request of {c:6d} tokens -> {'admit' if tb.take(t, c) else 'reject'}"
              f" (tokens left {tb.tokens:,.0f})")


if __name__ == "__main__":
    simulate()
    retry_amplification()
    bucket_demo()
