"""Compare AWS service-model candidates against weighted requirements."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    name: str
    control: int
    operational_burden: int
    burst_fit: int
    portability: int


def score(candidate: Candidate, weights: dict[str, int]) -> int:
    values = {
        "control": candidate.control,
        "operational_burden": candidate.operational_burden,
        "burst_fit": candidate.burst_fit,
        "portability": candidate.portability,
    }
    return sum(values[name] * weight for name, weight in weights.items())


def main() -> None:
    candidates = [
        Candidate("EC2 fleet", control=5, operational_burden=1, burst_fit=3, portability=4),
        Candidate("managed containers", control=4, operational_burden=3, burst_fit=4, portability=4),
        Candidate("Lambda functions", control=2, operational_burden=5, burst_fit=5, portability=2),
    ]
    weights = {"control": 1, "operational_burden": 3, "burst_fit": 2, "portability": 1}
    rankings = sorted(((score(item, weights), item.name) for item in candidates), reverse=True)
    for total, name in rankings:
        print(f"{name}: weighted score={total}")
    assert rankings[0][1] == "Lambda functions"


if __name__ == "__main__":
    main()
