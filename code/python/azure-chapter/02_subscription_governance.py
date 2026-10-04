"""Simulate inherited Azure Policy guardrails for a resource deployment."""


POLICY_ASSIGNMENTS = {
    "platform": {
        "allowed_regions": {"westeurope", "northeurope"},
        "required_tags": {"owner", "environment"},
    },
    "production": {
        "allowed_regions": {"westeurope"},
        "required_tags": {"data_classification"},
    },
}


def effective_policy(scopes: list[str]) -> dict[str, set[str]]:
    regions = None
    required_tags: set[str] = set()
    for scope in scopes:
        assignment = POLICY_ASSIGNMENTS[scope]
        allowed = assignment["allowed_regions"]
        regions = allowed if regions is None else regions & allowed
        required_tags |= assignment["required_tags"]
    return {"allowed_regions": regions or set(), "required_tags": required_tags}


def evaluate_resource(
    resource: dict[str, object], scopes: list[str]
) -> list[str]:
    policy = effective_policy(scopes)
    findings = []
    if resource["region"] not in policy["allowed_regions"]:
        findings.append(f"deny: region {resource['region']} is outside policy")

    tags = resource.get("tags", {})
    missing = policy["required_tags"] - tags.keys()
    if missing:
        findings.append(f"deny: missing required tags {', '.join(sorted(missing))}")

    if not findings:
        findings.append("allow: modeled policy constraints are satisfied")
    return findings


def main() -> None:
    scopes = ["platform", "production"]
    examples = [
        {
            "name": "complete production resource",
            "region": "westeurope",
            "tags": {
                "owner": "orders-team",
                "environment": "production",
                "data_classification": "confidential",
            },
        },
        {
            "name": "resource outside region policy",
            "region": "northeurope",
            "tags": {"owner": "orders-team", "environment": "production"},
        },
    ]
    for resource in examples:
        print(resource["name"])
        for finding in evaluate_resource(resource, scopes):
            print(f"  {finding}")


if __name__ == "__main__":
    main()