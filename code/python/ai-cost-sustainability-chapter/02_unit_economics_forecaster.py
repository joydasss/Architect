"""Unit economics (cost per successful outcome, margin, break-even,
sensitivity) and a usage-based spend forecaster (growth, context growth,
power users, heavy-tail requests).

Standard library only. All numbers are ILLUSTRATIVE assumptions.

Run: python 02_unit_economics_forecaster.py
"""
import math
import random


# ---------------------------------------------------------------- unit economics
def cost_per_outcome(model_cost, retry_rate, success_rate, review_rate,
                     review_cost, escalation_cost, fixed_per_case=0.0):
    """Cost per successful outcome.

    model_cost      model + retrieval + overhead cost of one attempt (USD)
    retry_rate      fraction of cases that need one extra automatic attempt
    success_rate    fraction of cases the AI path resolves without a human taking over
    review_rate     fraction of cases a human spot-checks (cost review_cost each)
    escalation_cost cost of a human handling a case the AI did not resolve
    """
    attempts = 1 + retry_rate
    ai_cost = attempts * model_cost + review_rate * review_cost + fixed_per_case
    rework = (1 - success_rate) * escalation_cost
    per_case = ai_cost + rework
    return per_case, per_case / success_rate, attempts, ai_cost


def unit_economics():
    print("== Unit economics: support assistant (illustrative) ==")
    per_case, per_outcome, attempts, ai_cost = cost_per_outcome(
        model_cost=0.021, retry_rate=0.15, success_rate=0.70,
        review_rate=0.05, review_cost=0.60, escalation_cost=4.50)
    print(f"attempts per case          {attempts:.2f}")
    print(f"AI-path cost per case       ${ai_cost:.4f}")
    print(f"cost per case incl. rework ${per_case:.4f}")
    print(f"cost per successful outcome ${per_outcome:.4f}")
    naive = cost_per_outcome(0.021, 0.15, 0.70, 0.05, 0.60, 4.50)[1]
    cheap = cost_per_outcome(0.004, 0.15, 0.55, 0.05, 0.60, 4.50)[1]
    print(f"cheaper model (cost 0.004, success 0.55): ${cheap:.4f} vs ${naive:.4f}")

    print("\n-- Gross margin per feature (per-seat pricing) --")
    price = 30.0
    for label, cases in (("average user", 120), ("heavy user", 900),
                         ("power user", 3000)):
        cost = cases * ai_cost
        print(f"{label:<13} {cases:>5} cases/mo cost ${cost:>8.2f} "
              f"margin ${price - cost:>8.2f} ({100 * (price - cost) / price:6.1f}%)")
    mix = {"average user": (0.80, 120), "heavy user": (0.17, 900),
           "power user": (0.03, 3000)}
    avg_cases = sum(w * c for w, c in mix.values())
    avg_cost = avg_cases * ai_cost
    print(f"blended cases/seat {avg_cases:.0f}, cost ${avg_cost:.2f}, "
          f"margin {100 * (price - avg_cost) / price:.1f}%")

    print("\n-- Break-even cases per seat at price $30 --")
    print(f"break-even cases/seat = {price / ai_cost:.0f}")

    print("\n-- Sensitivity of cost per outcome (one factor at a time) --")
    base = per_outcome
    cases = {
        "success_rate 0.70 -> 0.60": dict(success_rate=0.60),
        "success_rate 0.70 -> 0.80": dict(success_rate=0.80),
        "retry_rate 0.15 -> 0.40": dict(retry_rate=0.40),
        "model_cost +50%": dict(model_cost=0.0315),
        "model_cost -50%": dict(model_cost=0.0105),
        "escalation_cost 4.50 -> 6.50": dict(escalation_cost=6.50),
        "review_rate 5% -> 20%": dict(review_rate=0.20),
    }
    args = dict(model_cost=0.021, retry_rate=0.15, success_rate=0.70,
                review_rate=0.05, review_cost=0.60, escalation_cost=4.50)
    for name, change in cases.items():
        a = dict(args)
        a.update(change)
        v = cost_per_outcome(**a)[1]
        print(f"{name:<30} ${v:.4f}  ({100 * (v - base) / base:+6.1f}%)")


