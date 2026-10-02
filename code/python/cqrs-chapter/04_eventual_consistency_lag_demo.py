"""
CQRS end-to-end demo: makes the eventual-consistency window between the
write side and the read side observable, instead of just asserting it in
prose. A background thread plays the role of an asynchronous projection
worker (as it would be in production: a separate consumer process reading
off a queue/log), while the main thread issues a command and then polls the
read side, showing a window where the query returns stale data.

Run: python 04_eventual_consistency_lag_demo.py
"""
from __future__ import annotations

import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from importlib import import_module

command_mod = import_module("01_command_side".replace("-", "_"))
query_mod = import_module("02_query_side".replace("-", "_"))
projection_mod = import_module("03_projection_worker".replace("-", "_"))


PROJECTION_DELAY_SECONDS = 0.15  # simulates realistic queue/consumer lag


def run_background_projection_worker(
    worker: "projection_mod.ProjectionWorker", stop: threading.Event
) -> None:
    while not stop.is_set():
        time.sleep(PROJECTION_DELAY_SECONDS)
        worker.poll_and_apply()


def main() -> None:
    store = command_mod.EventStore()
    commands = command_mod.AccountCommandHandler(store)
    reads = query_mod.ReadModelStore()
    queries = query_mod.AccountQueryHandler(reads)

    worker = projection_mod.ProjectionWorker(store)
    worker.register(projection_mod.BalanceProjection(reads))
    worker.register(projection_mod.TransactionHistoryProjection(reads))

    stop_event = threading.Event()
    bg_thread = threading.Thread(
        target=run_background_projection_worker, args=(worker, stop_event), daemon=True
    )
    bg_thread.start()

    commands.open_account("acc-1", 10_000)
    print("Command accepted: account opened with balance 10000 (write side is immediately consistent).")

    print("Immediately reading the read side (projection has not run yet):")
    try:
        queries.get_balance("acc-1")
        print("  (unexpected: read model already present)")
    except KeyError:
        print("  read side raised KeyError — the projection has not caught up yet.")
        print("  This is the eventually-consistent window: the write succeeded,")
        print("  but a query issued immediately after can observe stale/missing data.")

    # Wait past the simulated projection delay, then read again.
    time.sleep(PROJECTION_DELAY_SECONDS * 2)
    balance = queries.get_balance("acc-1")
    print(f"After waiting for the projection to catch up, balance is now visible: {balance}")

    stop_event.set()
    bg_thread.join(timeout=1)


if __name__ == "__main__":
    main()
