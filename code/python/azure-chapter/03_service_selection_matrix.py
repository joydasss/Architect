"""Rank synthetic Azure service models against workload requirements."""


WEIGHTS = {
    "runtime_fit": 3,
    "burst_fit": 2,
    "private_network_fit": 2,
    "operational_simplicity": 1,
}

CANDIDATES = {
    "Virtual Machines": {
        "runtime_fit": 5,
        "burst_fit": 2,
        "private_network_fit": 5,
        "operational_simplicity": 1,
    },
    "App Service": {
        "runtime_fit": 4,
        "burst_fit": 4,
        "private_network_fit": 4,
        "operational_simplicity": 4,
    },
    "Azure Functions": {
        "runtime_fit": 2,
        "burst_fit": 5,
        "private_network_fit": 3,
        "operational_simplicity": 5,
    },
}


def rank_candidates(requirements: dict[str, int]) -> list[tuple[int, str]]:
    scores = []
    for candidate, attributes in CANDIDATES.items():
        score = sum(
            WEIGHTS[key] * min(attributes[key], requirements[key])
            for key in WEIGHTS
        )
        scores.append((score, candidate))
    return sorted(scores, reverse=True)


def main() -> None:
    requirements = {
        "runtime_fit": 4,
        "burst_fit": 5,
        "private_network_fit": 4,
        "operational_simplicity": 4,
    }
    for score, candidate in rank_candidates(requirements):
        print(f"{score:>3}  {candidate}")
    print("Scores are prompts for review, not service guarantees or benchmarks.")


if __name__ == "__main__":
    main()