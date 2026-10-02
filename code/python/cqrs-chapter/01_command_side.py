"""
CQRS write-side (command side) example.

Demonstrates:
- A command handler that owns the write model and enforces invariants
  (an account cannot go below its overdraft limit).
- An in-memory "event store" append-only log — the mechanism the
  projection worker (see 03_projection_worker.py) will later read from
  to build read models.
- The write model is optimized for consistency/invariant enforcement,
  NOT for the shape of any query — it only ever answers "is this command
  valid, and what happened as a result."

Run: python 01_command_side.py
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import List


# ---------------------------------------------------------------------------
# Domain events — the write side's output. These are the only thing that
# crosses from the write model to the rest of the system (including any
# read-side projection). See 03_projection_worker.py for the consumer side.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DomainEvent:
    event_id: int
    account_id: str


@dataclass(frozen=True)
class AccountOpened(DomainEvent):
    opening_balance_cents: int


@dataclass(frozen=True)
class FundsWithdrawn(DomainEvent):
    amount_cents: int
    resulting_balance_cents: int


@dataclass(frozen=True)
class FundsDeposited(DomainEvent):
    amount_cents: int
    resulting_balance_cents: int


class InsufficientFundsError(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# In-memory event store: append-only, ordered, replayable. A real system
# would use Kafka, a relational outbox table, or an event-sourced store
# (EventStoreDB) here — the interface is what matters for CQRS: commands
# produce events, nothing else reads the write model's internal state.
# ---------------------------------------------------------------------------
class EventStore:
    def __init__(self) -> None:
        self._log: List[DomainEvent] = []
        self._ids = itertools.count(1)

    def append(self, make_event) -> DomainEvent:
        event = make_event(next(self._ids))
        self._log.append(event)
        return event

    def all_events(self) -> List[DomainEvent]:
        return list(self._log)


# ---------------------------------------------------------------------------
# Write model: the ONLY place invariants are enforced. Note this model does
# not expose any "get balance formatted for a statement" or "get last 10
# transactions" query — those are read-model concerns and live entirely on
# the query side (02_query_side.py). This is the command/query asymmetry
# CQRS is named for.
# ---------------------------------------------------------------------------
@dataclass
class Account:
    account_id: str
    balance_cents: int
    overdraft_limit_cents: int = 0


class AccountCommandHandler:
    """Owns write-side invariants; the read side never enforces these."""

    def __init__(self, store: EventStore) -> None:
        self._store = store
        self._accounts: dict[str, Account] = {}

    def open_account(self, account_id: str, opening_balance_cents: int) -> None:
        if account_id in self._accounts:
            raise ValueError(f"account {account_id} already exists")
        self._accounts[account_id] = Account(account_id, opening_balance_cents)
        self._store.append(
            lambda eid: AccountOpened(eid, account_id, opening_balance_cents)
        )

    def withdraw(self, account_id: str, amount_cents: int) -> None:
        account = self._accounts[account_id]
        floor = -account.overdraft_limit_cents
        if account.balance_cents - amount_cents < floor:
            raise InsufficientFundsError(
                f"withdrawing {amount_cents} would breach overdraft limit"
            )
        account.balance_cents -= amount_cents
        self._store.append(
            lambda eid: FundsWithdrawn(eid, account_id, amount_cents, account.balance_cents)
        )

    def deposit(self, account_id: str, amount_cents: int) -> None:
        account = self._accounts[account_id]
        account.balance_cents += amount_cents
        self._store.append(
            lambda eid: FundsDeposited(eid, account_id, amount_cents, account.balance_cents)
        )


if __name__ == "__main__":
    store = EventStore()
    commands = AccountCommandHandler(store)
    commands.open_account("acc-1", opening_balance_cents=10_000)
    commands.deposit("acc-1", 2_500)
    commands.withdraw("acc-1", 4_000)
    try:
        commands.withdraw("acc-1", 1_000_000)
    except InsufficientFundsError as exc:
        print(f"invariant enforced on write side: {exc}")

    print("Events produced (write-side output, read-side input):")
    for event in store.all_events():
        print(" ", event)
