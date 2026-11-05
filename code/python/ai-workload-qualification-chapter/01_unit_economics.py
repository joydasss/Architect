"""Unit economics calculator for an AI workload (standard library only).

Computes cost per decision, value per decision, monthly net value, payback
and break-even volume, then a one-at-a-time sensitivity table.
All inputs are illustrative. Replace them with measured values.

Run: python 01_unit_economics.py
"""
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Inputs:
    volume: int = 40_000            # eligible cases per month
    labor_per_min: float = 0.60     # loaded labor cost, USD per minute
    base_minutes: float = 9.0       # baseline handling time per case
    ai_minutes: float = 6.6         # handling time with an AI draft (incl. review)
    adoption: float = 0.70          # share of cases where the draft is used
    calls_per_case: float = 1.3     # model calls per case (retries, tools)
    in_tokens: int = 3_500          # input tokens per call
    out_tokens: int = 400           # output tokens per call
    price_in_per_m: float = 3.0     # USD per million input tokens (illustrative)
    price_out_per_m: float = 15.0   # USD per million output tokens (illustrative)
    retrieval_per_case: float = 0.004   # search and embedding cost per case
    bad_draft_rate: float = 0.04    # drafts that cause a customer-visible error
    bad_draft_cost: float = 18.00   # remediation cost per bad draft, USD
    build_cost: float = 180_000.0   # one-time build, USD
    amortize_months: int = 24
    run_fixed_month: float = 6_500.0  # evaluation, monitoring, on-call share


def variable_cost(i: Inputs) -> float:
    per_call = (i.in_tokens * i.price_in_per_m + i.out_tokens * i.price_out_per_m) / 1e6
    return per_call * i.calls_per_case + i.retrieval_per_case


def value_per_case(i: Inputs) -> float:
    saved = (i.base_minutes - i.ai_minutes) * i.labor_per_min * i.adoption
    errors = i.bad_draft_rate * i.adoption * i.bad_draft_cost
    return saved - errors


def report(i: Inputs) -> dict:
    var = variable_cost(i)
    gross = value_per_case(i)
    net_case = gross - var
    fixed = i.build_cost / i.amortize_months + i.run_fixed_month
    monthly = net_case * i.volume - fixed
    be = fixed / net_case if net_case > 0 else float("inf")
    payback = (i.build_cost / ((net_case * i.volume) - i.run_fixed_month)
               if net_case * i.volume > i.run_fixed_month else float("inf"))
    return dict(var=var, gross=gross, net_case=net_case, fixed=fixed,
                monthly=monthly, breakeven=be, payback=payback,
                baseline_cost=i.base_minutes * i.labor_per_min)


if __name__ == "__main__":
    base = Inputs()
    r = report(base)
    print("Baseline cost per case:      $%.3f" % r["baseline_cost"])
    print("Variable AI cost per case:   $%.4f" % r["var"])
    print("Gross value per case:        $%.4f" % r["gross"])
    print("Net value per case:          $%.4f" % r["net_case"])
    print("Fixed cost per month:        $%.0f" % r["fixed"])
    print("Net value per month:         $%.0f" % r["monthly"])
    print("Break-even volume per month: %.0f cases" % r["breakeven"])
    print("Payback on build cost:       %.1f months" % r["payback"])
    print()
    print("Sensitivity (one input changed at a time)")
    print("%-34s %12s %14s" % ("change", "net/month", "break-even"))
    cases = [
        ("adoption 0.70 -> 0.40", dict(adoption=0.40)),
        ("ai_minutes 6.6 -> 8.0", dict(ai_minutes=8.0)),
        ("bad_draft_rate 0.04 -> 0.10", dict(bad_draft_rate=0.10)),
        ("token price x2", dict(price_in_per_m=6.0, price_out_per_m=30.0)),
        ("calls_per_case 1.3 -> 4.0", dict(calls_per_case=4.0)),
        ("volume 40000 -> 12000", dict(volume=12_000)),
    ]
    for name, kw in cases:
        rr = report(replace(base, **kw))
        print("%-34s %12.0f %14.0f" % (name, rr["monthly"], rr["breakeven"]))
    print()
    spike = replace(base, ai_minutes=5.8, adoption=0.72, bad_draft_rate=0.015)
    rs = report(spike)
    print("Spike-measured scenario (5.8 min, adoption 0.72, bad drafts 1.5%)")
    print("  net per case $%.5f, net per month $%.0f, break-even %.0f cases, payback %.1f months"
          % (rs["net_case"], rs["monthly"], rs["breakeven"], rs["payback"]))
    low = report(replace(spike, adoption=0.40))
    print("  with adoption 0.40: net per case $%.5f, net per month $%.0f" % (low["net_case"], low["monthly"]))