"""Check alert policies for ownership and response-action completeness."""


ALERTS = [
    {
        "name": "High API error rate",
        "owner": "orders-on-call",
        "action": "page",
        "runbook": "orders-api-errors",
        "customer_impact": True,
    },
    {
        "name": "Debug log count changed",
        "owner": "",
        "action": "page",
        "runbook": "",
        "customer_impact": False,
    },
]


def review_alert(alert: dict[str, object]) -> list[str]:
    findings = []
    if not alert["owner"]:
        findings.append("missing responder owner")
    if not alert["runbook"]:
        findings.append("missing response procedure")
    if alert["action"] == "page" and not alert["customer_impact"]:
        findings.append("page may be unnecessary without urgent impact")
    if not findings:
        findings.append("pass: ownership and action are defined")
    return findings


def main() -> None:
    for alert in ALERTS:
        print(alert["name"])
        for finding in review_alert(alert):
            print(f"  {finding}")


if __name__ == "__main__":
    main()