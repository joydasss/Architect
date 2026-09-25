"""
04_connection_model_and_pgbouncer_demo.py

Measures per-connection backend memory overhead directly against
pg_stat_activity/pg_backend_pid, and contrasts unpooled versus PgBouncer
transaction-mode-pooled connection behavior under concurrent load. See
CH11_PostgreSQL.md Sections 4.12-4.13 for the mechanisms this demonstrates.

Requires: psycopg2 (or psycopg 3), and a reachable PostgreSQL instance.
Optionally requires PgBouncer running in transaction-pooling mode on a
second port to run the pooled-vs-unpooled comparison in main().

    pip install psycopg2-binary
"""

from __future__ import annotations

import os
import statistics
import threading
import time

import psycopg2

DIRECT_DSN = os.environ.get(
    "PG_DIRECT_DSN", "dbname=postgres host=localhost port=5432 user=postgres"
)
# PgBouncer listening in transaction-pooling mode, fronting the same database.
POOLED_DSN = os.environ.get(
    "PG_POOLED_DSN", "dbname=postgres host=localhost port=6432 user=postgres"
)


def backend_memory_kb(pid: int) -> int | None:
    """Read a PostgreSQL backend process's resident memory via /proc.

    Only works when the client and PostgreSQL server share the same host
    (e.g. local development or a test container) -- in production, this
    metric would instead come from OS-level process monitoring on the DB
    host. Returns None if /proc is unavailable (non-Linux) or unreadable.
    """
    status_path = f"/proc/{pid}/status"
    try:
        with open(status_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1])
    except (FileNotFoundError, PermissionError):
        return None
    return None


def open_direct_connections(count: int) -> list[psycopg2.extensions.connection]:
    """Open `count` direct connections -- each forks a new PostgreSQL
    backend OS process (CH11_PostgreSQL.md Section 4.12)."""
    conns = []
    for _ in range(count):
        conn = conns_or_raise(DIRECT_DSN)
        conns.append(conn)
    return conns


def conns_or_raise(dsn: str) -> psycopg2.extensions.connection:
    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    return conn


def measure_backend_memory(connections: list[psycopg2.extensions.connection]) -> list[int]:
    """For each connection, ask PostgreSQL for its own backend PID via
    pg_backend_pid(), then read that process's resident memory."""
    memory_samples = []
    for conn in connections:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_backend_pid();")
            (pid,) = cur.fetchone()
        mem_kb = backend_memory_kb(pid)
        if mem_kb is not None:
            memory_samples.append(mem_kb)
    return memory_samples


def demo_process_per_connection_cost(connection_count: int = 50) -> None:
    """Opens many direct connections and reports the aggregate backend
    memory footprint -- the concrete cost behind Section 4.12's claim that
    every additional connection is additional worst-case memory/scheduling
    overhead whether or not it is concurrently active."""
    print(f"Opening {connection_count} direct connections (one OS process each)...")
    connections = open_direct_connections(connection_count)
    try:
        samples = measure_backend_memory(connections)
        if samples:
            total_kb = sum(samples)
            print(f"  Backends measured: {len(samples)}")
            print(f"  Mean backend RSS:  {statistics.mean(samples):.0f} KB")
            print(f"  Total backend RSS: {total_kb} KB (~{total_kb / 1024:.1f} MB)")
            print(
                "  Extrapolated to max_connections=200: "
                f"~{total_kb / len(samples) * 200 / 1024:.1f} MB baseline, "
                "before any query-driven work_mem usage."
            )
        else:
            print("  (Could not read /proc memory -- not on Linux, or DB is remote.)")
    finally:
        for conn in connections:
            conn.close()


def run_transaction(dsn: str) -> float:
    """Runs one short, representative transaction and returns its latency
    in seconds -- the workload shape transaction-mode pooling assumes."""
    start = time.perf_counter()
    conn = psycopg2.connect(dsn)
    try:
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
        conn.commit()
    finally:
        conn.close()
    return time.perf_counter() - start


def demo_pooled_vs_direct_under_concurrency(
    concurrency: int = 200, requests_per_client: int = 5
) -> None:
    """Fires many concurrent short transactions against both a direct
    connection and (if available) a PgBouncer transaction-mode pool, and
    compares completion behavior -- direct connections are expected to
    degrade or hit max_connections well before the pooled path does, per
    CH11_PostgreSQL.md Section 4.12's failure mode."""

    def run_workload(dsn: str, label: str) -> None:
        latencies: list[float] = []
        errors = 0
        lock = threading.Lock()

        def worker() -> None:
            nonlocal errors
            for _ in range(requests_per_client):
                try:
                    latency = run_transaction(dsn)
                    with lock:
                        latencies.append(latency)
                except psycopg2.OperationalError as exc:
                    with lock:
                        errors += 1
                    print(f"  [{label}] connection error: {exc}")

        threads = [threading.Thread(target=worker) for _ in range(concurrency)]
        start = time.perf_counter()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        elapsed = time.perf_counter() - start

        print(f"[{label}] concurrency={concurrency}, total requests={concurrency * requests_per_client}")
        print(f"  Elapsed: {elapsed:.2f}s, errors: {errors}")
        if latencies:
            print(
                f"  Latency mean={statistics.mean(latencies) * 1000:.1f}ms "
                f"p95={sorted(latencies)[int(len(latencies) * 0.95)] * 1000:.1f}ms"
            )

    print("--- Direct connections (process-per-connection, no pooling) ---")
    run_workload(DIRECT_DSN, "direct")

    print("\n--- PgBouncer transaction-mode pool ---")
    try:
        run_workload(POOLED_DSN, "pooled")
    except psycopg2.OperationalError as exc:
        print(f"  PgBouncer not reachable at {POOLED_DSN}: {exc}")
        print("  Start PgBouncer in transaction-pooling mode to run this half.")


def main() -> None:
    demo_process_per_connection_cost(connection_count=50)
    print()
    demo_pooled_vs_direct_under_concurrency(concurrency=200, requests_per_client=5)


if __name__ == "__main__":
    main()
