"""
CQRS projection worker example.

Demonstrates the projection mechanism: an asynchronous consumer that reads
write-side events (in order, exactly once per event) and updates one or more
read models to match. This is the bridge between the write side
(01_command_side.py) and the read side (02_query_side.py) — the concept
this chapter's Section 4.3 teaches in depth, and the same general
event-propagation idea Event Sourcing (the sibling chapter in this batch)
uses for its own write-model replay, though here events are just a
propagation channel, not the system of record.

Idempotency note: each projection tracks the last event_id it applied, so
re-delivering an already-applied event (e.g. after a worker crash-restart)
is a safe no-op rather than double-counting a balance change.

Run: python 03_projection_worker.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from importlib import import_module

command_mod = import_module("01_command_side".replace("-", "_"))  # noqa: E402
query_mod = import_module("02_query_side".replace("-", "_"))  # noqa: E402


class BalanceProjection:
    """Keeps BalanceReadModel rows in sync with write-side events."""

    def __init__(self, reads: "query_mod.ReadModelStore") -> None:
        self._reads = reads
        self._last_applied: dict[str, int] = {}

    def apply(self, event: "command_mod.DomainEvent") -> None:
        last_id = self._last_applied.get(event.account_id, 0)
        if event.event_id <= last_id:
            return  # already applied — idempotent replay guard

        if isinstance(event, command_mod.AccountOpened):
            self._reads.balances[event.account_id] = query_mod.BalanceReadModel(
                event.account_id, event.opening_balance_cents, event.event_id
            )
        elif isinstance(event, (command_mod.FundsWithdrawn, command_mod.FundsDeposited)):
            row = self._reads.balances[event.account_id]
            row.balance_cents = event.resulting_balance_cents
            row.last_event_id = event.event_id

        self._last_applied[event.account_id] = event.event_id


class TransactionHistoryProjection:
    """Keeps the append-only TransactionHistoryEntry feed in sync."""

    def __init__(self, reads: "query_mod.ReadModelStore") -> None:
        self._reads = reads
        self._last_applied: dict[str, int] = {}

    def apply(self, event: "command_mod.DomainEvent") -> None:
        last_id = self._last_applied.get(event.account_id, 0)
        if event.event_id <= last_id:
            return

        history = self._reads.history.setdefault(event.account_id, [])
        if isinstance(event, command_mod.AccountOpened):
            history.append(
                query_mod.TransactionHistoryEntry(
                    event.event_id, event.account_id, "opened",
                    event.opening_balance_cents, event.opening_balance_cents,
                )
            )
        elif isinstance(event, command_mod.FundsDeposited):
            history.append(
                query_mod.TransactionHistoryEntry(
                    event.event_id, event.account_id, "deposit",
                    event.amount_cents, event.resulting_balance_cents,
                )
            )
        elif isinstance(event, command_mod.FundsWithdrawn):
            history.append(
                query_mod.TransactionHistoryEntry(
                    event.event_id, event.account_id, "withdraw",
                    event.amount_cents, event.resulting_balance_cents,
                )
            )

        self._last_applied[event.account_id] = event.event_id


class ProjectionWorker:
    """Drains new write-side events into every registered projection."""

    def __init__(self, store: "command_mod.EventStore") -> None:
        self._store = store
        self._projections: list = []
        self._cursor = 0  # index into the event log this worker has consumed up to

    def register(self, projection) -> None:
        self._projections.append(projection)

    def poll_and_apply(self) -> int:
        events = self._store.all_events()
        new_events = events[self._cursor:]
        for event in new_events:
            for projection in self._projections:
                projection.apply(event)
        self._cursor = len(events)
        return len(new_events)


if __name__ == "__main__":
    store = command_mod.EventStore()
    commands = command_mod.AccountCommandHandler(store)
    reads = query_mod.ReadModelStore()
    queries = query_mod.AccountQueryHandler(reads)

    worker = ProjectionWorker(store)
    worker.register(BalanceProjection(reads))
    worker.register(TransactionHistoryProjection(reads))

    commands.open_account("acc-1", 10_000)
    commands.deposit("acc-1", 2_500)
    commands.withdraw("acc-1", 4_000)

    print("Before the projection worker runs, the read side has nothing yet.")
    applied = worker.poll_and_apply()
    print(f"Projection worker applied {applied} events.")
    print("Balance now visible on the read side:", queries.get_balance("acc-1"))

    # Replaying the same poll again must be a safe no-op (idempotent projection).
    applied_again = worker.poll_and_apply()
    print(f"Second poll applied {applied_again} events (expected 0 — idempotent).")