# ---------------------------------------------------------------- forecaster
def forecast_months(months=12, users0=2000, user_growth=0.08,
                    reqs_per_user=60, usage_growth=0.02,
                    tokens0=3000, context_growth=0.04,
                    out_tokens=350, price_in=1.0, price_out=4.0,
                    cache_hit=0.0, cached_price=0.1):
    rows = []
    for m in range(months):
        users = users0 * (1 + user_growth) ** m
        reqs = users * reqs_per_user * (1 + usage_growth) ** m
        tin = tokens0 * (1 + context_growth) ** m
        fresh = tin * (1 - cache_hit)
        cached = tin * cache_hit
        per_req = (fresh * price_in + cached * cached_price
                   + out_tokens * price_out) / 1e6
        rows.append((m + 1, users, reqs, tin, per_req, reqs * per_req))
    return rows


def forecast():
    print("\n== Deterministic forecast, 12 months (illustrative) ==")
    print("month  users   requests  in_tokens  $/req   spend")
    rows = forecast_months()
    for m, u, r, t, p, s in rows:
        if m in (1, 3, 6, 9, 12):
            print(f"{m:>5} {u:>7.0f} {r:>9.0f} {t:>9.0f} {p:>7.5f} ${s:>8.0f}")
    flat = forecast_months(context_growth=0.0)
    print(f"month-12 spend with context growth 4%/mo: ${rows[-1][5]:.0f}")
    print(f"month-12 spend with flat context:         ${flat[-1][5]:.0f}")
    print(f"12-month total (growth) ${sum(r[5] for r in rows):.0f}, "
          f"(flat context) ${sum(r[5] for r in flat):.0f}")


def heavy_tail(n=100000, seed=7):
    """Monte Carlo of per-request token counts: lognormal body plus rare giants."""
    rnd = random.Random(seed)
    mu, sigma = math.log(3000), 0.6
    total = 0.0
    costs = []
    for _ in range(n):
        tin = rnd.lognormvariate(mu, sigma)
        if rnd.random() < 0.01:
            tin *= 12           # 1 percent of requests carry a very long document
        c = (tin * 1.0 + 350 * 4.0) / 1e6
        costs.append(c)
        total += c
    costs.sort()
    mean = total / n
    p50 = costs[n // 2]
    p99 = costs[int(n * 0.99)]
    top1 = sum(costs[int(n * 0.99):]) / total
    naive = (3000 * 1.0 + 350 * 4.0) / 1e6
    print("\n== Heavy-tail request cost (Monte Carlo, illustrative) ==")
    print(f"naive planning cost (median input 3000): ${naive:.5f}")
    print(f"simulated mean ${mean:.5f}  p50 ${p50:.5f}  p99 ${p99:.5f}")
    print(f"top 1 percent of requests = {100 * top1:.1f}% of spend")
    print(f"mean / naive = {mean / naive:.2f}")


def power_users(users=2000, seed=11):
    rnd = random.Random(seed)
    reqs = []
    for _ in range(users):
        reqs.append(min(rnd.paretovariate(1.4) * 25, 20000))
    reqs.sort(reverse=True)
    total = sum(reqs)
    top = sum(reqs[: users // 100])
    top10 = sum(reqs[: users // 10])
    print("\n== Power users (Pareto usage, illustrative) ==")
    print(f"mean requests/user/month {total / users:.0f}, median {reqs[users // 2]:.0f}")
    print(f"top 1 percent of users = {100 * top / total:.1f}% of requests")
    print(f"top 10 percent of users = {100 * top10 / total:.1f}% of requests")


if __name__ == "__main__":
    unit_economics()
    forecast()
    heavy_tail()
    power_users()
