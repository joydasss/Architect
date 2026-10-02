"""Process tumbling windows using a bounded-disorder event-time watermark."""

from collections import defaultdict
from datetime import datetime, timedelta, timezone


class EventTimeProcessor:
    def __init__(self, window_size: timedelta, allowed_disorder: timedelta) -> None:
        if window_size <= timedelta(0):
            raise ValueError("window_size must be positive")
        if allowed_disorder < timedelta(0):
            raise ValueError("allowed_disorder cannot be negative")
        self.window_size = window_size
        self.allowed_disorder = allowed_disorder
        self.max_event_time: datetime | None = None
        self.watermark: datetime | None = None
        self.windows: dict[datetime, list[str]] = defaultdict(list)
        self.late_events: list[tuple[datetime, str]] = []

    def window_start(self, event_time: datetime) -> datetime:
        seconds = int(event_time.timestamp())
        width = int(self.window_size.total_seconds())
        return datetime.fromtimestamp(seconds - seconds % width, tz=timezone.utc)

    def close_ready_windows(self) -> list[tuple[datetime, list[str]]]:
        if self.watermark is None:
            return []
        ready = []
        for start in sorted(self.windows):
            if start + self.window_size <= self.watermark:
                ready.append((start, self.windows.pop(start)))
        return ready

    def process(self, event_time: datetime, value: str) -> list[tuple[datetime, list[str]]]:
        event_time = event_time.astimezone(timezone.utc)
        if self.watermark is not None and event_time <= self.watermark:
            self.late_events.append((event_time, value))
            print(f"late side output: {event_time.isoformat()} {value}")
            return []

        self.windows[self.window_start(event_time)].append(value)
        if self.max_event_time is None or event_time > self.max_event_time:
            self.max_event_time = event_time
        candidate = self.max_event_time - self.allowed_disorder
        if self.watermark is None or candidate > self.watermark:
            self.watermark = candidate
            print(f"watermark advanced to {self.watermark.isoformat()}")
        return self.close_ready_windows()

    def finish(self) -> list[tuple[datetime, list[str]]]:
        if self.max_event_time is not None:
            self.watermark = max(
                self.watermark or self.max_event_time,
                self.max_event_time + self.window_size,
            )
        return self.close_ready_windows()


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


def main() -> None:
    processor = EventTimeProcessor(
        window_size=timedelta(minutes=1),
        allowed_disorder=timedelta(seconds=30),
    )
    events = [
        ("2026-10-02T10:00:10", "reading-a"),
        ("2026-10-02T10:01:05", "reading-c"),
        ("2026-10-02T10:00:40", "reading-b-late-but-allowed"),
        ("2026-10-02T10:00:20", "reading-too-late"),
        ("2026-10-02T10:02:00", "reading-d"),
    ]

    for timestamp, value in events:
        for start, values in processor.process(parse_time(timestamp), value):
            print("closed window:", start.isoformat(), values)

    for start, values in processor.finish():
        print("final window:", start.isoformat(), values)
    print("late event count:", len(processor.late_events))


if __name__ == "__main__":
    main()