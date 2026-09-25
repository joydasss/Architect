"""
Chapter: Distributed Transactions - Section 4.5
A complete transactional outbox implementation:
  - The business write and the outbox row are inserted in ONE local SQLite
    transaction (single-node ACID, no cross-system coordination needed).
  - A polling publisher reads unpublished outbox rows in strict insertion
    order and publishes them to an in-memory broker stand-in.
  - The publisher can crash mid-batch (simulated) and safely resume,
    re-publishing already-published-but-unacknowledged rows - proving why
    every consumer must be idempotent under at-least-once delivery.
"""

import sqlite3


class InMemoryBroker:
    """Broker stand-in that records every delivered message, including duplicates."""

    def __init__(self):
        self.deliveries: list[str] = []

    def publish(self, event: str) -> None:
        self.deliveries.append(event)


class IdempotentConsumer:
    """Downstream consumer that safely tolerates at-least-once redelivery."""

    def __init__(self):
        self.processed_ids: set[str] = set()
        self.side_effects_applied = 0

    def handle(self, event: str) -> None:
        event_id = event.split(":")[1]
        if event_id in self.processed_ids:
            return  # duplicate delivery - safely ignored, this is the idempotency guarantee
        self.processed_ids.add(event_id)
        self.side_effects_applied += 1


def setup_db() -> sqlite3.Connection:
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, status TEXT)")
    db.execute(
        """CREATE TABLE outbox (
               seq INTEGER PRIMARY KEY AUTOINCREMENT,
               event TEXT NOT NULL,
               published INTEGER NOT NULL DEFAULT 0
           )"""
    )
    return db


def place_order(db: sqlite3.Connection, order_id: int) -> None:
    """Business write + outbox row, atomic because they share one local transaction."""
    cur = db.cursor()
    cur.execute("INSERT INTO orders (id, status) VALUES (?, ?)", (order_id, "placed"))
    cur.execute(
        "INSERT INTO outbox (event, published) VALUES (?, 0)",
        (f"OrderPlaced:{order_id}",),
    )
    db.commit()  # single ACID commit - both rows exist, or neither does


def run_publisher_batch(
    db: sqlite3.Connection, broker: InMemoryBroker, crash_after: int | None = None
) -> None:
    """Polling publisher: reads unpublished rows in insertion order, publishes,
    marks published. `crash_after` simulates the publisher dying mid-batch
    after publishing but before marking a row published, forcing redelivery
    on the next run."""
    cur = db.cursor()
    rows = cur.execute(
        "SELECT seq, event FROM outbox WHERE published = 0 ORDER BY seq ASC"
    ).fetchall()

    for i, (seq, event) in enumerate(rows):
        broker.publish(event)
        if crash_after is not None and i == crash_after:
            # Simulated crash: the publish above happened, but the UPDATE
            # below never runs, so this row is republished on the next batch.
            print(f"  [simulated publisher crash after seq={seq}]")
            return
        cur.execute("UPDATE outbox SET published = 1 WHERE seq = ?", (seq,))
        db.commit()


def run_demo() -> None:
    db = setup_db()
    broker = InMemoryBroker()
    consumer = IdempotentConsumer()

    for order_id in range(1, 6):
        place_order(db, order_id)

    print("First publisher run (crashes after publishing order 3, before marking it published):")
    run_publisher_batch(db, broker, crash_after=2)  # 0-indexed: 3rd row

    print("Second publisher run (resumes, republishes order 3 - a duplicate delivery):")
    run_publisher_batch(db, broker)

    for event in broker.deliveries:
        consumer.handle(event)

    unpublished = db.execute(
        "SELECT COUNT(*) FROM outbox WHERE published = 0"
    ).fetchone()[0]

    print(f"\nTotal broker deliveries (includes 1 duplicate): {len(broker.deliveries)}")
    print(f"Unique side effects applied by consumer        : {consumer.side_effects_applied}")
    print(f"Unpublished outbox rows remaining               : {unpublished}")

    assert len(broker.deliveries) == 6, "expected 5 orders + 1 duplicate redelivery"
    assert consumer.side_effects_applied == 5, "consumer must de-duplicate the redelivery"
    assert unpublished == 0, "every order must eventually be published"
    print("\nEvery order was delivered at-least-once, and the idempotent consumer")
    print("applied exactly 5 side effects despite 6 deliveries - the outbox")
    print("pattern's core guarantee, demonstrated end to end.")


if __name__ == "__main__":
    run_demo()
