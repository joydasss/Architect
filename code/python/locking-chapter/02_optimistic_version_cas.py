"""Optimistic concurrency control: version-column compare-and-swap retry loop.

Implements CH10_Locking.md Section 4.4 end to end against a real
PostgreSQL database, including a deliberate concurrent-conflict
demonstration and a bounded exponential-backoff retry loop.

Setup:
    pip install psycopg2-binary
    createdb locking_demo   # or point DSN below at an existing database

Run:
    python 02_optimistic_version_cas.py
"""

import random
import threading
import time

import psycopg2

DSN = "dbname=locking_demo"


def setup(conn):
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS documents")
        cur.execute(
            """
            CREATE TABLE documents (
                id      INT PRIMARY KEY,
                data    TEXT NOT NULL,
                version INT NOT NULL DEFAULT 1
            )
            """
        )
        cur.execute(
            "INSERT INTO documents (id, data, version) VALUES (%s, %s, %s)",
            (1, "original content", 1),
        )
    conn.commit()


def update_with_optimistic_lock(dsn, row_id, mutate_fn, max_retries=5, label=""):
    """Section 4.4's version-column compare-and-swap pattern with retry."""
    conn = psycopg2.connect(dsn)
    try:
        for attempt in range(1, max_retries + 1):
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT data, version FROM documents WHERE id = %s", (row_id,)
                )
                data, version = cur.fetchone()

                # Simulate "think time" between read and write -- exactly the
                # window optimistic concurrency control does NOT lock across,
                # unlike SELECT ... FOR UPDATE (Section 4.3).
                time.sleep(0.05)

                new_data = mutate_fn(data)
                cur.execute(
                    "UPDATE documents SET data = %s, version = version + 1 "
                    "WHERE id = %s AND version = %s",
                    (new_data, row_id, version),
                )
                if cur.rowcount == 1:
                    conn.commit()
                    print(f"[{label}] succeeded on attempt {attempt}: "
                          f"version {version} -> {version + 1}, data={new_data!r}")
                    return
                conn.rollback()
                print(f"[{label}] attempt {attempt} lost the CAS race "
                      f"(row changed since version {version}), retrying")
                backoff = min(0.5, 0.05 * (2 ** attempt)) + random.uniform(0, 0.05)
                time.sleep(backoff)
        raise RuntimeError(f"[{label}] exceeded max_retries under sustained contention")
    finally:
        conn.close()


def demo_concurrent_conflict():
    """Two writers race to update the same row; exactly one CAS wins per
    round, and the loser must re-read and retry (Section 4.4's scenario)."""
    conn = psycopg2.connect(DSN)
    setup(conn)
    conn.close()

    def worker(label, suffix):
        update_with_optimistic_lock(
            DSN, row_id=1, mutate_fn=lambda d: f"{d} + {suffix}", label=label
        )

    t1 = threading.Thread(target=worker, args=("Agent A", "note-from-A"))
    t2 = threading.Thread(target=worker, args=("Agent B", "note-from-B"))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    conn = psycopg2.connect(DSN)
    with conn.cursor() as cur:
        cur.execute("SELECT data, version FROM documents WHERE id = 1")
        print("Final row state:", cur.fetchone())
    conn.close()


if __name__ == "__main__":
    demo_concurrent_conflict()
