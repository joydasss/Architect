"""Check replica placement and remaining capacity after one zone is lost."""


def assess_placement(
    replicas_by_zone: dict[str, int], capacity_by_zone: dict[str, int], required: int
) -> list[str]:
    findings = []
    active_zones = [zone for zone, replicas in replicas_by_zone.items() if replicas > 0]
    if len(active_zones) < 2:
        findings.append("risk: replicas occupy fewer than two zones")

    for failed_zone in active_zones:
        remaining_capacity = sum(
            capacity for zone, capacity in capacity_by_zone.items() if zone != failed_zone
        )
        status = "pass" if remaining_capacity >= required else "fail"
        findings.append(
            f"{status}: after losing {failed_zone}, remaining capacity "
            f"is {remaining_capacity} (required {required})"
        )
    return findings


def main() -> None:
    replicas = {"zone-a": 3, "zone-b": 3, "zone-c": 0}
    capacity = {"zone-a": 4, "zone-b": 4, "zone-c": 4}
    for finding in assess_placement(replicas, capacity, required=6):
        print(finding)


if __name__ == "__main__":
    main()