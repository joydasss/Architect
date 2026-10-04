"""Check baseline controls assigned to platform and workload scopes."""


REQUIRED_CONTROLS = {
    "central-audit",
    "approved-regions",
    "owner-metadata",
    "network-egress-policy",
}

SCOPES = {
    "platform": {"central-audit", "approved-regions", "owner-metadata", "network-egress-policy"},
    "payments-prod": {"central-audit", "approved-regions", "network-egress-policy"},
    "sandbox": {"owner-metadata"},
}


def missing_controls(assigned: set[str], required: set[str]) -> list[str]:
    return sorted(required - assigned)


def main() -> None:
    for scope, controls in SCOPES.items():
        missing = missing_controls(controls, REQUIRED_CONTROLS)
        if missing:
            print(f"{scope}: missing {', '.join(missing)}")
        else:
            print(f"{scope}: baseline covered")


if __name__ == "__main__":
    main()