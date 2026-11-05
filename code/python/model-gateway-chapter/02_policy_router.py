"""Hard-constraint filter, then scored selection, plus cost/quality arithmetic.

Standard library only. Prices, quality and latency are illustrative.
Run: python 02_policy_router.py
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Route:
    name: str
    region: str
    classes: tuple          # data classes allowed
    tier: int               # 1 small, 2 medium, 3 large
    in_price: float         # USD per 1M input tokens (illustrative)
    out_price: float        # USD per 1M output tokens (illustrative)
    quality: float          # pass rate on the task's golden set
    p95_ms: int
    healthy: bool = True


ROUTES = [
    Route("small-eu", "eu", ("public", "internal"), 1, 0.20, 0.80, 0.82, 900),
    Route("mid-eu", "eu", ("public", "internal", "restricted"), 2, 1.00, 4.00, 0.91, 1800),
    Route("large-eu", "eu", ("public", "internal", "restricted"), 3, 5.00, 20.00, 0.95, 3500),
    Route("mid-us", "us", ("public", "internal"), 2, 0.90, 3.60, 0.91, 1600),
    Route("large-us", "us", ("public", "internal"), 3, 4.50, 18.00, 0.95, 3200),
]


def cost(route: Route, in_tok: int, out_tok: int) -> float:
    return (in_tok * route.in_price + out_tok * route.out_price) / 1_000_000


def eligible(routes, data_class, region, deadline_ms, min_quality):
    """Hard constraints only. Returns (kept, rejected_with_reason)."""
    kept, why = [], {}
    for r in routes:
        if data_class not in r.classes:
            why[r.name] = "data_class"
        elif region and r.region != region:
            why[r.name] = "residency"
        elif not r.healthy:
            why[r.name] = "unhealthy"
        elif r.p95_ms > deadline_ms:
            why[r.name] = "latency"
        elif r.quality < min_quality:
            why[r.name] = "quality"
        else:
            kept.append(r)
    return kept, why


def choose(routes, in_tok, out_tok, w_cost=1.0, w_lat=0.0001):
    """Cheapest expected cost per *successful* answer, latency as tiebreak."""
    def score(r):
        return cost(r, in_tok, out_tok) / r.quality + w_lat * r.p95_ms * 1e-3
    return min(routes, key=score) if routes else None


if __name__ == "__main__":
    in_tok, out_tok = 3000, 400
    print("per-request cost (3000 in / 400 out):")
    for r in ROUTES:
        print(f"  {r.name:9s} ${cost(r, in_tok, out_tok):.5f}  "
              f"per-success ${cost(r, in_tok, out_tok) / r.quality:.5f}")

    cases = [
        ("public FAQ, any region, 3s, q>=0.80", "public", None, 3000, 0.80),
        ("restricted, EU only, 4s, q>=0.90", "restricted", "eu", 4000, 0.90),
        ("restricted, EU only, 1s, q>=0.90", "restricted", "eu", 1000, 0.90),
        ("internal, any, 5s, q>=0.94", "internal", None, 5000, 0.94),
    ]
    for label, dc, reg, dl, q in cases:
        kept, why = eligible(ROUTES, dc, reg, dl, q)
        pick = choose(kept, in_tok, out_tok)
        print(f"\n{label}\n  rejected: {why}\n  chosen: {pick.name if pick else 'NONE -> declared fallback'}")

    # Blended-cost arithmetic for a 70/25/5 tier mix vs everything on large
    mix = {"small-eu": 0.70, "mid-eu": 0.25, "large-eu": 0.05}
    by = {r.name: r for r in ROUTES}
    blended = sum(share * cost(by[n], in_tok, out_tok) for n, share in mix.items())
    allbig = cost(by["large-eu"], in_tok, out_tok)
    q_blend = sum(share * by[n].quality for n, share in mix.items())
    print(f"\nblended ${blended:.5f} vs all-large ${allbig:.5f} "
          f"(saving {100 * (1 - blended / allbig):.1f}%), "
          f"blended quality {q_blend:.3f} vs {by['large-eu'].quality}")
