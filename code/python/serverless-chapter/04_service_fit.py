"""Rank serverless and managed execution models against workload needs."""


WEIGHTS = {
    "event_fit": 3,
    "long_running_fit": 2,
    "custom_runtime_fit": 2,
    "operational_simplicity": 2,
}

CANDIDATES = {
    "Function service": {
        "event_fit": 5,
        "long_running_fit": 1,
        "custom_runtime_fit": 2,
        "operational_simplicity": 5,
    },
    "Serverless container": {
        "event_fit": 4,
        "long_running_fit": 4,
        "custom_runtime_fit": 4,
        "operational_simplicity": 4,
    },
    "Managed worker fleet": {
        "event_fit": 3,
        "long_running_fit": 5,
        "custom_runtime_fit": 5,
        "operational_simplicity": 2,
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
        "event_fit": 5,
        "long_running_fit": 2,
        "custom_runtime_fit": 2,
        "operational_simplicity": 5,
    }
    for score, candidate in rank_candidates(requirements):
        print(f"{score:>3}  {candidate}")
    print("Scores are decision prompts; verify provider contracts and limits.")


if __name__ == "__main__":
    main()