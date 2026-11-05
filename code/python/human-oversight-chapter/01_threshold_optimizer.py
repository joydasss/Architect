"""Choose a review threshold from error costs and review capacity.

Standard library only. The model's confidence is assumed calibrated: among
items with confidence c, a fraction c of the model's answers are correct.
Items below the threshold go to a human reviewer. All numbers are illustrative.
"""

# (bin confidence, share of traffic). Shares sum to 1.0.
BINS = [
    (0.55, 0.05), (0.65, 0.07), (0.75, 0.10), (0.85, 0.15),
    (0.90, 0.18), (0.95, 0.20), (0.98, 0.15), (0.995, 0.10),
]

ITEMS_PER_DAY = 10_000
COST_ERROR = 200.0       # cost of one wrong decision that reaches the customer
COST_REVIEW = 4.0        # fully loaded cost of one human review
REVIEWER_CATCH = 0.90    # probability a reviewer fixes a model error
REVIEW_CAPACITY = 3_000  # reviews the team can do per day at target quality


def evaluate(threshold: float) -> dict:
    reviewed = sum(w for c, w in BINS if c < threshold) * ITEMS_PER_DAY
    auto_err = sum(w * (1 - c) for c, w in BINS if c >= threshold) * ITEMS_PER_DAY
    rev_err = sum(w * (1 - c) for c, w in BINS if c < threshold) * ITEMS_PER_DAY
    residual = auto_err + rev_err * (1 - REVIEWER_CATCH)
    cost = reviewed * COST_REVIEW + residual * COST_ERROR
    return {"t": threshold, "reviewed": reviewed, "residual": residual,
            "cost": cost, "feasible": reviewed <= REVIEW_CAPACITY}


def main() -> None:
    thresholds = [0.0] + [c + 1e-9 for c, _ in BINS]
    rows = [evaluate(t) for t in thresholds]
    print(f"{'threshold':>9} {'reviews/day':>11} {'residual errors':>15} "
          f"{'cost/day':>9} {'feasible':>8}")
    for r in rows:
        t = "none" if r["t"] == 0.0 else f"<{r['t']:.3f}"
        print(f"{t:>9} {r['reviewed']:>11.0f} {r['residual']:>15.1f} "
              f"{r['cost']:>9.0f} {str(r['feasible']):>8}")
    best_any = min(rows, key=lambda r: r["cost"])
    best_ok = min((r for r in rows if r["feasible"]), key=lambda r: r["cost"])
    print()
    print(f"Cheapest ignoring capacity: review below {best_any['t']:.3f} "
          f"({best_any['reviewed']:.0f} reviews/day, cost {best_any['cost']:.0f})")
    print(f"Cheapest within capacity {REVIEW_CAPACITY}: review below "
          f"{best_ok['t']:.3f} ({best_ok['reviewed']:.0f} reviews/day, "
          f"cost {best_ok['cost']:.0f})")
    # Break-even rule: review a bin when its error rate times catch rate times
    # cost of error exceeds the review cost.
    breakeven_err = COST_REVIEW / (REVIEWER_CATCH * COST_ERROR)
    print(f"Break-even model error rate: {breakeven_err:.4f} "
          f"(confidence {1 - breakeven_err:.4f})")
    # Sensitivity: how the unconstrained choice moves with the cost of error.
    print("\nSensitivity of the break-even confidence to error cost:")
    for ce in (50, 100, 200, 500, 2000):
        be = COST_REVIEW / (REVIEWER_CATCH * ce)
        print(f"  cost of error {ce:>5}: review when confidence < {1 - be:.4f}")


if __name__ == "__main__":
    main()
