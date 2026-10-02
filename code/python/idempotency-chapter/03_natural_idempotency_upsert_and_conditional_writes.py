"""
Chapter: Idempotency - Section 4.4 (natural idempotency via upsert/conditional writes)

Contrasts two operations that need no explicit idempotency-key dedup table
at all, because the underlying write itself is naturally idempotent:

  1. Order creation keyed by a client-supplied `client_order_id` with a
     UNIQUE constraint + `INSERT ... ON CONFLICT DO NOTHING` (an upsert).
     Retrying the exact same "create order" request any number of times
     converges to exactly one row - the database's own constraint does the
     deduplication work that a separate key-store would otherwise do.
  2. A conditional balance debit: `UPDATE accounts SET balance = balance -
     ? WHERE id = ? AND balance >= ?`. Retrying this after a network
     timeout is safe because the WHERE clause re-checks the precondition
     every time; if the first attempt already succeeded, a stale retry
     either changes nothing (balance-based re-check would only be truly
     idempotent when combined with a request-id guard - shown here as a
     contrast to make the limitation explicit) or is naturally rejected.

This file uses sqlite3 (stdlib) purely as a runnable stand-in for a real
relational database's constraint/conditional-update machinery.
"""

from __future__ import annotations

import sqlite3


def build_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_order_id TEXT NOT NULL UNIQUE,
            account_id TEXT NOT NULL,
            amount_cents INTEGER NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE accounts (
            id TEXT PRIMARY KEY,
            balance_cents INTEGER NOT NULL
        )
        """
    )
    conn.execute("INSERT INTO accounts (id, balance_cents) VALUES ('acct-A', 10000)")
    conn.commit()


def create_order_naturally_idempotent(
    conn: sqlite3.Connection, client_order_id: str, account_id: str, amount_cents: int
) -> str:
    """Natural idempotency via a UNIQUE constraint + upsert. Retrying with
    the same client_order_id is a no-op after the first success - the
    database itself is the dedup table, keyed by a column with a uniqueness
    constraint rather than a separate idempotency_keys table."""
    cur = conn.execute(
        """
        INSERT INTO orders (client_order_id, account_id, amount_cents)
        VALUES (?, ?, ?)
        ON CONFLICT(client_order_id) DO NOTHING
        """,
        (client_order_id, account_id, amount_cents),
    )
    conn.commit()
    created_new_row = cur.rowcount == 1
    return "created" if created_new_row else "already_existed"


def conditional_debit(conn: sqlite3.Connection, account_id: str, amount_cents: int) -> bool:
    """Conditional write: the WHERE clause re-verifies the precondition
    (sufficient balance) on every attempt, so an over-drawing retry is
    naturally rejected rather than silently double-debiting. NOTE: this
    alone does not make a *retry of an already-applied* debit safe if the
    balance happens to still satisfy the WHERE clause on the second call -
    see the chapter's discussion of why conditional writes are necessary
    but not always SUFFICIENT for idempotency without an accompanying
    request-id guard (that gap is exactly what Section 4.5's versioned
    state transitions close)."""
    cur = conn.execute(
        """
        UPDATE accounts
        SET balance_cents = balance_cents - ?
        WHERE id = ? AND balance_cents >= ?
        """,
        (amount_cents, account_id, amount_cents),
    )
    conn.commit()
    return cur.rowcount == 1


if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")
    build_schema(conn)

    # --- Natural idempotency via UNIQUE constraint + upsert -----------------
    client_order_id = "web-cart-9f2c1"
    results = [
        create_order_naturally_idempotent(conn, client_order_id, "acct-A", 4200)
        for _ in range(4)  # simulate 4 retries of the exact same create-order call
    ]
    print(f"create_order results across 4 retries: {results}")
    assert results[0] == "created" and all(r == "already_existed" for r in results[1:])

    order_count = conn.execute(
        "SELECT COUNT(*) FROM orders WHERE client_order_id = ?", (client_order_id,)
    ).fetchone()[0]
    print(f"orders rows for {client_order_id!r}: {order_count} (must be exactly 1)")
    assert order_count == 1, "UNIQUE constraint failed to prevent a duplicate order row"

    # --- Conditional write: correctly rejects an over-draw ------------------
    balance_before = conn.execute(
        "SELECT balance_cents FROM accounts WHERE id = 'acct-A'"
    ).fetchone()[0]
    print(f"balance before debit: {balance_before}")

    ok = conditional_debit(conn, "acct-A", 4200)
    print(f"first debit of 4200 applied: {ok}")
    assert ok is True

    balance_after_first = conn.execute(
        "SELECT balance_cents FROM accounts WHERE id = 'acct-A'"
    ).fetchone()[0]
    print(f"balance after first debit: {balance_after_first}")

    # A retry attempting to debit MORE than the remaining balance is
    # naturally rejected by the WHERE clause - no separate idempotency
    # bookkeeping was needed to prevent the overdraft.
    huge_debit_ok = conditional_debit(conn, "acct-A", 999_999)
    print(f"oversized debit correctly rejected: {not huge_debit_ok}")
    assert huge_debit_ok is False

    print("OK: natural idempotency (UNIQUE upsert + conditional WHERE) prevented "
          "duplicate order rows and an overdraft without a separate dedup table")
