"""Check synthetic Azure region and zone requirements without cloud access."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ServicePlacement:
    name: str
    regions: frozenset[str]
    zone_redundant_regions: frozenset[str]


SERVICES = (
    ServicePlacement(
        name="Application runtime",
        regions=frozenset({"westeurope", "northeurope"}),
        zone_redundant_regions=frozenset({"westeurope", "northeurope"}),
    ),
    ServicePlacement(
        name="Managed data store",
        regions=frozenset({"westeurope"}),
        zone_redundant_regions=frozenset({"westeurope"}),
    ),
)


def assess_placement(
    service: ServicePlacement, region: str, require_zone_redundancy: bool
) -> list[str]:
    findings = []
    if region not in service.regions:
        findings.append(f"{service.name}: unavailable in {region}")
    elif require_zone_redundancy and region not in service.zone_redundant_regions:
        findings.append(f"{service.name}: zone redundancy is not modeled in {region}")
    else:
        findings.append(f"{service.name}: placement assumptions pass for {region}")
    return findings


def main() -> None:
    target_region = "westeurope"
    for service in SERVICES:
        for finding in assess_placement(service, target_region, True):
            print(finding)

    unsupported_region = "example-region"
    result = assess_placement(SERVICES[1], unsupported_region, True)
    print(f"Scenario check: {result[0]}")


if __name__ == "__main__":
    main()