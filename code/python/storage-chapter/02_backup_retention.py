"""Check that sample recovery points meet a minimum retention policy."""


RECOVERY_POINTS = [
    {"name": "daily-001", "age_days": 2, "immutable": True},
    {"name": "weekly-001", "age_days": 9, "immutable": True},
    {"name": "monthly-001", "age_days": 35, "immutable": False},
    {"name": "quarterly-001", "age_days": 100, "immutable": True},
]


def audit_retention(
    recovery_points: list[dict[str, object]], minimum_age_days: int
) -> list[str]:
    findings = []
    for point in recovery_points:
        if point["age_days"] >= minimum_age_days and not point["immutable"]:
            findings.append(f"risk: {point['name']} is retained but mutable")
        elif point["age_days"] < minimum_age_days:
            findings.append(f"review: {point['name']} expires before {minimum_age_days} days")
        else:
            findings.append(f"pass: {point['name']} meets modeled retention")
    return findings


def main() -> None:
    for finding in audit_retention(RECOVERY_POINTS, minimum_age_days=90):
        print(finding)


if __name__ == "__main__":
    main()