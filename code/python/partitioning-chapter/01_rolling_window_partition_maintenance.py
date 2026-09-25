"""01_rolling_window_partition_maintenance.py

Rolling-window partition maintenance for a monthly RANGE-partitioned
time-series table (the "orders" table from
../../sql/partitioning-chapter/01_range_partitioned_table.sql).

Responsibilities, run on a schedule (e.g. a nightly cron job or a Kubernetes
CronJob):
  1. Ensure partitions exist for the current month plus a lead-time buffer
     of future months, so inserts never fall into the DEFAULT partition.
  2. Drop (or detach-and-archive) partitions older than the retention
     window, turning a multi-billion-row DELETE into a near-instant
     metadata-only DROP TABLE.

This script is intentionally idempotent: running it twice in the same month
must not error and must not duplicate partitions.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

import psycopg2

RETENTION_MONTHS = 12  # keep 12 trailing months of "orders" data
LEAD_MONTHS = 3        # always have the next 3 months' partitions pre-created


@dataclass(frozen=True)
class MonthRange:
    start: dt.date  # inclusive, always the first of the month
    end: dt.date    # exclusive, first of the following month

    @property
    def partition_name(self) -> str:
        return f"orders_{self.start:%Y_%m}"


def month_range(year: int, month: int) -> MonthRange:
    start = dt.date(year, month, 1)
    end = dt.date(year + (month // 12), (month % 12) + 1, 1)
    return MonthRange(start, end)


def months_from(anchor: dt.date, offset: int) -> MonthRange:
    total = anchor.year * 12 + (anchor.month - 1) + offset
    return month_range(total // 12, (total % 12) + 1)


def ensure_future_partitions(conn, today: dt.date) -> list[str]:
    """Create any missing partition for [this month .. this month + LEAD_MONTHS]."""
    created = []
    with conn.cursor() as cur:
        for offset in range(0, LEAD_MONTHS + 1):
            mr = months_from(today.replace(day=1), offset)
            cur.execute(
                "SELECT to_regclass(%s) IS NOT NULL",
                (f"public.{mr.partition_name}",),
            )
            (exists,) = cur.fetchone()
            if exists:
                continue
            cur.execute(
                f'CREATE TABLE {mr.partition_name} PARTITION OF orders '
                f"FOR VALUES FROM (%s) TO (%s)",
                (mr.start, mr.end),
            )
            created.append(mr.partition_name)
    conn.commit()
    return created


def drop_expired_partitions(conn, today: dt.date) -> list[str]:
    """Drop any monthly partition whose entire range is older than the
    retention window. DROP TABLE on a partition is metadata-only — it does
    not scan or individually delete rows, unlike DELETE FROM orders WHERE
    created_at < cutoff, which would have to visit every row and every
    index entry being removed (see chapter Section 11 and Section 4.8)."""
    cutoff = months_from(today.replace(day=1), -RETENTION_MONTHS).start
    dropped = []
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT child.relname
            FROM pg_inherits
            JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
            JOIN pg_class child ON pg_inherits.inhrelid = child.oid
            WHERE parent.relname = 'orders'
              AND child.relname ~ '^orders_[0-9]{4}_[0-9]{2}$'
            """
        )
        for (partition_name,) in cur.fetchall():
            year, month = (int(x) for x in partition_name.split("_")[1:3])
            mr = month_range(year, month)
            if mr.end <= cutoff:
                # In a regulated environment, ARCHIVE via DETACH + export to
                # cold storage before DROP; shown here as a plain drop for
                # the pure retention-only case.
                cur.execute(f"DROP TABLE {partition_name}")
                dropped.append(partition_name)
    conn.commit()
    return dropped


def run_maintenance(dsn: str, today: dt.date | None = None) -> None:
    today = today or dt.date.today()
    conn = psycopg2.connect(dsn)
    try:
        created = ensure_future_partitions(conn, today)
        dropped = drop_expired_partitions(conn, today)
        print(f"created={created} dropped={dropped}")
    finally:
        conn.close()


if __name__ == "__main__":
    import os

    run_maintenance(os.environ["ORDERS_DB_DSN"])
