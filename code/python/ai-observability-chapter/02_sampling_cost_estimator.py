"""Estimate trace storage volume and cost under sampling and retention tiers.

Standard library only. Run: python 02_sampling_cost_estimator.py

All inputs are illustrative. Replace them with your own measurements and your
storage vendor's price list.
"""
from __future__ import annotations

REQUESTS_PER_DAY = 2_000_000
ERROR_RATE = 0.02            # requests with a hard error or failed validation
LOW_QUALITY_RATE = 0.05      # requests flagged by automated checks or user signal
META_KB = 6                  # span metadata per request, no content
CONTENT_KB = 28              # prompts, retrieved text, output, tool I/O (about 4 chars/token)
HOT_DAYS, WARM_DAYS = 14, 76  # hot 14 d, warm until day 90
HOT_USD_GB_MONTH = 0.10      # indexed, queryable store (illustrative)
WARM_USD_GB_MONTH = 0.023    # object storage (illustrative)
BASE_RATE = 0.01             # head sampling of content for healthy traffic

GB = 1024 * 1024  # KB per GB


def daily_gb(kb_per_req: float, n: float) -> float:
    return kb_per_req * n / GB


def strategy(name: str, content_fraction: float) -> dict:
    meta_gb = daily_gb(META_KB, REQUESTS_PER_DAY)
    content_gb = daily_gb(CONTENT_KB, REQUESTS_PER_DAY * content_fraction)
    day_gb = meta_gb + content_gb
    # Steady state: hot holds HOT_DAYS of data, warm holds WARM_DAYS of data.
    hot = day_gb * HOT_DAYS * HOT_USD_GB_MONTH
    warm = day_gb * WARM_DAYS * WARM_USD_GB_MONTH
    return {"name": name, "content_pct": content_fraction * 100, "gb_day": day_gb,
            "usd_month": hot + warm}


if __name__ == "__main__":
    healthy = 1 - ERROR_RATE - LOW_QUALITY_RATE
    rows = [
        strategy("capture everything", 1.0),
        strategy("head 1% only", BASE_RATE),
        strategy("error-biased (all errors + 1% rest)",
                 ERROR_RATE + (1 - ERROR_RATE) * BASE_RATE),
        strategy("error+quality-biased (all flagged + 1% healthy)",
                 ERROR_RATE + LOW_QUALITY_RATE + healthy * BASE_RATE),
    ]
    print(f"{'strategy':52s} {'content%':>8s} {'GB/day':>8s} {'USD/month':>10s}")
    for r in rows:
        print(f"{r['name']:52s} {r['content_pct']:8.2f} {r['gb_day']:8.1f} {r['usd_month']:10.0f}")

    # Estimator precision for a healthy-traffic quality rate p from n sampled traces.
    p, n = 0.04, 20_000 * BASE_RATE * 7  # 20k healthy-slice requests/day for a week, 1% sampled
    import math
    se = math.sqrt(p * (1 - p) / n)
    print(f"\nweekly sampled traces n={n:.0f}, p={p}: 95% half-width = {1.96 * se:.4f}")
