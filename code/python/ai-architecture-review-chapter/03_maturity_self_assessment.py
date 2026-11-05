"""Organizational AI-architecture maturity self-assessment.

Standard library only. Run: python 03_maturity_self_assessment.py

Eight capabilities are rated 1-5:
  1 ad hoc   2 repeatable   3 defined   4 measured   5 improving
The overall level is capped by the weakest of the "foundation" capabilities,
because strong evaluation does not compensate for missing ownership.
"""

CAPABILITIES = {
    "intake_and_qualification": False,
    "data_rights_and_lineage": True,
    "evaluation_and_observability": True,
    "release_and_rollback": False,
    "security_and_privacy_controls": True,
    "human_oversight_design": False,
    "incident_response_and_learning": True,
    "cost_and_capacity_management": False,
}
# True marks a foundation capability that caps the overall level.

TEAMS = {
    "team_alpha": dict(intake_and_qualification=3, data_rights_and_lineage=2,
                       evaluation_and_observability=3, release_and_rollback=3,
                       security_and_privacy_controls=2, human_oversight_design=3,
                       incident_response_and_learning=1, cost_and_capacity_management=2),
    "team_beta": dict(intake_and_qualification=4, data_rights_and_lineage=4,
                      evaluation_and_observability=4, release_and_rollback=4,
                      security_and_privacy_controls=4, human_oversight_design=3,
                      incident_response_and_learning=4, cost_and_capacity_management=3),
}


def assess(ratings):
    mean = sum(ratings.values()) / len(ratings)
    foundation_min = min(v for k, v in ratings.items() if CAPABILITIES[k])
    level = min(round(mean), foundation_min + 1)
    weakest = sorted(ratings.items(), key=lambda kv: kv[1])[:3]
    return mean, foundation_min, level, weakest


if __name__ == "__main__":
    for name, r in TEAMS.items():
        mean, fmin, level, weakest = assess(r)
        print(f"{name}: mean={mean:.2f} foundation_min={fmin} overall_level={level}")
        print("  weakest:", ", ".join(f"{k}={v}" for k, v in weakest))
