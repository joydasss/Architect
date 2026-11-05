"""Pareto frontier over quality, latency, and cost, plus switching-cost payback.

Standard library only. All candidate numbers are ILLUSTRATIVE.
Part 1 keeps the candidates that no other candidate beats on all three axes
(higher quality, lower latency, lower cost). Part 2 computes cost per
*successful* task, including human correction, and the months needed to repay
a one-time migration cost.
"""

CANDIDATES = [
    # name, quality (pass rate), p95 latency seconds, cost per task
    ("A frontier",   0.93, 6.0, 0.0120),
    ("B mid",        0.90, 3.0, 0.0030),
    ("C open-large", 0.89, 4.0, 0.0040),
    ("D small",      0.84, 1.2, 0.0006),
    ("E mid-old",    0.88, 3.5, 0.0035),
    ("F tiny",       0.70, 0.6, 0.0002),
]
CORRECTION_COST = 0.05  # human cost to fix one failed task, illustrative


def dominated(x, others):
    for o in others:
        if o is x:
            continue
        if o[1] >= x[1] and o[2] <= x[2] and o[3] <= x[3] and (
                o[1] > x[1] or o[2] < x[2] or o[3] < x[3]):
            return True
    return False


def main():
    print("Pareto frontier:")
    for c in CANDIDATES:
        tag = "dominated" if dominated(c, CANDIDATES) else "frontier"
        print(f"  {c[0]:13s} q={c[1]:.2f} p95={c[2]:.1f}s cost={c[3]:.4f}  {tag}")
    print("\nEffective cost per task including human correction:")
    best = None
    for name, q, _, cost in CANDIDATES:
        eff = cost + (1 - q) * CORRECTION_COST
        print(f"  {name:13s} {eff:.4f}")
        if best is None or eff < best[1]:
            best = (name, eff)
    print(f"  lowest effective cost: {best[0]}")

    print("\nSensitivity: cheapest effective candidate by correction cost")
    for cc in (0.05, 0.20, 0.50):
        winner = min(CANDIDATES, key=lambda c: c[3] + (1 - c[1]) * cc)
        print(f"  correction cost {cc:.2f}: {winner[0]}")

    # Switching payback: move 2,000,000 tasks/month from A to B.
    volume = 2_000_000
    eff = {n: c + (1 - q) * CORRECTION_COST for n, q, _, c in CANDIDATES}
    saving = (eff["A frontier"] - eff["B mid"]) * volume
    one_time = 90_000
    print(f"\nmonthly saving moving A -> B at {volume:,} tasks: {saving:,.0f}")
    print(f"one-time migration cost {one_time:,}: payback {one_time / saving:.2f} months")


if __name__ == "__main__":
    main()
