"""Event-time deduplication with explicit allowed lateness handling."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    event_id: str
    event_time: int
    value: int


class WindowDeduplicator:
    def __init__(self, window: int, allowed_lateness: int) -> None:
        self.window = window
        self.allowed_lateness = allowed_lateness
        self.max_event_time = -1
        self.seen: dict[str, int] = {}

    @property
    def watermark(self) -> int:
        return self.max_event_time - self.allowed_lateness

    def accept(self, event: Event) -> str:
        if event.event_time < self.watermark - self.window:
            return "too_late"
        self.max_event_time = max(self.max_event_time, event.event_time)
        cutoff = self.watermark - self.window
        self.seen = {key: timestamp for key, timestamp in self.seen.items()
                     if timestamp >= cutoff}
        if event.event_id in self.seen:
            return "duplicate"
        self.seen[event.event_id] = event.event_time
        return "accepted"


def main() -> None:
    stream = WindowDeduplicator(window=10, allowed_lateness=3)
    events = [
        Event("e1", 100, 5),
        Event("e2", 104, 7),
        Event("e1", 101, 5),  # late but still within retained state
        Event("e3", 120, 2),  # advances watermark and evicts old IDs
        Event("e1", 100, 5),  # beyond the allowed state horizon
    ]
    outcomes = [stream.accept(event) for event in events]
    assert outcomes == ["accepted", "accepted", "duplicate", "accepted", "too_late"]
    print("Event-time outcomes:", ", ".join(outcomes))
    print("Too-late events require a correction/side-output policy.")


if __name__ == "__main__":
    main()