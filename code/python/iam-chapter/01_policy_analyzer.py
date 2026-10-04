"""Flag broad cloud policy statements in a synthetic policy document."""


POLICY = [
    {"effect": "allow", "actions": ["storage.objects.get"], "resources": ["bucket/orders/*"]},
    {"effect": "allow", "actions": ["*"], "resources": ["*"]},
    {"effect": "deny", "actions": ["compute.instances.delete"], "resources": ["*"]},
]


def analyze(policy: list[dict[str, object]]) -> list[str]:
    findings = []
    for index, statement in enumerate(policy, start=1):
        actions = statement["actions"]
        resources = statement["resources"]
        if statement["effect"] == "allow" and "*" in actions and "*" in resources:
            findings.append(f"statement {index}: broad allow covers every action and resource")
        elif statement["effect"] == "allow" and "*" in actions:
            findings.append(f"statement {index}: wildcard action needs review")
        elif statement["effect"] == "allow" and "*" in resources:
            findings.append(f"statement {index}: wildcard resource needs review")
        else:
            findings.append(f"statement {index}: scoped or restrictive statement")
    return findings


def main() -> None:
    for finding in analyze(POLICY):
        print(finding)


if __name__ == "__main__":
    main()