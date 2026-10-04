"""Estimate metric time-series cardinality from label dimensions."""

from math import prod


LABEL_VALUES = {
    "service": 12,
    "region": 4,
    "environment": 3,
    "status_code": 8,
}


def estimate_series(dimensions: dict[str, int]) -> int:
    return prod(dimensions.values())


def main() -> None:
    bounded = dict(LABEL_VALUES)
    unbounded = {**LABEL_VALUES, "user_id": 100_000}
    budget = 250_000
    for name, dimensions in (("bounded", bounded), ("with-user-id", unbounded)):
        series = estimate_series(dimensions)
        status = "within" if series <= budget else "over"
        print(f"{name}: {series:,} series, {status} budget {budget:,}")


if __name__ == "__main__":
    main()