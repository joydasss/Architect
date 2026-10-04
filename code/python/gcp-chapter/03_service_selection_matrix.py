"""Rank synthetic Google Cloud service models against workload needs."""


WEIGHTS = {
    "runtime_fit": 3,
    "event_fit": 2,
    "network_fit": 2,
    "operational_simplicity": 1,
}

CANDIDATES = {
    "Compute Engine": {
        "runtime_fit": 5,
        "event_fit": 2,
        "network_fit": 5,
        "operational_simplicity": 1,
    },
    "Google Kubernetes Engine": {
        "runtime_fit": 5,
        "event_fit": 3,
        "network_fit": 5,
        "operational_simplicity": 2,
    },
    "Cloud Run": {
        "runtime_fit": 4,
        "event_fit": 5,
        "network_fit": 4,
        "operational_simplicity": 5,
    },
}


def rank_candidates(requirements: dict[str, int]) -> list[tuple[int, str]]:
    ranked = []
    for candidate, attributes in CANDIDATES.items():
        score = sum(
            WEIGHTS[dimension] * min(attributes[dimension], requirements[dimension])
            for dimension in WEIGHTS
        )
        ranked.append((score, candidate))
    return sorted(ranked, reverse=True)


def main() -> None:
    requirements = {
        "runtime_fit": 4,
        "event_fit": 5,
        "network_fit": 4,
        "operational_simplicity": 4,
    }
    for score, candidate in rank_candidates(requirements):
        print(f"{score:>3}  {candidate}")
    print("Scores prompt review; validate limits, behavior, and cost separately.")


if __name__ == "__main__":
    main()