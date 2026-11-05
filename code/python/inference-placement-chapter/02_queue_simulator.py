"""Queue simulator for an LLM serving pool (standard library only).

Models a pool of c identical replicas, each serving one request at a time
(a simplification: real engines batch, see Part 16 CH28). Arrivals are Poisson
with rate lambda. Service times are lognormal to mimic variable output length.
Prints utilization, mean and p95/p99 wait, and checks Little's Law L = lambda*W.
Also prints the analytic Erlang-C result for exponential service as a check.
"""

import heapq
import math
import random


def erlang_c_wait(lam, mu, c):
    """Mean wait in queue (Wq) for M/M/c."""
    a = lam / mu
    rho = a / c
    if rho >= 1:
        return float("inf")
    s = sum(a ** k / math.factorial(k) for k in range(c))
    top = a ** c / (math.factorial(c) * (1 - rho))
    p_wait = top / (s + top)
    return p_wait / (c * mu - lam)


def simulate(lam, c, mean_service, sigma, n=60000, seed=7):
    rng = random.Random(seed)
    mu_ln = math.log(mean_service) - sigma ** 2 / 2   # so the mean is mean_service
    free = [0.0] * c
    heapq.heapify(free)
    t = 0.0
    waits, sojourns = [], []
    busy = 0.0
    last_depart = 0.0
    arrivals = []
    for _ in range(n):
        t += rng.expovariate(lam)
        s = rng.lognormvariate(mu_ln, sigma) if sigma > 0 else rng.expovariate(1 / mean_service)
        earliest = heapq.heappop(free)
        start = max(t, earliest)
        depart = start + s
        heapq.heappush(free, depart)
        waits.append(start - t)
        sojourns.append(depart - t)
        busy += s
        last_depart = max(last_depart, depart)
        arrivals.append(t)
    horizon = last_depart
    util = busy / (c * horizon)
    waits_sorted = sorted(waits)
    mean_w = sum(sojourns) / n
    lam_obs = n / arrivals[-1]
    L = sum(sojourns) / horizon        # time-average number in system
    return {
        "util": util,
        "mean_wait": sum(waits) / n,
        "p95_wait": waits_sorted[int(0.95 * n)],
        "p99_wait": waits_sorted[int(0.99 * n)],
        "mean_sojourn": mean_w,
        "L": L,
        "lam_W": lam_obs * mean_w,
    }


def main():
    c = 8
    mean_service = 10.0   # seconds per request on one replica (illustrative)
    mu = 1 / mean_service
    print(f"replicas c={c}, mean service={mean_service}s, capacity={c * mu:.2f} req/s")
    print(f"{'target util':>11} {'lam':>6} {'Wq analytic':>12} {'mean wait':>10} "
          f"{'p95 wait':>9} {'p99 wait':>9} {'L':>6} {'lam*W':>6}")
    for rho in (0.5, 0.7, 0.8, 0.9, 0.95):
        lam = rho * c * mu
        r = simulate(lam, c, mean_service, sigma=0.8)
        wq = erlang_c_wait(lam, mu, c)
        print(f"{rho:>11.2f} {lam:>6.3f} {wq:>12.2f} {r['mean_wait']:>10.2f} "
              f"{r['p95_wait']:>9.2f} {r['p99_wait']:>9.2f} {r['L']:>6.2f} {r['lam_W']:>6.2f}")
    print("Wq analytic assumes exponential service; the simulation uses lognormal")
    print("service (sigma=0.8), which has a higher variance and so waits longer.")


if __name__ == "__main__":
    main()
