"""Use-case risk tiering and human-review capacity arithmetic (standard library only).

Part 1 scores harms as severity x likelihood x reversibility and maps the result
to a governance tier. Part 2 computes how many reviewers an oversight design
needs and shows how a rubber-stamp review time collapses effective oversight.
Part 3 shows how automation bias distorts an override rate.

All scales and thresholds are illustrative. Calibrate them for your organization.

Run: python 02_risk_tiering_and_oversight.py
"""

import math

# Severity 1-5, likelihood 1-5, reversibility factor 1 (easy to undo) to 3 (irreversible).
HARMS = [
    ("credit-model", "wrongful denial of credit", 4, 3, 2),
    ("credit-model", "disparate error rates by group", 4, 3, 2),
    ("assistant", "confident wrong answer about policy", 2, 4, 1),
    ("assistant", "leak of another customer's data", 5, 2, 3),
    ("assistant", "toxic output to a user", 3, 2, 1),
    ("marketing-copy", "off-brand wording", 1, 3, 1),
]

TIERS = [(0, 10, "T1 low"), (10, 24, "T2 moderate"), (24, 60, "T3 high"), (60, 10**9, "T4 critical")]


def tier(score):
    for lo, hi, name in TIERS:
        if lo <= score < hi:
            return name
    raise ValueError(score)


def part1():
    print("== Part 1: harm scores (severity x likelihood x reversibility) ==")
    worst = {}
    for uc, harm, s, l, r in HARMS:
        score = s * l * r
        print(f"{uc:<15}{harm:<40}{s}x{l}x{r} = {score:>3}  {tier(score)}")
        worst[uc] = max(worst.get(uc, 0), score)
    print("Use-case tier = tier of the worst harm:")
    for uc, score in worst.items():
        print(f"  {uc:<15}{score:>3}  {tier(score)}")


def part2():
    print("\n== Part 2: review capacity ==")
    cases_per_day = 1200
    flag_rate = 0.25  # share routed to human review
    review_minutes = 6.0
    productive_hours = 5.5  # per reviewer per day, after meetings and breaks
    load_hours = cases_per_day * flag_rate * review_minutes / 60
    reviewers = math.ceil(load_hours / productive_hours)
    print(f"reviewed cases/day: {cases_per_day * flag_rate:.0f}")
    print(f"load: {load_hours:.1f} reviewer-hours/day -> {reviewers} reviewers at {productive_hours} h each")

    # If staffing is fixed at 3 reviewers, what time per case is available?
    staff = 3
    avail_min = staff * productive_hours * 60 / (cases_per_day * flag_rate)
    print(f"with {staff} reviewers: {avail_min:.1f} minutes per case (design assumed {review_minutes})")
    # Queueing: utilization and mean wait for an M/M/c-like rough check using utilization only.
    util = load_hours / (staff * productive_hours)
    print(f"utilization with {staff} reviewers: {util:.2f} (above 0.85 queues grow quickly)")

    # Flag-rate budget: the maximum flag rate that 3 reviewers can handle at design time.
    max_flag = staff * productive_hours * 60 / (review_minutes * cases_per_day)
    print(f"max flag rate for {staff} reviewers at {review_minutes} min: {max_flag:.3f}")


def part3():
    print("\n== Part 3: what an override rate can and cannot tell you ==")
    reviewed = 3000
    model_wrong = 0.10
    for label, catch_rate in (("attentive reviewer", 0.80), ("rubber-stamp reviewer", 0.15)):
        wrong = reviewed * model_wrong
        caught = wrong * catch_rate
        slipped = wrong - caught
        print(f"{label:<24}override rate {caught / reviewed:.3f}, wrong outputs shipped {slipped:.0f} of {wrong:.0f}")
    print("A 1.5% override rate would look 'good' yet ships 255 wrong outputs; an audit sample is needed.")

    # Audit sample size to estimate the miss rate within +/- 5 points at 95% confidence (p=0.5 worst case).
    z, e = 1.96, 0.05
    n = math.ceil(z * z * 0.25 / (e * e))
    print(f"independent audit sample for +/-5 points: {n} reviewed cases")


if __name__ == "__main__":
    part1()
    part2()
    part3()
