"""Reviewer staffing: Little's Law, Erlang C, and a queue simulation check.

Standard library only. Reviews arrive as a Poisson process and handling times
are exponential (an M/M/c queue). Real handling times are skewed, so treat the
formulas as a floor and confirm with the simulation or production data.
"""
import heapq
import math
import random


def erlang_c(c: int, a: float) -> float:
    """Probability an arriving review has to wait. a = lambda / mu (Erlangs)."""
    if a >= c:
        return 1.0
    term = 1.0
    total = 1.0
    for k in range(1, c):
        term *= a / k
        total += term
    last = term * a / c * (c / (c - a))
    return last / (total + last)


def mmc(lam_per_hr: float, handle_min: float, c: int) -> dict:
    mu = 60.0 / handle_min               # reviews per hour per reviewer
    a = lam_per_hr / mu                  # offered load in Erlangs
    rho = a / c
    if rho >= 1:
        return {"c": c, "rho": rho, "pwait": 1.0, "wq_min": math.inf, "p95_min": math.inf}
    pw = erlang_c(c, a)
    wq_hr = pw / (c * mu - lam_per_hr)   # mean wait in queue
    # Waiting time tail: P(W > t) = pw * exp(-(c*mu - lam) * t)
    rate = c * mu - lam_per_hr
    p95 = max(0.0, math.log(pw / 0.05) / rate) if pw > 0.05 else 0.0
    return {"c": c, "rho": rho, "pwait": pw, "wq_min": wq_hr * 60, "p95_min": p95 * 60}


def simulate(lam_per_hr: float, handle_min: float, c: int, n: int, seed: int) -> float:
    rng = random.Random(seed)
    free = [0.0] * c
    heapq.heapify(free)
    t = 0.0
    waits = []
    for _ in range(n):
        t += rng.expovariate(lam_per_hr)               # hours
        start = max(t, heapq.heappop(free))
        waits.append((start - t) * 60)
        heapq.heappush(free, start + rng.expovariate(60.0 / handle_min))
    return sum(waits) / len(waits)


def main() -> None:
    lam, handle = 90.0, 6.0   # 90 reviews/hour, 6 minutes each => 9 Erlangs
    print(f"Arrivals {lam}/hr, handling {handle} min => offered load "
          f"{lam * handle / 60:.1f} Erlangs")
    print(f"Little's Law: average cases in service = lambda x W = "
          f"{lam} x {handle / 60:.2f} h = {lam * handle / 60:.1f}")
    print(f"{'reviewers':>9} {'utilization':>11} {'P(wait)':>8} "
          f"{'mean wait min':>13} {'p95 wait min':>12}")
    for c in range(10, 16):
        m = mmc(lam, handle, c)
        print(f"{c:>9} {m['rho']:>11.1%} {m['pwait']:>8.2f} "
              f"{m['wq_min']:>13.1f} {m['p95_min']:>12.1f}")
    # Smallest team meeting: 95th percentile wait <= 15 minutes, utilization <= 80%.
    for c in range(1, 100):
        m = mmc(lam, handle, c)
        if m["rho"] <= 0.80 and m["p95_min"] <= 15:
            print(f"\nSmallest team with p95 wait <= 15 min and utilization <= 80%: {c}")
            break
    print("\nSimulation check (mean wait, minutes), 200000 reviews:")
    for c in (11, 12, 14):
        print(f"  c={c}: formula {mmc(lam, handle, c)['wq_min']:.2f}, "
              f"simulation {simulate(lam, handle, c, 200_000, 7):.2f}")
    print("\nEffect of a 25 percent rise in handling time (6.0 -> 7.5 min), c=12:")
    for h in (6.0, 7.5):
        m = mmc(lam, h, 12)
        print(f"  handling {h} min: utilization {m['rho']:.1%}, "
              f"mean wait {m['wq_min']:.1f} min")


if __name__ == "__main__":
    main()
