"""Simulate inherited allow and explicit-deny decisions across scopes."""


def evaluate(
    requested_action: str, inherited_allows: set[str], inherited_denies: set[str]
) -> str:
    if requested_action in inherited_denies or "*" in inherited_denies:
        return "deny: an applicable explicit deny overrides allow"
    if requested_action in inherited_allows or "*" in inherited_allows:
        return "allow: an applicable policy grants the action"
    return "deny: no applicable allow was found"


def main() -> None:
    inherited_allows = {"storage.objects.get", "compute.instances.start"}
    inherited_denies = {"compute.instances.delete"}
    for action in (
        "storage.objects.get",
        "compute.instances.start",
        "compute.instances.delete",
        "storage.objects.delete",
    ):
        print(f"{action}: {evaluate(action, inherited_allows, inherited_denies)}")


if __name__ == "__main__":
    main()