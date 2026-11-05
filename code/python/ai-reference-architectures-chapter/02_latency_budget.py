"""Online inference: latency budget simulation with timeouts and fallback.

Standard library only; fixed seed so output is reproducible.
Models a request path: auth -> feature read -> model call -> post-process.
Each hop has a lognormal latency. The feature read and model call have
timeouts. On timeout the path uses a deterministic fallback so the request
still finishes inside the deadline. Illustrative numbers, not benchmarks.
"""
import math
import random

random.seed(17)
N = 200_000
DEADLINE_MS = 250


def lognormal(median_ms, sigma):
    return random.lognormvariate(math.log(median_ms), sigma)


def pct(sorted_vals, p):
    return sorted_vals[int(p / 100 * (len(sorted_vals) - 1))]


def simulate(use_timeouts):
    lat, fallbacks, late = [], 0, 0
    for _ in range(N):
        t = lognormal(8, 0.3)                      # auth and routing
        f = lognormal(12, 0.6)                     # online feature read
        if use_timeouts and f > 40:
            f, fell = 40, True
        else:
            fell = False
        m = lognormal(60, 0.7)                     # model call
        if use_timeouts and m > 150:
            m, fell2 = 150, True
        else:
            fell2 = False
        p = lognormal(5, 0.3)                      # validate and persist
        total = t + f + m + p
        if fell or fell2:
            fallbacks += 1
            total += 3                            # rule-based fallback is cheap
        lat.append(total)
        if total > DEADLINE_MS:
            late += 1
    lat.sort()
    return lat, fallbacks / N, late / N


for label, flag in (("no timeouts", False), ("with timeouts", True)):
    lat, fb, late = simulate(flag)
    print(f"{label:<14} p50={pct(lat,50):6.1f} p95={pct(lat,95):6.1f} "
          f"p99={pct(lat,99):6.1f} p99.9={pct(lat,99.9):6.1f} ms  "
          f"fallback={fb*100:5.2f}%  late(>{DEADLINE_MS}ms)={late*100:5.2f}%")
