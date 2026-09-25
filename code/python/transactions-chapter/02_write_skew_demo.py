"""
02_write_skew_demo.py

Reproduces the write-skew anomaly from the chapter's Section 4.13 against a
real PostgreSQL database using two concurrent connections, then reruns the
identical scenario at SERIALIZABLE isolation to show the transaction abort
and a correct retry loop.

Requires: pip install psycopg2-binary
Requires a reachable PostgreSQL instance; set PG_DSN below or via env var.
"""

import os
import threading
import time

import psycopg2
from psycopg2 import errorcodes

PG_DSN = os.environ.get("PG_DSN", "dbname=postgres user=postgres host=localhost")

SETUP_SQL = """
DROP TABLE IF EXISTS on_call_roster;
CREATE TABLE on_call_roster (
    id      INT PRIMARY KEY,
    doctor  TEXT NOT NULL,
    on_call BOOLEAN NOT NULL
);
INSERT INTO on_call_roster (id, doctor, on_call) VALUES
    (1, 'Dr. Alvarez', TRUE),
    (2, 'Dr. Brennan', TRUE);
"""


def setup():
    conn = psycopg2.connect(PG_DSN)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(SETUP_SQL)
    conn.close()


def go_off_call(doctor_id: int, isolation_level: str, barrier: threading.Barrier, results: dict):
    """Each doctor independently checks 'is at least one colleague still on
    call?' and, if so, takes themselves off call. Under Repeatable Read /
    Snapshot Isolation both doctors can pass this check concurrently and both
    go off-call — violating the "at least one on-call" invariant. Under
    Serializable, PostgreSQL detects the read-write conflict and aborts one."""
    conn = psycopg2.connect(PG_DSN)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}")
            # (1) Read: is anyone ELSE still on call?
            cur.execute(
                "SELECT count(*) FROM on_call_roster WHERE on_call AND id != %s",
                (doctor_id,),
            )
            (others_on_call,) = cur.fetchone()

            # Synchronize both transactions so they read their snapshot at
            # roughly the same logical moment, maximizing the chance of
            # reproducing the anomaly deterministically.
            barrier.wait()

            if others_on_call > 0:
                # (2) Write: safe to go off call, since a colleague covers us.
                cur.execute(
                    "UPDATE on_call_roster SET on_call = FALSE WHERE id = %s",
                    (doctor_id,),
                )
                conn.commit()
                results[doctor_id] = "went off-call"
            else:
                conn.rollback()
                results[doctor_id] = "stayed on-call (no colleague available)"
    except psycopg2.Error as exc:
        conn.rollback()
        if exc.pgcode == errorcodes.T_R_SERIALIZATION_FAILURE:
            results[doctor_id] = "ABORTED (serialization_failure) — must retry"
        else:
            raise
    finally:
        conn.close()


def run_scenario(isolation_level: str) -> dict:
    setup()
    barrier = threading.Barrier(2)
    results: dict = {}
    threads = [
        threading.Thread(target=go_off_call, args=(1, isolation_level, barrier, results)),
        threading.Thread(target=go_off_call, args=(2, isolation_level, barrier, results)),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results


def print_final_state(label: str):
    conn = psycopg2.connect(PG_DSN)
    with conn.cursor() as cur:
        cur.execute("SELECT doctor, on_call FROM on_call_roster ORDER BY id")
        rows = cur.fetchall()
    conn.close()
    on_call_count = sum(1 for _, on_call in rows if on_call)
    print(f"\n[{label}] Final roster: {rows}")
    print(f"[{label}] Doctors still on call: {on_call_count} "
          f"({'INVARIANT VIOLATED' if on_call_count == 0 else 'invariant held'})")


if __name__ == "__main__":
    print("=== Scenario A: REPEATABLE READ (Snapshot Isolation) ===")
    results_rr = run_scenario("REPEATABLE READ")
    print(results_rr)
    print_final_state("REPEATABLE READ")

    time.sleep(0.5)

    print("\n=== Scenario B: SERIALIZABLE ===")
    results_ser = run_scenario("SERIALIZABLE")
    print(results_ser)
    print_final_state("SERIALIZABLE")

    print(
        "\nExpected outcome: Scenario A ends with ZERO doctors on call "
        "(write skew — the invariant silently breaks). Scenario B ends with "
        "exactly ONE doctor going off-call and the other transaction aborted "
        "with a serialization_failure, which a correctly-written client "
        "retries — after the retry, the invariant holds."
    )
