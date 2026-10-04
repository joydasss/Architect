"""Validate minimum ownership and governance fields for scope vending."""


REQUIRED_FIELDS = {
    "name",
    "owner",
    "environment",
    "billing_owner",
    "data_classification",
    "region",
}


def validate_request(request: dict[str, str]) -> list[str]:
    missing = sorted(REQUIRED_FIELDS - request.keys())
    if missing:
        return [f"reject: missing fields {', '.join(missing)}"]
    if request["environment"] not in {"dev", "test", "prod"}:
        return ["reject: environment must be dev, test, or prod"]
    return ["accept: request can enter the governed provisioning workflow"]


def main() -> None:
    requests = [
        {
            "name": "payments-prod",
            "owner": "payments-team",
            "environment": "prod",
            "billing_owner": "finance-payments",
            "data_classification": "restricted",
            "region": "westeurope",
        },
        {"name": "unowned-sandbox", "owner": "", "environment": "preview"},
    ]
    for request in requests:
        print(request["name"])
        for finding in validate_request(request):
            print(f"  {finding}")


if __name__ == "__main__":
    main()