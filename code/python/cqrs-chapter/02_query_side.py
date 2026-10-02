"""
CQRS read-side (query side) example.

Demonstrates:
- Multiple, differently-shaped read models built from the SAME underlying
  write-side events — this is the payoff of separating the read model from
  the write model: each query gets a model shaped exactly for it, instead
  of one normalized schema serving every access pattern.
- Query handlers are pure readers: they never validate business invariants
  (that already happened on the write side) and never mutate write state.

This file defines the read-model tables and query handlers only; see
03_projection_worker.py for how these tables get populated/kept up to date
from write-side events, and 04_end_to_end_demo.py for the full pipeline.

Run: python 02_query_side.py (uses a small pre-populated fixture)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


# ---------------------------------------------------------------------------
# Read model #1: current-balance lookup, optimized for O(1) point reads
# (e.g. rendering an account dashboard). Denormalized: it duplicates data
# that also exists as write-side events, on purpose.
# ---------------------------------------------------------------------------
@dataclass
class BalanceReadModel:
    account_id: str
    balance_cents: int
    last_event_id: int


# ---------------------------------------------------------------------------
# Read model #2: a transaction history feed, optimized for "show the last N
# transactions" (append-only list, newest-first) — a completely different
# shape than the balance lookup, even though both are derived from the same
# events. This is the essence of CQRS's read-model flexibility.
# ---------------------------------------------------------------------------
@dataclass
class TransactionHistoryEntry:
    event_id: int
    account_id: str
    kind: str
    amount_cents: int
    resulting_balance_cents: int


class ReadModelStore:
    """The read-side "database" — could be Postgres, Redis, Elasticsearch,
    or a denormalized document store; here it's two in-memory dicts to keep
    the example runnable without external infrastructure."""

    def __init__(self) -> None:
        self.balances: Dict[str, BalanceReadModel] = {}
        self.history: Dict[str, List[TransactionHistoryEntry]] = {}


class AccountQueryHandler:
    def __init__(self, reads: ReadModelStore) -> None:
        self._reads = reads

    def get_balance(self, account_id: str) -> int:
        return self._reads.balances[account_id].balance_cents

    def get_recent_transactions(self, account_id: str, limit: int = 10) -> List[TransactionHistoryEntry]:
        entries = self._reads.history.get(account_id, [])
        return list(reversed(entries[-limit:]))


if __name__ == "__main__":
    reads = ReadModelStore()
    reads.balances["acc-1"] = BalanceReadModel("acc-1", 8_500, last_event_id=3)
    reads.history["acc-1"] = [
        TransactionHistoryEntry(1, "acc-1", "opened", 10_000, 10_000),
        TransactionHistoryEntry(2, "acc-1", "deposit", 2_500, 12_500),
        TransactionHistoryEntry(3, "acc-1", "withdraw", 4_000, 8_500),
    ]

    queries = AccountQueryHandler(reads)
    print("Balance:", queries.get_balance("acc-1"))
    print("Recent transactions (newest first):")
    for entry in queries.get_recent_transactions("acc-1"):
        print(" ", entry)
