"""05_sga_pga_diagnostics.py

Connects to an Oracle instance and prints a human-readable SGA component
breakdown, PGA aggregate usage, and top wait events -- tying Chapter
Sections 4.2-4.3 (SGA/PGA memory architecture) to live diagnostic queries
an architect can run against a real system.

Requires: pip install oracledb
Connection details are read from environment variables so no credentials
are hard-coded:
    ORACLE_DSN   e.g. "localhost:1521/ORCLPDB1"
    ORACLE_USER  e.g. "diag_user" (needs SELECT on V$SGASTAT/V$PGASTAT/
                 V$SYSTEM_EVENT, typically granted via SELECT_CATALOG_ROLE)
    ORACLE_PASSWORD
"""
from __future__ import annotations

import os
import sys

import oracledb


def fetch_rows(cursor: oracledb.Cursor, sql: str) -> list[tuple]:
    cursor.execute(sql)
    return cursor.fetchall()


def print_sga_breakdown(cursor: oracledb.Cursor) -> None:
    print("=== SGA component breakdown (V$SGASTAT) ===")
    rows = fetch_rows(
        cursor,
        """
        SELECT pool, name, ROUND(SUM(bytes) / 1024 / 1024, 2) AS mb
        FROM   v$sgastat
        GROUP  BY pool, name
        ORDER  BY mb DESC
        FETCH FIRST 10 ROWS ONLY
        """,
    )
    for pool, name, mb in rows:
        pool_label = pool if pool else "(fixed)"
        print(f"  {pool_label:14s} {name:35s} {mb:>10.2f} MB")


def print_pga_summary(cursor: oracledb.Cursor) -> None:
    print("\n=== PGA aggregate usage (V$PGASTAT) ===")
    rows = fetch_rows(
        cursor,
        """
        SELECT name, ROUND(value / 1024 / 1024, 2) AS mb
        FROM   v$pgastat
        WHERE  name IN (
            'aggregate PGA target parameter',
            'total PGA allocated',
            'total PGA used for auto workareas',
            'total freeable PGA memory'
        )
        """,
    )
    for name, mb in rows:
        print(f"  {name:40s} {mb:>10.2f} MB")


def print_top_wait_events(cursor: oracledb.Cursor) -> None:
    print("\n=== Top wait events by total wait time (V$SYSTEM_EVENT) ===")
    rows = fetch_rows(
        cursor,
        """
        SELECT event, total_waits, ROUND(time_waited_micro / 1000000, 2) AS seconds
        FROM   v$system_event
        WHERE  wait_class != 'Idle'
        ORDER  BY time_waited_micro DESC
        FETCH FIRST 8 ROWS ONLY
        """,
    )
    for event, total_waits, seconds in rows:
        print(f"  {event:35s} waits={total_waits:>10}  total={seconds:>10.2f}s")


def main() -> int:
    dsn = os.environ.get("ORACLE_DSN")
    user = os.environ.get("ORACLE_USER")
    password = os.environ.get("ORACLE_PASSWORD")
    if not (dsn and user and password):
        print(
            "Set ORACLE_DSN, ORACLE_USER, ORACLE_PASSWORD environment "
            "variables before running this script.",
            file=sys.stderr,
        )
        return 1

    with oracledb.connect(user=user, password=password, dsn=dsn) as conn:
        with conn.cursor() as cursor:
            print_sga_breakdown(cursor)
            print_pga_summary(cursor)
            print_top_wait_events(cursor)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
