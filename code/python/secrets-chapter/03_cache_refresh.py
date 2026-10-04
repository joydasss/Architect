"""Check secret cache freshness against rotation and revocation windows."""


def assess_cache(
    refresh_interval_minutes: int,
    allowed_staleness_minutes: int,
    revocation_target_minutes: int,
) -> list[str]:
    findings = []
    if refresh_interval_minutes > allowed_staleness_minutes:
        findings.append("risk: refresh interval exceeds allowed stale-secret window")
    if refresh_interval_minutes > revocation_target_minutes:
        findings.append("risk: cached credential can outlive revocation target")
    if not findings:
        findings.append("pass: modeled refresh interval meets freshness targets")
    return findings


def main() -> None:
    for finding in assess_cache(
        refresh_interval_minutes=15,
        allowed_staleness_minutes=20,
        revocation_target_minutes=10,
    ):
        print(finding)


if __name__ == "__main__":
    main()