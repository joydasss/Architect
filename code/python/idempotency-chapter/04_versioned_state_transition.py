"""
Chapter: Idempotency - Section 4.5 (idempotent state transitions via
versioned/conditional updates)

Demonstrates why a naive "retry the state transition" approach can
double-apply a transition (e.g. re-charging a customer when a `PAID ->
SHIPPED` retry accidentally replays `PENDING -> PAID` logic), and how
guarding every transition with an explicit version number closes that gap.

Model: an order moves through PENDING -> PAID -> SHIPPED. Each transition
is applied via `UPDATE orders SET status = ?, version = version + 1 WHERE
id = ? AND version = ?` - the WHERE clause requires the caller to have read
the exact version the transition applies from. A retried request that
carries the SAME expected version as an already-applied transition matches
zero rows (rowcount = 0) and is therefore a safe, detectable no-op instead
of a silent double-transition - this is optimistic concurrency control
used specifically as an idempotency mechanism, not merely a
lost-update-prevention technique.
"""

from __future__ import annotations

import sqlite3
from enum import Enum


class Status(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"


TRANSITIONS = {
    Status.PENDING: Status.PAID,
    Status.PAID: Status.SHIPPED,
}


class StaleVersionError(Exception):
    """Raised when a transition's expected version no longer matches the
    stored row - either a genuine concurrent conflict, or (the case this
    chapter cares about) a retry of a transition that already applied."""


def build_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE orders (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            version INTEGER NOT NULL
        )
        """
    )
    conn.execute(
        "INSERT INTO orders (id, status, version) VALUES ('order-1', ?, 0)",
        (Status.PENDING.value,),
    )
    conn.commit()


def read_order(conn: sqlite3.Connection, order_id: str) -> tuple[Status, int]:
    row = conn.execute(
        "SELECT status, version FROM orders WHERE id = ?", (order_id,)
    ).fetchone()
    return Status(row[0]), row[1]


def apply_transition(
    conn: sqlite3.Connection, order_id: str, expected_version: int, expected_from: Status
) -> Status:
    """The idempotent-transition primitive: succeeds only if the row is
    still at exactly `expected_version`. On success, returns the new
    status. On a version mismatch, raises StaleVersionError - the caller
    (see the demo below) treats that as "already applied, safe to ignore"
    rather than as a hard failure, which is what makes retries safe."""
    new_status = TRANSITIONS[expected_from]
    cur = conn.execute(
        """
        UPDATE orders
        SET status = ?, version = version + 1
        WHERE id = ? AND version = ? AND status = ?
        """,
        (new_status.value, order_id, expected_version, expected_from.value),
    )
    conn.commit()
    if cur.rowcount == 0:
        raise StaleVersionError(
            f"order {order_id} was not at version {expected_version}/status "
            f"{expected_from.value} - transition already applied or conflicted"
        )
    return new_status


def advance_with_idempotent_retry(conn: sqlite3.Connection, order_id: str) -> None:
    """Simulates a client that calls 'advance to next status' and, believing
    the call timed out, retries the exact same logical transition with the
    SAME expected_version it originally read - the correct client-side
    behavior for a versioned/conditional-update idempotency scheme."""
    status, version = read_order(conn, order_id)
    if status not in TRANSITIONS:
        print(f"order {order_id} has no further transition from {status.value}")
        return

    for attempt in range(1, 4):  # simulate 3 retries of the SAME transition
        try:
            new_status = apply_transition(conn, order_id, version, status)
            print(f"attempt {attempt}: transition applied -> {new_status.value}")
        except StaleVersionError as exc:
            print(f"attempt {attempt}: safely ignored (already applied): {exc}")


if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")
    build_schema(conn)

    print("--- Correct usage: idempotent retry with a fixed expected_version ---")
    advance_with_idempotent_retry(conn, "order-1")
    status, version = read_order(conn, "order-1")
    print(f"final status: {status.value}, version: {version}")
    assert status == Status.PAID and version == 1, "expected exactly one transition to apply"

    print("\n--- Contrast: WITHOUT versioning, a blind retry re-reads current "
          "state each time and can double-advance ---")
    build_schema_conn = sqlite3.connect(":memory:")
    build_schema(build_schema_conn)

    def naive_advance_no_version(conn: sqlite3.Connection, order_id: str) -> Status:
        """The bug: re-reads current status fresh on every retry instead of
        pinning to the version the client originally observed, so a retry
        issued AFTER the first attempt's effect has already been read by
        another process can advance the state an extra time."""
        status, _ = read_order(conn, order_id)
        new_status = TRANSITIONS[status]
        conn.execute(
            "UPDATE orders SET status = ?, version = version + 1 WHERE id = ?",
            (new_status.value, order_id),
        )
        conn.commit()
        return new_status

    # Two "retries" of what the client believes is the SAME transition
    # request, but because there is no version guard, each call re-reads
    # whatever the current status is and blindly advances it again.
    first = naive_advance_no_version(build_schema_conn, "order-1")
    second = naive_advance_no_version(build_schema_conn, "order-1")
    print(f"naive first call result: {first.value}, second call result: {second.value}")
    final_status, _ = read_order(build_schema_conn, "order-1")
    print(f"naive final status: {final_status.value} (order was double-advanced: "
          f"PENDING -> PAID -> SHIPPED from what the client intended as one transition)")
    assert final_status == Status.SHIPPED, "expected the naive version to double-advance"

    print("\nOK: versioned/conditional updates make a retried transition a safe "
          "no-op; the unversioned naive retry silently double-advances instead")
