"""Section 9/4.6 - official neo4j Python driver: parameterized Cypher,
explicit write-transaction functions with automatic retry-on-transient-
failure, and a causally-consistent read using a bookmark.

Requires: pip install neo4j
Run against a local Neo4j instance (default bolt://localhost:7687).
"""

from __future__ import annotations

from neo4j import GraphDatabase, Driver, ManagedTransaction, Bookmarks

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password")  # replace with real credentials


def create_person(tx: ManagedTransaction, person_id: str, name: str, age: int) -> None:
    """Parameterized Cypher (Section 13) - never string-concatenate
    untrusted input into a query; bound parameters prevent the
    Cypher-query-language equivalent of SQL injection.
    """
    tx.run(
        """
        MERGE (p:Person {personId: $personId})
        SET p.name = $name, p.age = $age
        """,
        personId=person_id,
        name=name,
        age=age,
    )


def write_person(driver: Driver, person_id: str, name: str, age: int) -> Bookmarks:
    """Explicit write-transaction function (Section 9). The driver
    automatically retries this function if the write fails due to a
    transient cluster condition - e.g. a Raft leader election happening
    mid-transaction (Section 4.6) - without the caller hand-rolling retry
    logic. Returns the session's bookmarks so a subsequent read can prove
    causal consistency with this write.
    """
    with driver.session(database="neo4j") as session:
        session.execute_write(create_person, person_id, name, age)
        return session.last_bookmarks()


def read_person_causally_consistent(
    driver: Driver, person_id: str, bookmarks: Bookmarks
) -> dict | None:
    """Causally-consistent read (Section 4.6). Passing the bookmark
    obtained from the prior write ensures this read - even if routed to a
    Core-server follower or a Read Replica that replicates asynchronously
    - blocks briefly until its applied state has caught up to at least
    that bookmark's point, guaranteeing read-your-writes for this session
    without requiring every cluster member to be fully synchronous.
    """

    def _read(tx: ManagedTransaction, person_id: str) -> dict | None:
        result = tx.run(
            "MATCH (p:Person {personId: $personId}) RETURN p.name AS name, p.age AS age",
            personId=person_id,
        )
        record = result.single()
        return dict(record) if record is not None else None

    with driver.session(database="neo4j", bookmarks=bookmarks) as session:
        return session.execute_read(_read, person_id)


def main() -> None:
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()

        bookmarks = write_person(driver, "p-2001", "Dana", 37)
        person = read_person_causally_consistent(driver, "p-2001", bookmarks)
        print(f"Read-your-write result: {person}")


if __name__ == "__main__":
    main()
