"""Replay historical events into an isolated projection generation."""
import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    event_id: str
    order_id: str
    amount: int


class ProjectionConsumer:
    def __init__(self, generation: str, connection: sqlite3.Connection) -> None:
        self.generation = generation
        self.connection = connection
        self.connection.executescript(
            "CREATE TABLE IF NOT EXISTS inbox (generation TEXT, event_id TEXT, "
            "PRIMARY KEY (generation, event_id));"
            "CREATE TABLE IF NOT EXISTS revenue (generation TEXT, order_id TEXT, amount INTEGER, "
            "PRIMARY KEY (generation, order_id));"
        )

    def consume(self, event: Event) -> bool:
        with self.connection:
            cursor = self.connection.execute(
                "INSERT OR IGNORE INTO inbox VALUES (?, ?)",
                (self.generation, event.event_id),
            )
            if cursor.rowcount == 0:
                return False
            self.connection.execute(
                "INSERT INTO revenue VALUES (?, ?, ?) "
                "ON CONFLICT(generation, order_id) DO UPDATE "
                "SET amount = excluded.amount",
                (self.generation, event.order_id, event.amount),
            )
        return True

    def total(self) -> int:
        row = self.connection.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM revenue WHERE generation = ?",
            (self.generation,),
        ).fetchone()
        return row[0]


def main() -> None:
    archive = [Event("cdc-1", "order-1", 120), Event("cdc-2", "order-2", 80)]
    connection = sqlite3.connect(":memory:")
    live = ProjectionConsumer("revenue-v2", connection)
    assert all(live.consume(event) for event in archive)
    assert not live.consume(archive[0])

    rebuilt = ProjectionConsumer("revenue-v3", connection)
    assert all(rebuilt.consume(event) for event in archive)
    assert rebuilt.total() == live.total() == 200
    assert not rebuilt.consume(archive[1])
    print("Replay rebuilt isolated generation: revenue=200; repeat suppressed")
    print("No external side effects are emitted during projection rebuild.")


if __name__ == "__main__":
    main()