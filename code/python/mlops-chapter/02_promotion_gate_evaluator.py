"""Promotion gate evaluator for a candidate versus a champion model.

Standard library only. The gate combines:
  1. a paired non-inferiority / superiority test on the error rate
     (discordant-pair normal approximation, as in McNemar's test),
  2. a latency ceiling on p95,
  3. a cost ceiling per 1,000 requests,
  4. a per-slice regression limit.
All numbers are illustrative.
"""
import math

Z95_ONE_SIDED = 1.645
Z975 = 1.96


def paired_error_diff(b, c, n):
    """b = champion wrong and candidate right, c = champion right and candidate wrong.

    Difference in error rate (candidate - champion) = (c - b) / n.
    Variance of that difference (paired): (b + c - (b - c)^2 / n) / n^2.
    """
    diff = (c - b) / n
    var = (b + c - (b - c) ** 2 / n) / n**2
    return diff, math.sqrt(var)


def gate(report):
    n = report["n"]
    diff, se = paired_error_diff(report["b"], report["c"], n)
    hi = diff + Z95_ONE_SIDED * se  # one-sided 95% upper bound on added error
    lo = diff - Z975 * se
    up = diff + Z975 * se
    checks = []
    checks.append(("error non-inferiority (upper bound <= margin)",
                   hi <= report["margin"], f"diff={diff:+.4f} se={se:.4f} upper={hi:+.4f} margin={report['margin']}"))
    checks.append(("p95 latency", report["p95_ms"] <= report["p95_limit_ms"],
                   f"{report['p95_ms']} ms vs {report['p95_limit_ms']} ms"))
    checks.append(("cost per 1k requests", report["cost_1k"] <= report["cost_limit_1k"],
                   f"{report['cost_1k']} vs {report['cost_limit_1k']}"))
    for name, (sb, sc, sn) in report["slices"].items():
        d, s = paired_error_diff(sb, sc, sn)
        worst = d + Z975 * s
        checks.append((f"slice {name} (95% upper <= {report['slice_margin']})",
                       worst <= report["slice_margin"], f"diff={d:+.4f} upper={worst:+.4f} n={sn}"))
    improved = up < 0
    return checks, (lo, up), improved


def run(title, report):
    print(f"== {title}")
    checks, (lo, up), improved = gate(report)
    for name, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    print(f"  two-sided 95% CI of error difference: [{lo:+.4f}, {up:+.4f}]  significantly better: {improved}")
    print("  DECISION:", "GO" if all(ok for _, ok, _ in checks) else "NO-GO")


if __name__ == "__main__":
    base = {
        "n": 20_000, "b": 410, "c": 290, "margin": 0.002,
        "p95_ms": 82, "p95_limit_ms": 100, "cost_1k": 0.41, "cost_limit_1k": 0.50,
        "slice_margin": 0.010,
        "slices": {"region_eu": (60, 45, 3_000), "new_customers": (35, 30, 1_200)},
    }
    run("Candidate A (better overall, all slices ok)", base)
    bad = dict(base, slices={"region_eu": (60, 45, 3_000), "new_customers": (10, 45, 1_200)})
    run("Candidate B (same overall, regresses on new customers)", bad)
    slow = dict(base, p95_ms=131)
    run("Candidate C (accurate but slow)", slow)
