"""
Chapter: Idempotency - Section 4.6 (idempotency in message-driven/queue-consumer systems)

Simulates an at-least-once delivery queue that occasionally redelivers a
message (network blip between broker and consumer before the ack lands,
consumer crash after processing but before ack, consumer-group rebalance
replaying an un-committed offset). Two consumers process the exact same
delivery stream:

  * `NaiveConsumer` re-applies every delivery blindly -> double-processes
    duplicates (the bug this whole chapter exists to prevent).
  * `IdempotentConsumer` keeps a dedup table of processed message IDs (with
    a TTL, mirroring 01_idempotency_key_middleware.py's pattern) and safely
    ignores a redelivered message it has already applied, producing the
    same end state as if every message had been delivered exactly once -
    this is "at-least-once delivery behaving like exactly-once at the
    effect level," the concept this chapter defines and the future
    CH17_Exactly_Once_Processing.md/CH19_Deduplication.md chapters build on.
"""

from __future__ import annotations

import random
import sqlite3
import time
from dataclasses import dataclass


@dataclass
class Message:
    message_id: str  # producer-assigned, stable across redeliveries
    account_id: str
    amount_cents: int


class AtLeastOnceQueue:
    """Wraps a list of unique messages and yields a delivery stream where
    some messages are redelivered 1-2 extra times, mimicking real
    at-least-once broker behavior (Kafka/SQS/RabbitMQ with manual acks)."""

    def __init__(self, messages: list[Message], redelivery_rate: float, seed: int = 7):
        self._messages = messages
        self._redelivery_rate = redelivery_rate
        self._rng = random.Random(seed)

    def deliveries(self):
        for msg in self._messages:
            yield msg
            # Simulate a redelivery: the ack was lost, or the consumer
            # crashed after applying the effect but before committing the
            # offset, so the broker redelivers the same message_id again.
            while self._rng.random() < self._redelivery_rate:
                yield msg


class Ledger:
    """SQLite-backed account state shared by both consumer implementations."""

    def __init__(self):
        self.connection = sqlite3.connect(":memory:", isolation_level=None)
        self.connection.execute(
            "CREATE TABLE balances (account_id TEXT PRIMARY KEY, amount_cents INTEGER NOT NULL)"
        )
        self.connection.execute(
            "CREATE TABLE applied_effects (effect_id INTEGER PRIMARY KEY)"
        )

    def credit(self, account_id: str, amount_cents: int) -> None:
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            self.apply_credit_in_transaction(account_id, amount_cents)
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def apply_credit_in_transaction(self, account_id: str, amount_cents: int) -> None:
        self.connection.execute(
            """
            INSERT INTO balances (account_id, amount_cents) VALUES (?, ?)
            ON CONFLICT(account_id) DO UPDATE
            SET amount_cents = amount_cents + excluded.amount_cents
            """,
            (account_id, amount_cents),
        )
        self.connection.execute("INSERT INTO applied_effects DEFAULT VALUES")

    @property
    def balances(self) -> dict[str, int]:
        rows = self.connection.execute(
            "SELECT account_id, amount_cents FROM balances"
        ).fetchall()
        return dict(rows)

    @property
    def applied_count(self) -> int:
        return self.connection.execute("SELECT COUNT(*) FROM applied_effects").fetchone()[0]


class NaiveConsumer:
    """Applies every delivery without checking for duplicates - broken."""

    def __init__(self, ledger: Ledger):
        self.ledger = ledger

    def handle(self, msg: Message) -> None:
        self.ledger.credit(msg.account_id, msg.amount_cents)


class IdempotentConsumer:
    """Dedup-table-backed consumer: applies each unique message_id exactly
    once regardless of how many times the queue redelivers it."""

    def __init__(self, ledger: Ledger, ttl_seconds: float = 3600.0):
        self.ledger = ledger
        self._ttl = ttl_seconds
        self.ledger.connection.execute(
            "CREATE TABLE inbox (message_id TEXT PRIMARY KEY, expires_at REAL NOT NULL)"
        )

    def handle(self, msg: Message) -> None:
        connection = self.ledger.connection
        now = time.time()
        connection.execute("BEGIN IMMEDIATE")
        try:
            # Expiry is safe only when it is longer than the supported broker
            # redelivery and manual replay horizon.
            connection.execute("DELETE FROM inbox WHERE expires_at <= ?", (now,))
            connection.execute(
                "INSERT INTO inbox (message_id, expires_at) VALUES (?, ?)",
                (msg.message_id, now + self._ttl),
            )
            self.ledger.apply_credit_in_transaction(msg.account_id, msg.amount_cents)
            connection.commit()
        except sqlite3.IntegrityError:
            connection.rollback()
            return  # the inbox row proves this effect already committed
        except Exception:
            connection.rollback()
            raise


if __name__ == "__main__":
    unique_messages = [
        Message(message_id="m-1", account_id="acct-A", amount_cents=1000),
        Message(message_id="m-2", account_id="acct-A", amount_cents=2500),
        Message(message_id="m-3", account_id="acct-B", amount_cents=500),
    ]
    expected_total = sum(m.amount_cents for m in unique_messages)

    naive_ledger = Ledger()
    naive_consumer = NaiveConsumer(naive_ledger)
    for delivery in AtLeastOnceQueue(unique_messages, redelivery_rate=0.6, seed=7).deliveries():
        naive_consumer.handle(delivery)

    print(f"[naive]      deliveries applied: {naive_ledger.applied_count} "
          f"(unique messages: {len(unique_messages)}), "
          f"acct-A balance: {naive_ledger.balances['acct-A']} "
          f"(correct value would be "
          f"{sum(m.amount_cents for m in unique_messages if m.account_id == 'acct-A')})")
    assert naive_ledger.applied_count > len(unique_messages), (
        "expected the queue to redeliver at least one message in this demo run"
    )
    print("BUG confirmed: naive consumer double-applied at least one redelivered message")

    idempotent_ledger = Ledger()
    idempotent_consumer = IdempotentConsumer(idempotent_ledger)
    # Same redelivery pattern (same seed), applied through the idempotent consumer.
    for delivery in AtLeastOnceQueue(unique_messages, redelivery_rate=0.6, seed=7).deliveries():
        idempotent_consumer.handle(delivery)

    # Simulate a consumer crash after its database commit but before its
    # broker acknowledgment; the broker later redelivers the same message.
    idempotent_consumer.handle(unique_messages[0])

    print(f"[idempotent] unique applies: {idempotent_ledger.applied_count}, "
          f"acct-A balance: {idempotent_ledger.balances['acct-A']}, "
          f"acct-B balance: {idempotent_ledger.balances['acct-B']}, "
          f"total: {sum(idempotent_ledger.balances.values())} (expected {expected_total})")

    assert idempotent_ledger.applied_count == len(unique_messages), (
        "idempotent consumer applied the wrong number of unique messages"
    )
    assert sum(idempotent_ledger.balances.values()) == expected_total, (
        "idempotent consumer produced the wrong total - duplicates leaked through"
    )
    print("OK: idempotent consumer converged to the correct total despite at-least-once redelivery")
