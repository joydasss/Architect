"""Compare synthetic managed Kubernetes modes by responsibility and needs."""


MODES = {
    "Automated mode": {
        "node_control": 1,
        "custom_networking": 2,
        "operational_simplicity": 5,
        "specialized_hardware": 2,
    },
    "Standard node pools": {
        "node_control": 5,
        "custom_networking": 5,
        "operational_simplicity": 2,
        "specialized_hardware": 5,
    },
}

WEIGHTS = {
    "node_control": 2,
    "custom_networking": 2,
    "operational_simplicity": 3,
    "specialized_hardware": 2,
}


def rank_modes(requirements: dict[str, int]) -> list[tuple[int, str]]:
    results = []
    for mode, attributes in MODES.items():
        score = sum(
            WEIGHTS[key] * min(requirements[key], attributes[key])
            for key in WEIGHTS
        )
        results.append((score, mode))
    return sorted(results, reverse=True)


def main() -> None:
    requirements = {
        "node_control": 2,
        "custom_networking": 2,
        "operational_simplicity": 5,
        "specialized_hardware": 1,
    }
    for score, mode in rank_modes(requirements):
        print(f"{score:>3}  {mode}")
    print("Scores are discussion aids; verify provider-specific feature boundaries.")


if __name__ == "__main__":
    main()