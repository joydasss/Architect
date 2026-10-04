"""Estimate storage and retrieval cost for simple lifecycle tiers."""


TIERS = {
    "hot": {"storage_per_gb_month": 0.020, "retrieval_per_gb": 0.00},
    "cool": {"storage_per_gb_month": 0.010, "retrieval_per_gb": 0.01},
    "archive": {"storage_per_gb_month": 0.002, "retrieval_per_gb": 0.03},
}


def estimate_monthly_cost(
    tier: str, gigabytes: float, retrieved_gigabytes: float
) -> float:
    prices = TIERS[tier]
    return (
        gigabytes * prices["storage_per_gb_month"]
        + retrieved_gigabytes * prices["retrieval_per_gb"]
    )


def main() -> None:
    stored_gb = 10_000
    retrieved_gb = 2_000
    for tier in TIERS:
        cost = estimate_monthly_cost(tier, stored_gb, retrieved_gb)
        print(f"{tier:>7}: normalized monthly units={cost:.2f}")
    print("Illustrative rates omit requests, minimum duration, and egress.")


if __name__ == "__main__":
    main()