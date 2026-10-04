"""Simulate inherited guardrails for a Google Cloud project."""


POLICIES = {
    "organization": {
        "allowed_regions": {"europe-west1", "europe-west4", "us-central1"},
        "required_labels": {"owner"},
    },
    "regulated": {
        "allowed_regions": {"europe-west1", "europe-west4"},
        "required_labels": {"data_classification", "environment"},
    },
}


def effective_policy(scopes: list[str]) -> dict[str, set[str]]:
    allowed_regions = None
    required_labels: set[str] = set()
    for scope in scopes:
        policy = POLICIES[scope]
        allowed = policy["allowed_regions"]
        allowed_regions = allowed if allowed_regions is None else allowed_regions & allowed
        required_labels |= policy["required_labels"]
    return {
        "allowed_regions": allowed_regions or set(),
        "required_labels": required_labels,
    }


def evaluate_project(project: dict[str, object], scopes: list[str]) -> list[str]:
    policy = effective_policy(scopes)
    findings = []
    if project["region"] not in policy["allowed_regions"]:
        findings.append(f"deny: {project['region']} is not allowed by inherited policy")
    missing = policy["required_labels"] - project.get("labels", {}).keys()
    if missing:
        findings.append(f"deny: missing labels {', '.join(sorted(missing))}")
    if not findings:
        findings.append("allow: modeled project guardrails pass")
    return findings


def main() -> None:
    scopes = ["organization", "regulated"]
    projects = [
        {
            "project_id": "orders-prod",
            "region": "europe-west1",
            "labels": {
                "owner": "orders-team",
                "environment": "production",
                "data_classification": "confidential",
            },
        },
        {
            "project_id": "analytics-prod",
            "region": "us-central1",
            "labels": {"owner": "analytics-team", "environment": "production"},
        },
    ]
    for project in projects:
        print(project["project_id"])
        for finding in evaluate_project(project, scopes):
            print(f"  {finding}")


if __name__ == "__main__":
    main()