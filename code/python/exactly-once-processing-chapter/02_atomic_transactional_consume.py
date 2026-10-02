"""Commit inbox identity, business state, and source position in SQLite."""

import sqlite3


def create_database() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.executescript(
        """
        CREATE TABLE accounts (
            account_id TEXT PRIMARY KEY,
            balance INTEGER NOT NULL
        );
        CREATE TABLE inbox (
            partition_id INTEGER NOT NULL,
            offset_value INTEGER NOT NULL,
            event_id TEXT NOT NULL,
            PRIMARY KEY (partition_id, offset_value),
            UNIQUE (partition_id, event_id)
        );
        CREATE TABLE source_positions (
            partition_id INTEGER PRIMARY KEY,
            next_offset INTEGER NOT NULL
        );
        INSERT INTO accounts VALUES ('acct-1', 100);
        INSERT INTO source_positions VALUES (0, 0);
        """
    )
    return connection


def consume(
    connection: sqlite3.Connection,
    partition_id: int,
    offset_value: int,
    event_id: str,
    amount: int,
    crash_before_commit: bool = False,
) -> str:
    try:
        with connection:
            position = connection.execute(
                "SELECT next_offset FROM source_positions WHERE partition_id = ?",
                (partition_id,),
            ).fetchone()[0]
            if offset_value < position:
                return "duplicate: already committed"
            if offset_value != position:
                raise ValueError(f"expected offset {position}, got {offset_value}")

            connection.execute(
                "INSERT INTO inbox(partition_id, offset_value, event_id) VALUES (?, ?, ?)",
                (partition_id, offset_value, event_id),
            )
            connection.execute(
                "UPDATE accounts SET balance = balance + ? WHERE account_id = 'acct-1'",
                (amount,),
            )
            connection.execute(
                "UPDATE source_positions SET next_offset = ? WHERE partition_id = ?",
                (offset_value + 1, partition_id),
            )
            if crash_before_commit:
                raise RuntimeError("simulated process crash before database commit")
    except RuntimeError:
        return "crashed: transaction rolled back"
    return "committed: acknowledge broker now"


def current_state(connection: sqlite3.Connection) -> tuple[int, int]:
    balance = connection.execute(
        "SELECT balance FROM accounts WHERE account_id = 'acct-1'"
    ).fetchone()[0]
    next_offset = connection.execute(
        "SELECT next_offset FROM source_positions WHERE partition_id = 0"
    ).fetchone()[0]
    return balance, next_offset


def main() -> None:
    connection = create_database()
    failed = consume(connection, 0, 0, "event-0", 25, crash_before_commit=True)
    print(f"first attempt: {failed}; state={current_state(connection)}")
    assert current_state(connection) == (100, 0)

    committed = consume(connection, 0, 0, "event-0", 25)
    print(f"redelivery: {committed}; state={current_state(connection)}")
    assert current_state(connection) == (125, 1)

    # Simulates commit succeeding while the broker acknowledgment is lost.
    duplicate = consume(connection, 0, 0, "event-0", 25)
    print(f"after lost broker acknowledgment: {duplicate}; state={current_state(connection)}")
    assert current_state(connection) == (125, 1)

    try:
        gap = consume(connection, 0, 2, "event-2", 5)
    except ValueError as error:
        gap = str(error)
    print(f"out-of-order position: {gap}")
    assert "expected offset 1" in gap
    connection.close()


if __name__ == "__main__":
    main()