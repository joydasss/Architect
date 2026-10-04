"""Find workloads missing required monitoring and audit coverage."""


REQUIRED_SIGNALS = {"metrics", "logs", "audit", "owner"}

WORKLOADS = {
    "orders-api": {"metrics", "logs", "audit", "owner"},
    "billing-worker": {"metrics", "logs", "owner"},
    "sandbox-job": {"metrics"},
}


def audit_coverage(workloads: dict[str, set[str]]) -> dict[str, list[str]]:
    return {
        name: sorted(REQUIRED_SIGNALS - signals)
        for name, signals in workloads.items()
        if REQUIRED_SIGNALS - signals
    }


def main() -> None:
    gaps = audit_coverage(WORKLOADS)
    for workload, missing in gaps.items():
        print(f"{workload}: missing {', '.join(missing)}")
    if not gaps:
        print("All workloads meet the modeled signal baseline.")


if __name__ == "__main__":
    main()