"""Worked numbers: moderation layer trade-offs and denial-of-wallet budgets.

Standard library only. All rates and prices are illustrative.
Run: python 04_safeguard_tradeoffs_and_budgets.py
"""
from __future__ import annotations


def layer(name, volume, prevalence, recall, fpr, latency_ms):
    pos = volume * prevalence
    neg = volume - pos
    tp = pos * recall
    fp = neg * fpr
    fn = pos - tp
    precision = tp / (tp + fp)
    print(f"{name:22} TP={tp:7.0f} FP={fp:8.0f} FN={fn:6.0f} precision={precision:.3f} recall={recall:.2f} +{latency_ms}ms")
    return tp, fp, fn


def main():
    volume, prev = 1_000_000, 0.002  # 1M requests, 0.2% harmful (illustrative)
    print("Single classifier at three thresholds (1M requests, 0.2% harmful)")
    layer("strict (t=0.3)", volume, prev, 0.98, 0.050, 30)
    layer("balanced (t=0.5)", volume, prev, 0.92, 0.010, 30)
    layer("lenient (t=0.8)", volume, prev, 0.75, 0.001, 30)

    print("\nTwo layers in series, block if either flags (independence assumed)")
    r1, f1 = 0.92, 0.010
    r2, f2 = 0.70, 0.005
    recall = 1 - (1 - r1) * (1 - r2)
    fpr = 1 - (1 - f1) * (1 - f2)
    layer("either-flags", volume, prev, recall, fpr, 30 + 30)

    print("\nHuman review load for the balanced classifier at 1M/day")
    flagged = volume * prev * 0.92 + volume * (1 - prev) * 0.010
    minutes = flagged * 1.5
    print(f"flagged/day={flagged:.0f}, review minutes at 1.5 min each={minutes:.0f}, reviewers (6h)={minutes / 360:.1f}")

    print("\nDenial-of-wallet: one request cost with an agent loop (illustrative prices)")
    in_price, out_price = 3.0, 15.0  # USD per million tokens
    steps, in_tok, out_tok = 20, 12_000, 800
    cost = steps * (in_tok * in_price + out_tok * out_price) / 1e6
    print(f"uncapped 20-step loop: ${cost:.2f} per request")
    capped = 6 * (in_tok * in_price + out_tok * out_price) / 1e6
    print(f"capped at 6 steps:     ${capped:.2f} per request")
    attackers, per_min = 50, 10
    hourly = attackers * per_min * 60 * cost
    print(f"50 clients x 10 req/min uncapped for 1 hour: ${hourly:,.0f}")
    budget = 200.0
    print(f"per-tenant hourly budget ${budget:.0f} caps loss at 1 tenant: ${budget:.0f}")


if __name__ == "__main__":
    main()
