"""Check whether a credential rotation window overlaps consumer refresh."""


def assess_rotation(
    rotation_interval_days: int,
    maximum_consumer_cache_hours: int,
    overlap_hours: int,
    rollback_hours: int,
) -> list[str]:
    findings = []
    required_overlap = maximum_consumer_cache_hours + rollback_hours
    if overlap_hours < required_overlap:
        findings.append(
            f"risk: overlap {overlap_hours}h is shorter than cache plus rollback "
            f"window {required_overlap}h"
        )
    else:
        findings.append("pass: overlap covers modeled cache and rollback windows")
    if rotation_interval_days <= 0:
        findings.append("risk: rotation interval must be positive")
    return findings


def main() -> None:
    for finding in assess_rotation(
        rotation_interval_days=30,
        maximum_consumer_cache_hours=12,
        overlap_hours=36,
        rollback_hours=24,
    ):
        print(finding)


if __name__ == "__main__":
    main()