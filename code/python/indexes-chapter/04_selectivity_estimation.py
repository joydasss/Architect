"""Estimate column selectivity/cardinality to decide index candidacy.

Referenced from 06_Databases_and_Storage/CH03_Indexes.md (Section 10).

Builds a small SQLite dataset, then computes cardinality (distinct value
count) and selectivity (distinct values / total rows) per column, mirroring
the estimate a query planner's statistics catalog keeps -- see Section 4.7.
A column with selectivity close to 1.0 is a strong standalone index
candidate; a column with selectivity close to 0 (few distinct values over
many rows) is a poor standalone candidate and is usually only useful as a
non-leading column in a composite index.
"""
import random
import sqlite3
from dataclasses import dataclass


@dataclass
class ColumnStats:
    column: str
    distinct_values: int
    total_rows: int

    @property
    def selectivity(self) -> float:
        return self.distinct_values / self.total_rows

    @property
    def avg_rows_per_value(self) -> float:
        return self.total_rows / self.distinct_values

    def recommendation(self) -> str:
        if self.selectivity >= 0.10:
            return "GOOD standalone index candidate (high selectivity)"
        if self.selectivity >= 0.01:
            return "MARGINAL: consider as part of a composite index only"
        return "POOR standalone index candidate (low selectivity)"


def build_sample_database(path: str, row_count: int = 200_000) -> None:
    conn = sqlite3.connect(path)
    conn.execute("DROP TABLE IF EXISTS events")
    conn.execute(
        """
        CREATE TABLE events (
            event_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            is_error INTEGER NOT NULL
        )
        """
    )
    event_types = ["click", "view", "purchase", "signup", "logout"]
    rows = [
        (
            i,
            random.randint(1, 40_000),          # user_id: high cardinality
            random.choice(event_types),          # event_type: medium cardinality
            1 if random.random() < 0.02 else 0,  # is_error: very low cardinality
        )
        for i in range(row_count)
    ]
    conn.executemany(
        "INSERT INTO events (event_id, user_id, event_type, is_error) VALUES (?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()


def compute_selectivity(path: str, column: str, total_rows: int) -> ColumnStats:
    conn = sqlite3.connect(path)
    (distinct_count,) = conn.execute(
        f"SELECT COUNT(DISTINCT {column}) FROM events"
    ).fetchone()
    conn.close()
    return ColumnStats(column=column, distinct_values=distinct_count, total_rows=total_rows)


def main() -> None:
    db_path = "events_selectivity_demo.sqlite3"
    row_count = 200_000
    build_sample_database(db_path, row_count)

    for column in ("user_id", "event_type", "is_error"):
        stats = compute_selectivity(db_path, column, row_count)
        print(
            f"{stats.column:12s} distinct={stats.distinct_values:>7d} "
            f"selectivity={stats.selectivity:.5f} "
            f"avg_rows_per_value={stats.avg_rows_per_value:>9.1f}  "
            f"-> {stats.recommendation()}"
        )


if __name__ == "__main__":
    main()
