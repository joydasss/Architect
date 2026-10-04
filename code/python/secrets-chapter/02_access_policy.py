"""Review synthetic secret resource grants for broad access."""


GRANTS = [
    {"principal": "orders-runtime", "secret": "orders-db-password", "actions": {"read"}},
    {"principal": "all-workloads", "secret": "*", "actions": {"read", "write", "delete"}},
    {"principal": "rotation-job", "secret": "billing-api-token", "actions": {"read", "write"}},
]


def review_grant(grant: dict[str, object]) -> str:
    actions = grant["actions"]
    if grant["principal"] == "all-workloads" or grant["secret"] == "*":
        return "high: wildcard principal or secret scope"
    if "delete" in actions:
        return "review: delete permission needs explicit ownership"
    if "write" in actions and not str(grant["principal"]).endswith("rotation-job"):
        return "review: secret write should be limited to rotation identity"
    return "pass: modeled scope is narrow"


def main() -> None:
    for grant in GRANTS:
        print(f"{grant['principal']} -> {grant['secret']}: {review_grant(grant)}")


if __name__ == "__main__":
    main()