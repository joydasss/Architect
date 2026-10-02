"""Demonstrate bounded per-key sequence ordering with an in-memory buffer."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    key: str
    sequence: int
    value: str


class ReorderBuffer:
    def __init__(self, key: str, first_sequence: int, max_pending: int = 8) -> None:
        if max_pending < 1:
            raise ValueError("max_pending must be positive")
        self.key = key
        self.next_expected = first_sequence
        self.max_pending = max_pending
        self.pending: dict[int, Event] = {}

    def receive(self, event: Event) -> list[Event]:
        if event.key != self.key:
            raise ValueError(f"expected key {self.key!r}, got {event.key!r}")
        if event.sequence < self.next_expected:
            print(f"stale position {event.sequence}; expected {self.next_expected}")
            return []
        if event.sequence > self.next_expected:
            if event.sequence in self.pending:
                if self.pending[event.sequence] != event:
                    raise ValueError("conflicting payloads claim the same sequence")
                print(f"position {event.sequence} is already buffered")
                return []
            if len(self.pending) >= self.max_pending:
                raise BufferError("pending sequence bound exceeded; repair is required")
            self.pending[event.sequence] = event
            print(f"buffer {event.sequence}; waiting for {self.next_expected}")
            return []

        applied = [event]
        self.next_expected += 1
        while self.next_expected in self.pending:
            applied.append(self.pending.pop(self.next_expected))
            self.next_expected += 1
        return applied


def main() -> None:
    buffer = ReorderBuffer(key="order-7", first_sequence=11, max_pending=4)
    arrivals = [
        Event("order-7", 12, "authorize"),
        Event("order-7", 11, "create"),
        Event("order-7", 14, "ship"),
        Event("order-7", 13, "capture"),
    ]

    for event in arrivals:
        released = buffer.receive(event)
        if released:
            print("apply:", [(item.sequence, item.value) for item in released])

    print(f"next expected sequence: {buffer.next_expected}")


if __name__ == "__main__":
    main()