"""Score a synthetic landing zone and list foundational gaps."""


CAPABILITIES = {
    "identity_baseline": True,
    "central_audit": True,
    "automated_vending": False,
    "network_ownership": True,
    "exception_expiry": False,
    "decommissioning": False,
}


def scorecard(capabilities: dict[str, bool]) -> tuple[int, list[str]]:
    complete = sum(capabilities.values())
    missing = [name for name, enabled in capabilities.items() if not enabled]
    return complete, missing


def main() -> None:
    complete, missing = scorecard(CAPABILITIES)
    print(f"Foundational capabilities: {complete}/{len(CAPABILITIES)}")
    for capability in missing:
        print(f"  improvement: {capability}")
    print("Use gaps to sequence platform work, not as a compliance certification.")


if __name__ == "__main__":
    main()