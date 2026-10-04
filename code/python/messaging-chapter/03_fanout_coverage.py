"""Compare required consumers with configured event subscriptions."""


REQUIRED_CONSUMERS = {"fulfillment", "analytics", "notifications"}
SUBSCRIPTIONS = {
    "orders-topic": {"fulfillment", "analytics"},
    "customer-events": {"notifications", "analytics"},
}


def audit_coverage(
    required: set[str], subscriptions: dict[str, set[str]]
) -> list[str]:
    configured = set().union(*subscriptions.values()) if subscriptions else set()
    missing = required - configured
    unexpected = configured - required
    findings = []
    if missing:
        findings.append(f"missing consumers: {', '.join(sorted(missing))}")
    if unexpected:
        findings.append(f"unexpected consumers: {', '.join(sorted(unexpected))}")
    if not findings:
        findings.append("pass: all required consumers are represented")
    return findings


def main() -> None:
    for topic, consumers in SUBSCRIPTIONS.items():
        print(f"{topic}: {', '.join(sorted(consumers))}")
    for finding in audit_coverage(REQUIRED_CONSUMERS, SUBSCRIPTIONS):
        print(finding)


if __name__ == "__main__":
    main()