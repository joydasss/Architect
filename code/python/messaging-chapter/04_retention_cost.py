"""Estimate normalized broker storage from backlog and retention settings."""


def estimate_retained_gb(
    messages_per_second: float,
    average_message_kb: float,
    retention_hours: int,
    dead_letter_fraction: float,
) -> float:
    seconds = retention_hours * 60 * 60
    message_count = messages_per_second * seconds
    primary_gb = message_count * average_message_kb / 1_000_000
    return primary_gb * (1 + dead_letter_fraction)


def main() -> None:
    for retention_hours in (24, 72, 168):
        retained = estimate_retained_gb(
            messages_per_second=350,
            average_message_kb=8,
            retention_hours=retention_hours,
            dead_letter_fraction=0.05,
        )
        print(f"retention={retention_hours:>3}h -> modeled storage={retained:.1f} GB")
    print("Estimate omits replication, indexes, request, and egress charges.")


if __name__ == "__main__":
    main()