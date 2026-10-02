"""Event store as CQRS write model + a projection as the CQRS read model.

Demonstrates Section 4.5: Event Sourcing pairs naturally with CQRS
(Command Query Responsibility Segregation) -- the append-only event log
IS the write model, and one or more projections built by folding that
log into a different shape ARE the CQRS read model(s). This file only
shows the mechanical seam between the two; the full CQRS read/write
split, query-side scaling, and staleness trade-offs are owned by the
sibling CQRS chapter (see CH14_CQRS.md) and are deliberately not
re-taught here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class Event:
    aggregate_id: str
    version: int


@dataclass(frozen=True)
class OrderPlaced(Event):
    customer_id: str
    total_cents: int


@dataclass(frozen=True)
class OrderShipped(Event):
    carrier: str


@dataclass(frozen=True)
class OrderCancelled(Event):
    reason: str


class EventStore:
    """The write side: an append-only log per aggregate stream. Commands
    validate against a freshly replayed aggregate and, on success, append
    new events here -- nothing else is the write model."""

    def __init__(self) -> None:
        self._streams: Dict[str, List[Event]] = {}
        self._subscribers: List["Projection"] = []

    def subscribe(self, projection: "Projection") -> None:
        self._subscribers.append(projection)

    def append(self, aggregate_id: str, expected_version: int, events: List[Event]) -> None:
        stream = self._streams.setdefault(aggregate_id, [])
        actual_version = stream[-1].version if stream else 0
        if actual_version != expected_version:
            raise RuntimeError("concurrency conflict")
        stream.extend(events)
        # Publish to projections -- in a real system this is typically
        # asynchronous (via a message broker or the store's own
        # subscription API), which is exactly why CQRS read models are
        # eventually consistent, not transactionally consistent with the
        # write. That staleness trade-off belongs to the CQRS chapter.
        for projection in self._subscribers:
            for event in events:
                projection.apply(event)

    def load_stream(self, aggregate_id: str) -> List[Event]:
        return list(self._streams.get(aggregate_id, []))


@dataclass
class OrderSummaryRow:
    order_id: str
    customer_id: str = ""
    total_cents: int = 0
    status: str = "placed"


class Projection:
    """A CQRS read model built purely by folding the event stream into a
    query-optimized shape -- here, a flat dict keyed by order_id, but in
    production this is typically a denormalized SQL table, a search
    index, or a cache, chosen for the query patterns it needs to serve,
    completely independent of the event log's own layout."""

    def __init__(self) -> None:
        self.rows: Dict[str, OrderSummaryRow] = {}

    def apply(self, event: Event) -> None:
        if isinstance(event, OrderPlaced):
            self.rows[event.aggregate_id] = OrderSummaryRow(
                order_id=event.aggregate_id,
                customer_id=event.customer_id,
                total_cents=event.total_cents,
                status="placed",
            )
        elif isinstance(event, OrderShipped):
            row = self.rows[event.aggregate_id]
            row.status = f"shipped via {event.carrier}"
        elif isinstance(event, OrderCancelled):
            row = self.rows[event.aggregate_id]
            row.status = f"cancelled: {event.reason}"

    def orders_for_customer(self, customer_id: str) -> List[OrderSummaryRow]:
        """The read side answers a query shape (all orders for a
        customer) that would require scanning every stream in the write
        model -- this is precisely why the read model exists as a
        separate, purpose-built structure."""
        return [r for r in self.rows.values() if r.customer_id == customer_id]


def main() -> None:
    store = EventStore()
    read_model = Projection()
    store.subscribe(read_model)

    # Command: place two orders for the same customer.
    store.append(
        "order-1",
        expected_version=0,
        events=[
            OrderPlaced(
                aggregate_id="order-1", version=1, customer_id="cust-9", total_cents=4200
            )
        ],
    )
    store.append(
        "order-2",
        expected_version=0,
        events=[
            OrderPlaced(
                aggregate_id="order-2", version=1, customer_id="cust-9", total_cents=1500
            )
        ],
    )

    # Command: ship one order, cancel the other.
    store.append(
        "order-1", expected_version=1, events=[OrderShipped(aggregate_id="order-1", version=2, carrier="UPS")]
    )
    store.append(
        "order-2",
        expected_version=1,
        events=[OrderCancelled(aggregate_id="order-2", version=2, reason="customer request")],
    )

    # Query side: served entirely from the projection, never from replaying
    # write-side streams.
    for row in read_model.orders_for_customer("cust-9"):
        print(row)

    # The write model remains the durable source of truth: the projection
    # could be dropped and rebuilt from scratch by replaying every stream
    # from the beginning, which is exactly what Section 4.1 means by
    # "state as a derived, replayable projection" -- applied here to a
    # cross-aggregate read model instead of a single aggregate's state.
    rebuilt = Projection()
    for aggregate_id in ("order-1", "order-2"):
        for event in store.load_stream(aggregate_id):
            rebuilt.apply(event)
    assert rebuilt.rows == read_model.rows
    print("Rebuilt projection from raw event log matches live projection")


if __name__ == "__main__":
    main()
