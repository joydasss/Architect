"""Demonstrate duplicate event delivery with an idempotency key."""


def process_deliveries(event_ids: list[str]) -> tuple[int, int]:
    completed: set[str] = set()
    side_effects = 0
    duplicates = 0
    for event_id in event_ids:
        if event_id in completed:
            duplicates += 1
            continue
        completed.add(event_id)
        side_effects += 1
    return side_effects, duplicates


def main() -> None:
    deliveries = ["evt-100", "evt-101", "evt-100", "evt-102", "evt-101"]
    effects, duplicates = process_deliveries(deliveries)
    print(f"Deliveries received: {len(deliveries)}")
    print(f"Business side effects: {effects}")
    print(f"Duplicate deliveries suppressed: {duplicates}")
    print("Production deduplication requires durable, atomic idempotency state.")


if __name__ == "__main__":
    main()