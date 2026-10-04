"""Check visibility and retry timing against processing duration."""


def assess_retry_window(
    processing_seconds: int,
    visibility_seconds: int,
    retry_attempts: int,
    backoff_seconds: int,
) -> list[str]:
    findings = []
    if visibility_seconds <= processing_seconds:
        findings.append("risk: message can become visible before processing completes")
    if retry_attempts < 1:
        findings.append("risk: no retry attempt is configured")
    if retry_attempts * backoff_seconds > 3600:
        findings.append("review: retry horizon exceeds one hour")
    if not findings:
        findings.append("pass: modeled visibility and retry window are plausible")
    return findings


def main() -> None:
    scenarios = [
        {"name": "short job", "processing": 20, "visibility": 60, "attempts": 5, "backoff": 10},
        {"name": "slow job", "processing": 180, "visibility": 120, "attempts": 4, "backoff": 30},
    ]
    for scenario in scenarios:
        print(scenario["name"])
        for finding in assess_retry_window(
            scenario["processing"], scenario["visibility"],
            scenario["attempts"], scenario["backoff"]
        ):
            print(f"  {finding}")


if __name__ == "__main__":
    main()