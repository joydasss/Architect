"""Compare synthetic container execution services against workload needs."""


WEIGHTS = {
    "orchestration_control": 3,
    "http_service_fit": 2,
    "batch_fit": 2,
    "operational_simplicity": 1,
}

CANDIDATES = {
    "Managed task service": {
        "orchestration_control": 2,
        "http_service_fit": 2,
        "batch_fit": 5,
        "operational_simplicity": 4,
    },
    "Managed container application": {
        "orchestration_control": 2,
        "http_service_fit": 5,
        "batch_fit": 3,
        "operational_simplicity": 5,
    },
    "Managed Kubernetes": {
        "orchestration_control": 5,
        "http_service_fit": 4,
        "batch_fit": 4,
        "operational_simplicity": 1,
    },
}


def rank_services(requirements: dict[str, int]) -> list[tuple[int, str]]:
    scores = []
    for service, attributes in CANDIDATES.items():
        score = sum(
            WEIGHTS[dimension] * min(requirements[dimension], attributes[dimension])
            for dimension in WEIGHTS
        )
        scores.append((score, service))
    return sorted(scores, reverse=True)


def main() -> None:
    requirements = {
        "orchestration_control": 2,
        "http_service_fit": 5,
        "batch_fit": 2,
        "operational_simplicity": 5,
    }
    for score, service in rank_services(requirements):
        print(f"{score:>3}  {service}")
    print("Scores guide review; verify actual limits, network, and recovery contracts.")


if __name__ == "__main__":
    main()