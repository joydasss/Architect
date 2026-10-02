"""Small directional API compatibility classifier for teaching purposes."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Change:
    name: str
    old_client_new_server: bool
    new_client_old_server: bool
    rationale: str


def classify(change: Change) -> str:
    """Summarize the two required pairings without inferring schema semantics."""
    if change.old_client_new_server and change.new_client_old_server:
        return "compatible_in_both_directions"
    if change.old_client_new_server or change.new_client_old_server:
        return "compatible_in_one_direction_only"
    return "breaking_in_both_directions"


def main() -> None:
    examples = [
        Change(
            name="optional response field, tolerant old reader",
            old_client_new_server=True,
            new_client_old_server=True,
            rationale="The new client does not require the field from an old server.",
        ),
        Change(
            name="new request field required by the new client",
            old_client_new_server=True,
            new_client_old_server=False,
            rationale="The new client requires behavior the old server does not understand.",
        ),
        Change(
            name="existing field changes units",
            old_client_new_server=False,
            new_client_old_server=False,
            rationale="Both pairings can parse the value but disagree on its meaning.",
        ),
    ]

    for change in examples:
        print(f"{change.name}: {classify(change)}")
        print(f"  old client/new server: {change.old_client_new_server}")
        print(f"  new client/old server: {change.new_client_old_server}")
        print(f"  rationale: {change.rationale}")

    assert classify(examples[0]) == "compatible_in_both_directions"
    assert classify(examples[1]) == "compatible_in_one_direction_only"
    assert classify(examples[2]) == "breaking_in_both_directions"


if __name__ == "__main__":
    main()