"""Recommend workload scopes from ownership and isolation requirements."""


WORKLOADS = [
    {"name": "payments-prod", "owner": "payments", "regulated": True, "environment": "prod"},
    {"name": "payments-dev", "owner": "payments", "regulated": True, "environment": "dev"},
    {"name": "catalog-prod", "owner": "catalog", "regulated": False, "environment": "prod"},
]


def recommend_scope(workload: dict[str, object]) -> str:
    if workload["regulated"]:
        return f"dedicated scope under regulated/{workload['owner']}/{workload['environment']}"
    return f"scope under standard/{workload['owner']}/{workload['environment']}"


def main() -> None:
    for workload in WORKLOADS:
        print(f"{workload['name']}: {recommend_scope(workload)}")
    print("Validate recommendations against quota, billing, and team ownership needs.")


if __name__ == "__main__":
    main()