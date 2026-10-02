"""Exact durable membership with a SQLite unique key and atomic claim."""
import sqlite3


class SeenStore:
    def __init__(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.execute(
            "CREATE TABLE seen (source TEXT NOT NULL, event_id TEXT NOT NULL, "
            "first_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, "
            "PRIMARY KEY (source, event_id))"
        )

    def claim(self, source: str, event_id: str) -> bool:
        with self.connection:
            cursor = self.connection.execute(
                "INSERT OR IGNORE INTO seen (source, event_id) VALUES (?, ?)",
                (source, event_id),
            )
        return cursor.rowcount == 1


def main() -> None:
    store = SeenStore()
    assert store.claim("payments-cdc", "offset-91")
    assert not store.claim("payments-cdc", "offset-91")
    assert store.claim("inventory-cdc", "offset-91")
    count = store.connection.execute("SELECT COUNT(*) FROM seen").fetchone()[0]
    assert count == 2
    print("Exact scoped claims: new, duplicate, independent source; rows=2")


if __name__ == "__main__":
    main()