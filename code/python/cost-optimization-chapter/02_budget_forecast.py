"""Compare current spend and forecast with a synthetic budget threshold."""


def assess_budget(
    current_spend: float, days_elapsed: int, days_in_period: int, budget: float
) -> dict[str, float | str]:
    if days_elapsed <= 0 or days_in_period <= 0:
        raise ValueError("period lengths must be positive")
    forecast = current_spend / days_elapsed * days_in_period
    status = "alert" if forecast >= budget else "within budget"
    return {"forecast": forecast, "variance": forecast - budget, "status": status}


def main() -> None:
    result = assess_budget(
        current_spend=18_500,
        days_elapsed=12,
        days_in_period=30,
        budget=40_000,
    )
    print(f"Forecast: {result['forecast']:.2f} normalized units")
    print(f"Variance: {result['variance']:.2f}")
    print(f"Status: {result['status']}")
    print("Linear forecasts ignore seasonality, credits, and late-arriving charges.")


if __name__ == "__main__":
    main()