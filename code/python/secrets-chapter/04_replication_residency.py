"""Check secret replication targets against a synthetic residency allowlist."""


ALLOWED_REGIONS = {"westeurope", "northeurope"}
REPLICATION_TARGETS = {"westeurope", "northeurope", "us-east1"}


def check_targets(
    allowed_regions: set[str], targets: set[str]
) -> list[str]:
    findings = []
    disallowed = targets - allowed_regions
    if disallowed:
        findings.append(f"deny: disallowed replication regions {', '.join(sorted(disallowed))}")
    allowed = targets & allowed_regions
    if allowed:
        findings.append(f"allow: approved replication regions {', '.join(sorted(allowed))}")
    if not findings:
        findings.append("review: no replication target is configured")
    return findings


def main() -> None:
    for finding in check_targets(ALLOWED_REGIONS, REPLICATION_TARGETS):
        print(finding)


if __name__ == "__main__":
    main()