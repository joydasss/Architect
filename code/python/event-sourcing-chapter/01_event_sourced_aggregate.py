"""Event-sourced Account aggregate: state derived by replaying events.

Demonstrates the core event-sourcing principle from Section 4.1: the
event log (a list of immutable, ordered facts) is the single source of
truth. Current state is never stored directly -- it is *derived* by
folding (replaying) every event from the beginning, in order, into an
empty starting state. Also demonstrates optimistic concurrency (Section
4.2) via an expected-version check at append time.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


# --- Events: immutable, past-tense facts, never mutated or deleted ---

@dataclass(frozen=True)
class Event:
    aggregate_id: str
    version: int  # position of this event in its stream, starting at 1


@dataclass(frozen=True)
class AccountOpened(Event):
    owner: str
    initial_balance: int  # cents


@dataclass(frozen=True)
class FundsDeposited(Event):
    amount: int  # cents


@dataclass(frozen=True)
class FundsWithdrawn(Event):
    amount: int  # cents


@dataclass(frozen=True)
class AccountClosed(Event):
    reason: str


class InsufficientFundsError(Exception):
    pass


class AccountClosedError(Exception):
    pass


class ConcurrencyConflictError(Exception):
    """Raised when the expected version does not match the stream's actual
    version -- another writer appended events since this aggregate was
    loaded (Section 4.2's optimistic-concurrency check)."""


# --- Aggregate: current state is a projection, not a stored fact ---

@dataclass
class Account:
    account_id: str
    owner: str = ""
    balance: int = 0
    closed: bool = False
    version: int = 0  # last applied event's version == current stream version

    def apply(self, event: Event) -> None:
        """Fold one event into current state. This is the *only* place
        state is mutated -- and it is always driven by an event, never
        by a direct field assignment from a command handler."""
        if isinstance(event, AccountOpened):
            self.owner = event.owner
            self.balance = event.initial_balance
        elif isinstance(event, FundsDeposited):
            self.balance += event.amount
        elif isinstance(event, FundsWithdrawn):
            self.balance -= event.amount
        elif isinstance(event, AccountClosed):
            self.closed = True
        else:
            raise ValueError(f"Unknown event type: {type(event).__name__}")
        self.version = event.version

    @classmethod
    def replay(cls, account_id: str, events: List[Event]) -> "Account":
        """Rebuild an aggregate's current state from scratch by folding
        its entire event history. This is the mechanism behind Section
        4.1's claim that state is a *replayable projection*, not a
        separately persisted fact."""
        account = cls(account_id=account_id)
        for event in events:
            account.apply(event)
        return account

    # --- Command methods: validate invariants, then produce new events ---
    # Note the shape: commands never mutate self.balance/self.closed
    # directly. They validate against current in-memory state, build the
    # new event, and return it for the caller to append + apply.

    def deposit(self, amount: int) -> FundsDeposited:
        if self.closed:
            raise AccountClosedError(f"account {self.account_id} is closed")
        if amount <= 0:
            raise ValueError("deposit amount must be positive")
        return FundsDeposited(
            aggregate_id=self.account_id, version=self.version + 1, amount=amount
        )

    def withdraw(self, amount: int) -> FundsWithdrawn:
        if self.closed:
            raise AccountClosedError(f"account {self.account_id} is closed")
        if amount > self.balance:
            raise InsufficientFundsError(
                f"balance {self.balance} < withdrawal {amount}"
            )
        return FundsWithdrawn(
            aggregate_id=self.account_id, version=self.version + 1, amount=amount
        )

    def close(self, reason: str) -> AccountClosed:
        if self.closed:
            raise AccountClosedError(f"account {self.account_id} already closed")
        return AccountClosed(
            aggregate_id=self.account_id, version=self.version + 1, reason=reason
        )


# --- Event store: append-only log per aggregate stream ---

class EventStore:
    """In-memory stand-in for a real event store (e.g. EventStoreDB,
    a Kafka-compacted topic, or an `events` table keyed by
    (aggregate_id, version)). Real implementations persist durably and
    enforce the expected-version check with a unique constraint on
    (aggregate_id, version) so two concurrent appends at the same
    version cannot both succeed."""

    def __init__(self) -> None:
        self._streams: dict[str, List[Event]] = {}

    def load_stream(self, aggregate_id: str) -> List[Event]:
        return list(self._streams.get(aggregate_id, []))

    def append(
        self, aggregate_id: str, expected_version: int, new_events: List[Event]
    ) -> None:
        stream = self._streams.setdefault(aggregate_id, [])
        actual_version = stream[-1].version if stream else 0
        if actual_version != expected_version:
            raise ConcurrencyConflictError(
                f"expected version {expected_version} but stream is at "
                f"{actual_version} -- reload and retry"
            )
        stream.extend(new_events)


def main() -> None:
    store = EventStore()
    account_id = "acct-1"

    # Open the account: version 0 -> 1
    opened = AccountOpened(
        aggregate_id=account_id, version=1, owner="Priya Shah", initial_balance=10_000
    )
    store.append(account_id, expected_version=0, new_events=[opened])

    # Load current state by replaying the stream so far.
    account = Account.replay(account_id, store.load_stream(account_id))
    print(f"After open: balance={account.balance} version={account.version}")

    # Deposit and withdraw, each round-tripping through the event store.
    deposit_event = account.deposit(2_500)
    store.append(account_id, expected_version=account.version, new_events=[deposit_event])
    account.apply(deposit_event)

    withdraw_event = account.withdraw(4_000)
    store.append(account_id, expected_version=account.version, new_events=[withdraw_event])
    account.apply(withdraw_event)

    print(f"After deposit+withdraw: balance={account.balance} version={account.version}")

    # Demonstrate the optimistic-concurrency failure mode: a second writer
    # loads the same stream, then tries to append using a stale expected
    # version because a third write happened in between.
    stale_account = Account.replay(account_id, store.load_stream(account_id))
    concurrent_withdraw = stale_account.withdraw(1_000)
    store.append(
        account_id,
        expected_version=stale_account.version,
        new_events=[concurrent_withdraw],
    )
    print(f"Concurrent writer succeeded: version={stale_account.version + 1}")

    try:
        # `account` is now stale relative to the store (it doesn't know
        # about the concurrent withdrawal above) -- its append must fail.
        another_withdraw = account.withdraw(500)
        store.append(
            account_id, expected_version=account.version, new_events=[another_withdraw]
        )
    except ConcurrencyConflictError as exc:
        print(f"Expected conflict caught: {exc}")

    # Rebuilding state from the full log always reflects every event that
    # actually committed, regardless of which in-memory copy was stale.
    final = Account.replay(account_id, store.load_stream(account_id))
    print(f"Final replayed state: balance={final.balance} version={final.version}")


if __name__ == "__main__":
    main()
