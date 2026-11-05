"""Cache hit-rate economics, fallback-chain availability, and cost anomaly detection.

Standard library only. All inputs are illustrative. Run: python 04_cache_and_fallback_economics.py
"""
from __future__ import annotations

import statistics


def cache_economics():
    req_per_day = 200_000
    cost_per_call = 0.012            # USD
    lookup_cost = 0.00002            # embedding + vector lookup per request (semantic cache)
    print("cache economics (200,000 requests/day, $0.012 per model call)")
    for name, hit, lookup in [("exact", 0.08, 0.0), ("semantic", 0.30, lookup_cost)]:
        saved = req_per_day * hit * cost_per_call
        spent = req_per_day * lookup
        print(f"  {name:8s} hit {hit:.0%}: saved ${saved:,.2f}/day, lookup ${spent:,.2f}/day, net ${saved - spent:,.2f}/day")
    # Semantic cache false-hit damage: wrong-answer rate on hits
    hit, wrong = 0.30, 0.02
    print(f"  semantic wrong-answer exposure: {req_per_day * hit * wrong:,.0f} wrong cached answers/day at {wrong:.0%} of hits")
    # Break-even hit rate: lookup_cost = h * cost_per_call
    print(f"  break-even hit rate for semantic lookup: {lookup_cost / cost_per_call:.4%}")


def fallback_availability():
    print("\nfallback availability (independent failures assumed, then shared dependency)")
    a_primary, a_alt = 0.995, 0.990
    indep = 1 - (1 - a_primary) * (1 - a_alt)
    print(f"  primary {a_primary:.3%}, alternate {a_alt:.3%}, independent -> {indep:.5%}")
    # 30% of primary outages are shared (same network or auth provider) with the alternate
    shared = 0.30
    p_both_down = (1 - a_primary) * ((1 - a_alt) * (1 - shared) + shared)
    print(f"  with {shared:.0%} correlated outages -> {1 - p_both_down:.5%}")
    minutes = 30 * 24 * 60
    print(f"  downtime per 30 days: independent {(1 - indep) * minutes:.1f} min, correlated {p_both_down * minutes:.1f} min")


def anomaly_detection():
    daily = [410, 395, 402, 420, 388, 405, 399, 412, 407, 940]   # USD per day, last day spike
    base = daily[:-1]
    mu, sd = statistics.mean(base), statistics.pstdev(base)
    z = (daily[-1] - mu) / sd
    print(f"\ncost anomaly: baseline mean ${mu:.1f}, sd ${sd:.1f}, latest ${daily[-1]} -> z = {z:.1f}")
    print("  alert" if z > 4 else "  ok")


if __name__ == "__main__":
    cache_economics()
    fallback_availability()
    anomaly_detection()
