"""Rank synthetic cloud messaging models against workload requirements."""


WEIGHTS = {
    "work_distribution": 3,
    "fanout": 2,
    "replay": 2,
    "operational_simplicity": 1,
}

CANDIDATES = {
    "Managed queue": {
        "work_distribution": 5,
        "fanout": 1,
        "replay": 2,
        "operational_simplicity": 5,
    },
    "Publish-subscribe topic": {
        "work_distribution": 3,
        "fanout": 5,
        "replay": 2,
        "operational_simplicity": 4,
    },
    "Partitioned event stream": {
        "work_distribution": 4,
        "fanout": 4,
        "replay": 5,
        "operational_simplicity": 2,
    },
}


def rank_models(requirements: dict[str, int]) -> list[tuple[int, str]]:
    ranked = []
    for model, attributes in CANDIDATES.items():
        score = sum(
            WEIGHTS[key] * min(attributes[key], requirements[key])
            for key in WEIGHTS
        )
        ranked.append((score, model))
    return sorted(ranked, reverse=True)


def main() -> None:
    requirements = {
        "work_distribution": 4,
        "fanout": 5,
        "replay": 2,
        "operational_simplicity": 4,
    }
    for score, model in rank_models(requirements):
        print(f"{score:>3}  {model}")
    print("Scores are screening aids; verify real service contracts.")


if __name__ == "__main__":
    main()