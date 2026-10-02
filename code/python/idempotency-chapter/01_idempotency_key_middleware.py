"""
Chapter: Idempotency - Section 4.3 (idempotency-key deduplication table with TTL)

Implements a Stripe-style idempotency-key middleware/decorator as a small,
self-contained, in-memory reference implementation (no web framework
dependency, so it runs anywhere). A client attaches an `Idempotency-Key`
header (a client-generated UUID) to a state-changing request. The
middleware:

  1. Looks up the key in a dedup table.
  2. If not present: runs the handler, stores {status, body, request_hash,
     expires_at}, and returns the fresh result.
  3. If present and the stored request_hash matches the incoming request's
     hash: returns the STORED response without re-running the handler
     (this is what makes a retried POST safe).
  4. If present but the request_hash differs: rejects with a 409-style
     conflict - the same key must not be reused for a materially different
     request, since that would silently return the wrong cached result.
  5. Entries expire after a TTL (Time To Live); once expired, the key is
     treated as new again - this bounds the dedup table's storage growth at
     the cost of a (deliberately small) window where a very late retry
     could double-execute.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time


class ConflictError(Exception):
    """Raised when a reused idempotency key carries a different request body."""


class ResponseLostError(Exception):
    """Simulates a committed operation whose response did not reach the caller."""


class IdempotencyStore:
    """SQLite-backed key store; the claim, ledger effect, and result commit together."""

    def __init__(self, ttl_seconds: float = 86400.0):
        self._ttl = ttl_seconds
        self._connection = sqlite3.connect(":memory:", isolation_level=None)
        self._connection.execute(
            """
            CREATE TABLE operations (
                operation_key TEXT PRIMARY KEY,
                request_hash TEXT NOT NULL,
                state TEXT NOT NULL,
                status_code INTEGER,
                response_body TEXT,
                expires_at REAL NOT NULL
            )
            """
        )
        self._connection.execute(
            """
            CREATE TABLE charges (
                charge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount_cents INTEGER NOT NULL,
                currency TEXT NOT NULL
            )
            """
        )

    @staticmethod
    def _hash_request(payload: dict) -> str:
        canonical = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    def execute_once(self, key: str, payload: dict, handler) -> tuple[int, dict, bool]:
        """Claim the key, run its local effect, and save the outcome atomically."""
        connection = self._connection
        now = time.time()
        connection.execute("BEGIN IMMEDIATE")
        try:
            connection.execute("DELETE FROM operations WHERE expires_at <= ?", (now,))
            request_hash = self._hash_request(payload)
            existing = connection.execute(
                "SELECT request_hash, state, status_code, response_body "
                "FROM operations WHERE operation_key = ?",
                (key,),
            ).fetchone()
            if existing is not None:
                if existing[0] != request_hash:
                    raise ConflictError(
                        f"idempotency key {key!r} was already used with a different request body"
                    )
                if existing[1] != "COMPLETED":
                    raise RuntimeError("operation is not in a replayable terminal state")
                connection.commit()
                return existing[2], json.loads(existing[3]), True

            connection.execute(
                "INSERT INTO operations "
                "(operation_key, request_hash, state, expires_at) VALUES (?, ?, 'IN_PROGRESS', ?)",
                (key, request_hash, now + self._ttl),
            )
            status_code, body = handler(connection, payload)
            connection.execute(
                "UPDATE operations SET state = 'COMPLETED', status_code = ?, response_body = ? "
                "WHERE operation_key = ?",
                (status_code, json.dumps(body, sort_keys=True), key),
            )
            connection.commit()
            return status_code, body, False
        except Exception:
            connection.rollback()
            raise

    def size(self) -> int:
        return self._connection.execute("SELECT COUNT(*) FROM operations").fetchone()[0]

    def charge_count(self) -> int:
        return self._connection.execute("SELECT COUNT(*) FROM charges").fetchone()[0]


def idempotent(store: IdempotencyStore):
    """Decorator: wraps a handler(payload) -> (status_code, body) with
    idempotency-key deduplication. The caller supplies the key out-of-band
    (as an HTTP header would), passed here as an explicit argument to keep
    the demo framework-agnostic."""

    def decorator(handler):
        def wrapper(idempotency_key: str, payload: dict, simulate_lost_response: bool = False):
            status_code, body, replayed = store.execute_once(
                idempotency_key, payload, handler
            )
            if simulate_lost_response and not replayed:
                raise ResponseLostError("operation committed before the response was lost")
            return status_code, {**body, "replayed_from_cache": replayed}

        return wrapper

    return decorator


# --- Demo: a "charge card" effect in the same transaction as its key --------

def _charge_card(connection: sqlite3.Connection, payload: dict) -> tuple[int, dict]:
    """Simulates a charge ledger insert protected by the operation transaction."""
    cursor = connection.execute(
        "INSERT INTO charges (amount_cents, currency) VALUES (?, ?)",
        (payload["amount_cents"], payload["currency"]),
    )
    charge_id = cursor.lastrowid
    return 201, {
        "charge_id": charge_id,
        "amount_cents": payload["amount_cents"],
        "currency": payload["currency"],
        "status": "succeeded",
    }


if __name__ == "__main__":
    store = IdempotencyStore(ttl_seconds=60.0)
    charge = idempotent(store)(_charge_card)

    key = "11111111-2222-3333-4444-555555555555"
    payload = {"amount_cents": 5000, "currency": "USD"}

    # The first call commits, then simulates a lost response. The retry must
    # recover the original outcome without inserting another ledger charge.
    try:
        charge(key, payload, simulate_lost_response=True)
    except ResponseLostError as exc:
        print(f"first attempt: {exc}")

    for attempt in range(2, 4):
        status, body = charge(key, payload)
        print(f"attempt {attempt}: status={status} body={body}")

    print(f"ledger entries (should be exactly 1): {store.charge_count()}")
    assert store.charge_count() == 1, "double charge detected - idempotency middleware failed"

    # A different payload under the SAME key must be rejected, not silently
    # charged again or silently returned as if it matched.
    try:
        charge(key, {"amount_cents": 9999, "currency": "USD"})
        raise AssertionError("expected ConflictError for reused key with different payload")
    except ConflictError as exc:
        print(f"correctly rejected reused key with different body: {exc}")

    # A fresh key for a genuinely new charge must go through normally.
    status, body = charge("66666666-7777-8888-9999-000000000000", payload)
    print(f"new key, new charge: status={status} body={body}")
    print(f"ledger entries (should be exactly 2): {store.charge_count()}")
    assert store.charge_count() == 2

    print(f"dedup table size: {store.size()}")
    print("OK: idempotency-key middleware prevented duplicate charges on retry")
