"""Deterministic canary decision simulation (standard library only).

Each stage routes a fraction of a fixed 10,000-request window to the canary.
Observed error counts are set to their expected values so the output is
reproducible and can be checked by hand. Decision rule per stage:
  - guardrail: canary error rate above 5.0 percent -> ROLLBACK at any size
  - evidence: below 500 canary requests, only the guardrail can roll back
  - test: one-sided two-proportion z-test, ROLLBACK if z > 2.33
Run: python 02_canary_decision_simulation.py
"""
from math import sqrt

WINDOW = 10_000
STAGES = [0.01, 0.05, 0.25, 0.50]
BASE_RATE = 0.02
MIN_CANARY_N = 500
Z_LIMIT = 2.33
ABS_GUARD = 0.05


def z_stat(ec, nc, eb, nb):
    pc, pb = ec / nc, eb / nb
    pooled = (ec + eb) / (nc + nb)
    se = sqrt(pooled * (1 - pooled) * (1 / nc + 1 / nb))
    return (pc - pb) / se if se else 0.0


def run(name, canary_rate):
    print(f"Scenario {name}: canary true error rate {canary_rate:.1%}, baseline {BASE_RATE:.1%}")
    for f in STAGES:
        nc = round(WINDOW * f)
        nb = WINDOW - nc
        ec = round(nc * canary_rate)
        eb = round(nb * BASE_RATE)
        z = z_stat(ec, nc, eb, nb)
        if ec / nc > ABS_GUARD:
            decision = "ROLLBACK (absolute guardrail)"
        elif nc < MIN_CANARY_N:
            decision = "ADVANCE (too little evidence to reject)"
        elif z > Z_LIMIT:
            decision = "ROLLBACK (z above limit)"
        else:
            decision = "ADVANCE"
        print(f"  stage {f:>4.0%}: canary n={nc:>5} errors={ec:>3} | base n={nb:>5} errors={eb:>3} | z={z:5.2f} -> {decision}")
        if decision.startswith("ROLLBACK"):
            print("  result: rolled back, 100 percent of traffic returned to baseline")
            return
    print("  result: promoted to 100 percent")


if __name__ == "__main__":
    run("A (healthy)", 0.02)
    run("B (regression)", 0.03)
