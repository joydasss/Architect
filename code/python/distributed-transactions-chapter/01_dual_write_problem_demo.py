"""
Chapter: Distributed Transactions - Section 4.1
Demonstrates the dual-write problem: a service commits a local database
write and then makes a separate call to "publish" an event. Because the
two calls are not covered by any shared atomicity mechanism, a failure
between them silently loses the event even though the business write
succeeded. The second half of this script fixes it with the transactional
outbox pattern (taught in full in 02_transactional_outbox.py).
"""

import sqlite3
import random


class UnreliableBroker:
    """A message broker stand-in that randomly fails to simulate a network blip."""

    def __init__(self, failure_rate: float):
        self.failure_rate = failure_rate
        self.delivered_events: list[str] = []

    def publish(self, event: str) -> None:
        if random.random() < self.failure_rate:
            raise ConnectionError("broker unreachable (simulated network blip)")
        self.delivered_events.append(event)


def naive_dual_write(db: sqlite3.Connection, broker: UnreliableBroker, order_id: int) -> bool:
    """The unsafe pattern: two independent writes, no shared atomicity."""
    cur = db.cursor()
    cur.execute("INSERT INTO orders (id, status) VALUES (?, ?)", (order_id, "placed"))
    db.commit()  # write #1 durably succeeds no matter what happens next

    try:
        broker.publish(f"OrderPlaced:{order_id}")  # write #2 - independently failing
        return True
    except ConnectionError:
        # The order row above is now permanently committed with no event ever
        # published - this is the dual-write problem's silent data-loss failure.
        return False


def run_demo() -> None:
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, status TEXT)")
    broker = UnreliableBroker(failure_rate=0.4)

    lost_events = 0
    for order_id in range(1, 21):
        ok = naive_dual_write(db, broker, order_id)
        if not ok:
            lost_events += 1

    order_count = db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    print(f"Orders committed to the database : {order_count}")
    print(f"Events successfully published     : {len(broker.delivered_events)}")
    print(f"Silently lost events (dual-write bug): {lost_events}")
    assert order_count > len(broker.delivered_events), (
        "expected at least one lost event to demonstrate the dual-write problem"
    )
    print("\nThis is the dual-write problem: every order row above is committed,")
    print("but some will never have a corresponding downstream event - see")
    print("02_transactional_outbox.py for the fix.")


if __name__ == "__main__":
    random.seed(7)  # deterministic output for the walkthrough
    run_demo()
