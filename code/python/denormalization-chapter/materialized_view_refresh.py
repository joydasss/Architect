"""Incremental materialized-view refresh job for an order-summary read model.

Referenced from 06_Databases_and_Storage/CH02_Denormalization.md (Section 10).

Simulates a denormalized `order_summary` materialized view kept in sync with
a normalized `orders` / `order_items` source-of-truth using an incremental
(delta-only) refresh strategy: instead of recomputing every row on every
refresh (eager, full-rebuild) or waiting for an on-demand query (lazy), this
job tracks a high-water mark (`last_refreshed_at`) and only reprocesses rows
that changed since the last run.
"""
from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone


SCHEMA = """
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE order_items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id),
    quantity INTEGER NOT NULL,
    unit_price_cents INTEGER NOT NULL
);

-- Denormalized read model: one row per order, aggregate columns precomputed.
CREATE TABLE order_summary (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    item_count INTEGER NOT NULL,
    total_cents INTEGER NOT NULL,
    refreshed_at TEXT NOT NULL
);

CREATE TABLE refresh_state (
    view_name TEXT PRIMARY KEY,
    last_refreshed_at TEXT NOT NULL
);
"""


@dataclass(frozen=True)
class RefreshResult:
    strategy: str
    rows_examined: int
    rows_upserted: int
    watermark: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def eager_full_refresh(conn: sqlite3.Connection) -> RefreshResult:
    """Rebuild every row from scratch — simplest, most consistent, most expensive.

    Correct after every write, but O(all orders) work regardless of how many
    orders actually changed; only viable while `orders` stays small.
    """
    with closing(conn.cursor()) as cur:
        cur.execute("DELETE FROM order_summary")
        cur.execute(
            """
            INSERT INTO order_summary
                (order_id, customer_id, status, item_count, total_cents, refreshed_at)
            SELECT
                o.order_id,
                o.customer_id,
                o.status,
                COUNT(oi.item_id),
                COALESCE(SUM(oi.quantity * oi.unit_price_cents), 0),
                ?
            FROM orders o
            LEFT JOIN order_items oi ON oi.order_id = o.order_id
            GROUP BY o.order_id
            """,
            (_now(),),
        )
        rows = cur.rowcount
        conn.commit()
    return RefreshResult("eager_full", rows, rows, _now())


def incremental_refresh(conn: sqlite3.Connection) -> RefreshResult:
    """Delta-only refresh: only touch orders changed since the last watermark.

    This is the strategy a production job should use once order volume makes
    a full rebuild too slow to run on every write — the trade-off is that the
    read model can be stale for up to one refresh interval, and the job must
    correctly handle a watermark that is briefly behind an in-flight write
    (see the failure-mode discussion in Section 15 of the chapter).
    """
    with closing(conn.cursor()) as cur:
        cur.execute(
            "SELECT last_refreshed_at FROM refresh_state WHERE view_name = ?",
            ("order_summary",),
        )
        row = cur.fetchone()
        watermark = row[0] if row else "1970-01-01T00:00:00+00:00"

        cur.execute(
            "SELECT order_id FROM orders WHERE updated_at > ?",
            (watermark,),
        )
        changed_order_ids = [r[0] for r in cur.fetchall()]

        for order_id in changed_order_ids:
            cur.execute(
                """
                SELECT
                    o.order_id, o.customer_id, o.status,
                    COUNT(oi.item_id),
                    COALESCE(SUM(oi.quantity * oi.unit_price_cents), 0)
                FROM orders o
                LEFT JOIN order_items oi ON oi.order_id = o.order_id
                WHERE o.order_id = ?
                GROUP BY o.order_id
                """,
                (order_id,),
            )
            summary_row = cur.fetchone()
            cur.execute(
                """
                INSERT INTO order_summary
                    (order_id, customer_id, status, item_count, total_cents, refreshed_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(order_id) DO UPDATE SET
                    customer_id = excluded.customer_id,
                    status = excluded.status,
                    item_count = excluded.item_count,
                    total_cents = excluded.total_cents,
                    refreshed_at = excluded.refreshed_at
                """,
                (*summary_row, _now()),
            )

        new_watermark = _now()
        cur.execute(
            """
            INSERT INTO refresh_state (view_name, last_refreshed_at)
            VALUES (?, ?)
            ON CONFLICT(view_name) DO UPDATE SET last_refreshed_at = excluded.last_refreshed_at
            """,
            ("order_summary", new_watermark),
        )
        conn.commit()

    return RefreshResult(
        "incremental",
        rows_examined=len(changed_order_ids),
        rows_upserted=len(changed_order_ids),
        watermark=new_watermark,
    )


if __name__ == "__main__":
    with closing(sqlite3.connect(":memory:")) as conn:
        conn.executescript(SCHEMA)
        conn.executemany(
            "INSERT INTO orders VALUES (?, ?, ?, ?)",
            [
                (1, 100, "PAID", "2026-01-01T00:00:00+00:00"),
                (2, 101, "PENDING", "2026-01-01T00:00:00+00:00"),
            ],
        )
        conn.executemany(
            "INSERT INTO order_items VALUES (?, ?, ?, ?)",
            [(1, 1, 2, 1999), (2, 1, 1, 500), (3, 2, 3, 750)],
        )
        conn.commit()

        print(eager_full_refresh(conn))
        # Simulate a status change to order 2, then only that order is reprocessed.
        conn.execute(
            "UPDATE orders SET status = 'PAID', updated_at = ? WHERE order_id = 2",
            (_now(),),
        )
        conn.commit()
        print(incremental_refresh(conn))
