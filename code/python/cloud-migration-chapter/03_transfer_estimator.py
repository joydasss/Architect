"""Estimate online and offline transfer duration with synthetic costs."""


def estimate_transfer(data_gib, usable_mbps, online_cost_per_gib, appliance_cost):
    """Return idealized online hours and comparative transfer costs."""
    if data_gib <= 0 or usable_mbps <= 0:
        raise ValueError("data size and usable bandwidth must be positive")
    seconds = data_gib * 1024**3 * 8 / (usable_mbps * 1_000_000)
    hours = seconds / 3600
    return {
        "online_hours": hours,
        "online_cost": data_gib * online_cost_per_gib,
        "offline_cost": appliance_cost,
        "offline_is_cheaper": appliance_cost < data_gib * online_cost_per_gib,
    }


if __name__ == "__main__":
    result = estimate_transfer(
        data_gib=20_000,
        usable_mbps=500,
        online_cost_per_gib=0.02,
        appliance_cost=250,
    )
    assert result["online_hours"] > 90
    assert result["offline_is_cheaper"]
    print("Estimate (idealized; excludes retries and incremental sync):", result)