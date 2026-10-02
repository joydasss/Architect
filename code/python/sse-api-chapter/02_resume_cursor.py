"""Runnable in-memory model of bounded, strictly-after feed replay."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeedEvent:
    position: int
    payload: str


@dataclass(frozen=True)
class ReplayResult:
    events: tuple[FeedEvent, ...]
    reset_required: bool
    oldest_position: int
    high_watermark: int


class RetainedFeed:
    def __init__(self, events: list[FeedEvent]) -> None:
        if not events:
            raise ValueError("the model requires at least one retained event")
        positions = [event.position for event in events]
        if positions != sorted(set(positions)):
            raise ValueError("event positions must be strictly increasing")
        self._events = tuple(events)

    def resume(self, last_event_id: str | None) -> ReplayResult:
        cursor = int(last_event_id) if last_event_id is not None else 0
        oldest = self._events[0].position
        high_watermark = self._events[-1].position
        if cursor < oldest - 1:
            return ReplayResult((), True, oldest, high_watermark)
        if cursor > high_watermark:
            raise ValueError("cursor is beyond the feed high-water mark")
        replay = tuple(event for event in self._events if event.position > cursor)
        return ReplayResult(replay, False, oldest, high_watermark)


def main() -> None:
    feed = RetainedFeed(
        [
            FeedEvent(101, "order accepted"),
            FeedEvent(102, "payment captured"),
            FeedEvent(103, "order shipped"),
        ]
    )
    for cursor in ("101", "98"):
        result = feed.resume(cursor)
        if result.reset_required:
            print(
                f"cursor {cursor}: reset required; retained floor is "
                f"{result.oldest_position}, high-water mark is "
                f"{result.high_watermark}"
            )
        else:
            print(f"cursor {cursor}: {[event.payload for event in result.events]}")


if __name__ == "__main__":
    main()