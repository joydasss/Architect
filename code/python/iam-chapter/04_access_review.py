"""Report principals that need ownership or access review."""


PRINCIPALS = [
    {"name": "orders-runtime", "owner": "orders-team", "last_used_days": 2, "admin": False},
    {"name": "legacy-deployer", "owner": "", "last_used_days": 210, "admin": True},
    {"name": "auditor-readonly", "owner": "security-team", "last_used_days": 120, "admin": False},
]


def review(principal: dict[str, object], stale_days: int) -> list[str]:
    findings = []
    if not principal["owner"]:
        findings.append("missing owner")
    if principal["last_used_days"] > stale_days:
        findings.append("no recent use")
    if principal["admin"]:
        findings.append("privileged access requires explicit justification")
    if not findings:
        findings.append("no review trigger in this simplified check")
    return findings


def main() -> None:
    for principal in PRINCIPALS:
        print(principal["name"])
        for finding in review(principal, stale_days=90):
            print(f"  review: {finding}")


if __name__ == "__main__":
    main()