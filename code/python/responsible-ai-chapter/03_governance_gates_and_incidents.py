"""Lifecycle governance gates as a state machine, plus an AI incident register.

The gate machine refuses transitions that lack required evidence or sign-off,
and records every decision in an append-only log. The incident register
computes severity from impact and scope and tracks time to contain.
Standard library only.

Run: python 03_governance_gates_and_incidents.py
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta

# state -> {next_state: (required evidence keys, required signers)}
TRANSITIONS = {
    "intake": {"design": ({"use_case_form", "tier"}, {"product_owner"})},
    "design": {
        "build": ({"impact_assessment", "data_review"}, {"product_owner", "risk_partner"}),
        "intake": (set(), {"product_owner"}),
    },
    "build": {"pre_release": ({"eval_report", "slice_report"}, {"model_owner"})},
    "pre_release": {
        "live": ({"red_team_report", "rollback_plan", "residual_risk_record"}, {"model_owner", "risk_partner"}),
        "build": (set(), {"model_owner"}),
    },
    "live": {
        "restricted": ({"incident_ref"}, {"on_call_owner"}),
        "retired": ({"retirement_plan"}, {"product_owner"}),
    },
    "restricted": {
        "live": ({"remediation_evidence", "re_eval_report"}, {"model_owner", "risk_partner"}),
        "retired": ({"retirement_plan"}, {"product_owner"}),
    },
}

# Tier T3 and above need an extra senior signature on release.
EXTRA_SIGNER = {"T3 high": "council_chair", "T4 critical": "council_chair"}


@dataclass
class System:
    name: str
    tier: str
    state: str = "intake"
    log: list = field(default_factory=list)

    def move(self, to, evidence, signers):
        rule = TRANSITIONS.get(self.state, {}).get(to)
        if rule is None:
            self.log.append((self.state, to, "REJECTED: no such transition"))
            return False
        need_ev, need_sign = rule
        need_sign = set(need_sign)
        if self.state == "pre_release" and to == "live" and self.tier in EXTRA_SIGNER:
            need_sign.add(EXTRA_SIGNER[self.tier])
        missing_ev = need_ev - set(evidence)
        missing_sig = need_sign - set(signers)
        if missing_ev or missing_sig:
            self.log.append((self.state, to, f"REJECTED: missing evidence {sorted(missing_ev)} signers {sorted(missing_sig)}"))
            return False
        self.log.append((self.state, to, "APPROVED"))
        self.state = to
        return True


def demo_gates():
    print("== Gate state machine ==")
    s = System("credit-model", "T3 high")
    s.move("design", {"use_case_form", "tier"}, {"product_owner"})
    s.move("build", {"impact_assessment", "data_review"}, {"product_owner", "risk_partner"})
    s.move("pre_release", {"eval_report", "slice_report"}, {"model_owner"})
    s.move("live", {"red_team_report", "rollback_plan"}, {"model_owner", "risk_partner"})
    s.move("live", {"red_team_report", "rollback_plan", "residual_risk_record"}, {"model_owner", "risk_partner", "council_chair"})
    s.move("intake", set(), set())
    for a, b, r in s.log:
        print(f"{a:>12} -> {b:<12} {r}")
    print("final state:", s.state)


@dataclass
class Incident:
    ident: str
    detected: datetime
    contained: datetime
    people_affected: int
    harm: int  # 1 minor, 2 moderate, 3 serious (rights, money, safety)
    reversible: bool

    def severity(self):
        if self.harm == 3 or (self.harm == 2 and self.people_affected >= 1000):
            return "SEV1"
        if self.harm == 2 or self.people_affected >= 1000:
            return "SEV2"
        return "SEV3"

    def minutes_to_contain(self):
        return (self.contained - self.detected) / timedelta(minutes=1)


def demo_register():
    print("\n== Incident register ==")
    t0 = datetime(2026, 10, 1, 9, 0)
    rows = [
        Incident("INC-001", t0, t0 + timedelta(minutes=50), 12, 1, True),
        Incident("INC-002", t0 + timedelta(days=3), t0 + timedelta(days=3, hours=4), 2300, 2, True),
        Incident("INC-003", t0 + timedelta(days=9), t0 + timedelta(days=9, hours=1, minutes=30), 40, 3, False),
    ]
    targets = {"SEV1": 60, "SEV2": 240, "SEV3": 1440}
    for r in rows:
        sev = r.severity()
        m = r.minutes_to_contain()
        ok = "within target" if m <= targets[sev] else "MISSED target"
        print(f"{r.ident} {sev} affected={r.people_affected:>5} contain={m:>5.0f} min ({ok}, target {targets[sev]})")
    mttc = sum(r.minutes_to_contain() for r in rows) / len(rows)
    print(f"mean time to contain: {mttc:.0f} minutes")


if __name__ == "__main__":
    demo_gates()
    demo_register()
