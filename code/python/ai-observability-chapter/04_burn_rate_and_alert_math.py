"""Burn-rate and alert sample-size arithmetic for AI quality SLOs.

Standard library only. Run: python 04_burn_rate_and_alert_math.py
"""
from __future__ import annotations

import math

SLO = 0.97                 # 97% of sampled requests are "good"
BUDGET = 1 - SLO           # 3% bad events allowed
WINDOW_DAYS = 30


def burn_rate(bad_fraction: float) -> float:
    return bad_fraction / BUDGET


def hours_to_exhaust(rate: float) -> float:
    return WINDOW_DAYS * 24 / rate


def min_n_for_shift(p0: float, p1: float, alpha: float = 0.05, power: float = 0.8) -> int:
    """One-sided two-proportion style sample size against a fixed baseline p0."""
    za = {0.05: 1.645, 0.01: 2.326}[alpha]
    zb = {0.8: 0.842, 0.9: 1.282}[power]
    num = (za * math.sqrt(p0 * (1 - p0)) + zb * math.sqrt(p1 * (1 - p1))) ** 2
    return math.ceil(num / (p1 - p0) ** 2)


if __name__ == "__main__":
    print("budget fraction:", BUDGET)
    for bad in (0.03, 0.09, 0.18, 0.43):
        r = burn_rate(bad)
        print(f"bad={bad:.2f} burn rate={r:5.2f}  budget gone in {hours_to_exhaust(r):7.1f} h")
    print("\nsample size to detect p0 -> p1 (alpha 0.05, power 0.8):")
    for p0, p1 in ((0.03, 0.05), (0.03, 0.06), (0.03, 0.09)):
        print(f"  {p0:.2f} -> {p1:.2f}: n = {min_n_for_shift(p0, p1)}")

    # Multi-window check: page when 1h and 5min windows both exceed 14.4x.
    sampled_per_hour = 600
    bad_in_hour = 270
    frac = bad_in_hour / sampled_per_hour
    print(f"\n1h window: {bad_in_hour}/{sampled_per_hour} bad = {frac:.3f}, burn {burn_rate(frac):.2f}")

    # False alarms: naive per-check alpha across many slices and checks.
    checks_per_day, slices = 24, 12
    alpha = 0.05
    expected = checks_per_day * slices * alpha
    print(f"naive alpha={alpha}: {checks_per_day * slices} tests/day -> {expected:.1f} false alarms/day")
    alpha_b = alpha / (checks_per_day * slices)
    print(f"Bonferroni alpha per test = {alpha_b:.6f}")
