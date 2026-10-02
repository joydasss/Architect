"""Snapshotting: avoid replaying an entire history on every load.

Demonstrates Section 4.3: a snapshot is a periodic, materialized
checkpoint of an aggregate's derived state at a specific event version.
Loading becomes "load the latest snapshot, then replay only the events
after it" instead of replaying the full history from event 1 every time.
The snapshot is a performance optimization and cache, never the source
of truth -- it can always be safely deleted and rebuilt by replaying the
event log from scratch (that invariant is proven by the last demo below).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Event:
    aggregate_id: str
    version: int


@dataclass(frozen=True)
class ItemAdded(Event):
    sku: str
    quantity: int


@dataclass(frozen=True)
class ItemRemoved(Event):
    sku: str
    quantity: int


@dataclass
class InventoryCounter:
    """Aggregate whose full history could be tens of thousands of events
    for a busy warehouse bin -- exactly the case snapshotting targets."""

    aggregate_id: str
    counts: Dict[str, int] = field(default_factory=dict)
    version: int = 0

    def apply(self, event: Event) -> None:
        if isinstance(event, ItemAdded):
            self.counts[event.sku] = self.counts.get(event.sku, 0) + event.quantity
        elif isinstance(event, ItemRemoved):
            self.counts[event.sku] = self.counts.get(event.sku, 0) - event.quantity
        else:
            raise ValueError(f"Unknown event type: {type(event).__name__}")
        self.version = event.version

    @classmethod
    def replay(cls, aggregate_id: str, events: List[Event]) -> "InventoryCounter":
        agg = cls(aggregate_id=aggregate_id)
        for event in events:
            agg.apply(event)
        return agg


@dataclass(frozen=True)
class Snapshot:
    aggregate_id: str
    version: int  # the version this snapshot represents -- replay resumes after this
    counts: Dict[str, int]


class EventStoreWithSnapshots:
    def __init__(self, snapshot_every_n_events: int = 100) -> None:
        self._streams: Dict[str, List[Event]] = {}
        self._snapshots: Dict[str, Snapshot] = {}
        self.snapshot_every_n_events = snapshot_every_n_events

    def append(self, aggregate_id: str, expected_version: int, events: List[Event]) -> None:
        stream = self._streams.setdefault(aggregate_id, [])
        actual_version = stream[-1].version if stream else 0
        if actual_version != expected_version:
            raise RuntimeError("concurrency conflict")
        stream.extend(events)
        self._maybe_snapshot(aggregate_id)

    def _maybe_snapshot(self, aggregate_id: str) -> None:
        """A production system typically snapshots asynchronously, off
        the write's critical path, after every N events or every T
        seconds -- shown here synchronously for clarity."""
        stream = self._streams[aggregate_id]
        last_snapshot = self._snapshots.get(aggregate_id)
        last_snapshot_version = last_snapshot.version if last_snapshot else 0
        events_since_snapshot = stream[-1].version - last_snapshot_version
        if events_since_snapshot >= self.snapshot_every_n_events:
            projection = InventoryCounter.replay(aggregate_id, stream)
            self._snapshots[aggregate_id] = Snapshot(
                aggregate_id=aggregate_id,
                version=projection.version,
                counts=dict(projection.counts),
            )
            print(
                f"  [snapshot taken at version {projection.version} "
                f"for {aggregate_id}]"
            )

    def load(self, aggregate_id: str) -> InventoryCounter:
        """Load-with-snapshot: start from the latest snapshot (if any),
        then replay only the events after it -- the whole point of
        snapshotting."""
        snapshot = self._snapshots.get(aggregate_id)
        stream = self._streams.get(aggregate_id, [])
        if snapshot is None:
            return InventoryCounter.replay(aggregate_id, stream)
        agg = InventoryCounter(
            aggregate_id=aggregate_id,
            counts=dict(snapshot.counts),
            version=snapshot.version,
        )
        tail = [e for e in stream if e.version > snapshot.version]
        for event in tail:
            agg.apply(event)
        return agg

    def full_history_events_count(self, aggregate_id: str) -> int:
        return len(self._streams.get(aggregate_id, []))


def main() -> None:
    store = EventStoreWithSnapshots(snapshot_every_n_events=50)
    bin_id = "bin-A1"

    # Simulate 175 events accumulating over the bin's history.
    events: List[Event] = []
    version = 0
    for i in range(175):
        version += 1
        if i % 2 == 0:
            events.append(ItemAdded(aggregate_id=bin_id, version=version, sku="SKU-1", quantity=3))
        else:
            events.append(ItemRemoved(aggregate_id=bin_id, version=version, sku="SKU-1", quantity=1))

    # Append in batches so snapshotting has a chance to trigger partway through.
    batch_size = 25
    for start in range(0, len(events), batch_size):
        batch = events[start : start + batch_size]
        expected = batch[0].version - 1
        store.append(bin_id, expected_version=expected, events=batch)

    total_events = store.full_history_events_count(bin_id)
    print(f"Total events in stream: {total_events}")

    # Timed comparison: replay-from-scratch vs. load-with-snapshot.
    full_stream = store.load(bin_id)  # uses snapshot internally already
    print(f"Loaded via snapshot+tail: version={full_stream.version} "
          f"counts={full_stream.counts}")

    start_time = time.perf_counter()
    from_scratch = InventoryCounter.replay(bin_id, store._streams[bin_id])
    scratch_elapsed = time.perf_counter() - start_time

    start_time = time.perf_counter()
    via_snapshot = store.load(bin_id)
    snapshot_elapsed = time.perf_counter() - start_time

    print(
        f"Replay-from-scratch: {scratch_elapsed * 1e6:.1f}us over "
        f"{total_events} events"
    )
    print(
        f"Snapshot+tail-replay: {snapshot_elapsed * 1e6:.1f}us over "
        f"<= {store.snapshot_every_n_events} tail events"
    )

    # Prove the snapshot is a cache, not a fact: state rebuilt from the
    # full event log alone must match the snapshot-assisted state exactly.
    assert from_scratch.counts == via_snapshot.counts
    assert from_scratch.version == via_snapshot.version
    print("Invariant proven: snapshot-assisted state == full-replay state")


if __name__ == "__main__":
    main()
