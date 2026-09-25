-- 01_isolation_level_anomalies.sql
-- Demonstrates dirty read, non-repeatable read, phantom read, and write skew
-- under different PostgreSQL isolation levels, using two concurrent sessions.
-- Run each "Session A" / "Session B" statement block in two separate psql
-- connections to the same database, interleaving them in the numbered order.
--
-- PostgreSQL does not implement Read Uncommitted (it is treated as Read
-- Committed), so the dirty-read block below is annotated to show what WOULD
-- happen on an engine that truly implements Read Uncommitted (e.g. some
-- configurations of SQL Server with READ UNCOMMITTED / NOLOCK).

-- ---------------------------------------------------------------------------
-- Setup: run once
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts (
    id      INT PRIMARY KEY,
    owner   TEXT NOT NULL,
    balance NUMERIC(12, 2) NOT NULL,
    on_call BOOLEAN NOT NULL DEFAULT FALSE
);
INSERT INTO accounts (id, owner, balance, on_call) VALUES
    (1, 'checking', 100.00, TRUE),
    (2, 'savings',  100.00, TRUE);

-- ===========================================================================
-- SCENARIO 1: Dirty read (Read Uncommitted only — annotated, not reproducible
-- on PostgreSQL, which never permits dirty reads at any isolation level)
-- ===========================================================================
-- Session A                                  | Session B
-- ------------------------------------------- | ---------------------------
-- BEGIN;                                      |
-- UPDATE accounts SET balance = 5000          |
--   WHERE id = 1;  -- uncommitted             |
-- -- (does NOT commit yet)                    |
--                                              | -- On a true Read Uncommitted
--                                              | -- engine, this SELECT would
--                                              | -- see 5000 (the dirty,
--                                              | -- uncommitted value):
--                                              | SELECT balance FROM accounts
--                                              |   WHERE id = 1;
-- ROLLBACK;                                   |
--                                              | -- Session B acted on a
--                                              | -- balance that never
--                                              | -- existed once committed.
-- On PostgreSQL, SELECT ... FROM accounts WHERE id = 1 in Session B would
-- block (Read Committed+) or return the last-committed 100.00 (never 5000),
-- because Postgres's storage engine (MVCC, Section 4.11 of the chapter)
-- never exposes uncommitted row versions to other transactions.

-- ===========================================================================
-- SCENARIO 2: Non-repeatable read — prevented by Repeatable Read, permitted
-- by Read Committed
-- ===========================================================================
-- Run with Session A at READ COMMITTED:

-- Session A                                   | Session B
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;
SELECT balance FROM accounts WHERE id = 1;      -- (1) reads 100.00
--                                               | BEGIN;
--                                               | UPDATE accounts SET balance = 250
--                                               |   WHERE id = 1;
--                                               | COMMIT;                      -- (2)
SELECT balance FROM accounts WHERE id = 1;      -- (3) reads 250.00 -- CHANGED!
COMMIT;
-- Step (3) returned a different value than step (1) within the SAME
-- transaction: a non-repeatable read. Re-run this scenario with
-- ISOLATION LEVEL REPEATABLE READ instead, and step (3) will still return
-- 100.00 — the snapshot taken at BEGIN is held for the whole transaction.

-- ===========================================================================
-- SCENARIO 3: Phantom read — prevented by Serializable (and, on PostgreSQL
-- specifically, also prevented by Repeatable Read via Snapshot Isolation;
-- the SQL standard only mandates phantom prevention at Serializable)
-- ===========================================================================
-- Session A                                   | Session B
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;
SELECT count(*) FROM accounts WHERE balance > 50;  -- (1) reads 2
--                                               | BEGIN;
--                                               | INSERT INTO accounts
--                                               |   (id, owner, balance)
--                                               |   VALUES (3, 'brokerage', 900);
--                                               | COMMIT;                      -- (2)
SELECT count(*) FROM accounts WHERE balance > 50;  -- (3) reads 3 -- PHANTOM ROW!
COMMIT;
-- A new row satisfying the same predicate "appeared" between two identical
-- queries in one transaction. PostgreSQL's REPEATABLE READ (implemented via
-- Snapshot Isolation, Section 4.11) also prevents this specific case because
-- the whole table is read from one fixed MVCC snapshot — but the SQL
-- standard's REPEATABLE READ definition does not guarantee this on every
-- engine, so treat phantom-read prevention as a Serializable-tier guarantee
-- unless you have verified your specific engine's implementation.

-- ===========================================================================
-- SCENARIO 4: Write skew — the anomaly Repeatable Read/Snapshot Isolation
-- does NOT prevent, but true Serializable does
-- ===========================================================================
-- Invariant the application relies on: at least one of {checking, savings}
-- must have on_call = TRUE at all times (an on-call rotation constraint).
-- Both accounts start on_call = TRUE. Two doctors each independently decide
-- "I can safely go off-call because my colleague is still on-call" — reading
-- a stale, but individually valid, snapshot.

-- Reset on_call flags before running this scenario:
-- UPDATE accounts SET on_call = TRUE;

-- Session A (isolation REPEATABLE READ)       | Session B (isolation REPEATABLE READ)
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT count(*) FROM accounts WHERE on_call;    -- (1) reads 2 (both TRUE)
--                                               | BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
--                                               | SELECT count(*) FROM accounts WHERE on_call; -- (1') reads 2
UPDATE accounts SET on_call = FALSE WHERE id = 1;  -- (2) A goes off-call
--                                               | UPDATE accounts SET on_call = FALSE WHERE id = 2; -- (2') B goes off-call
COMMIT;                                          -- (3)
--                                               | COMMIT;                     -- (3')
-- Final state: BOTH accounts have on_call = FALSE. Each transaction's own
-- read/write pair was individually consistent with the snapshot it saw, but
-- neither transaction's write conflicted with a row the other transaction
-- physically wrote (they touched DIFFERENT rows), so Snapshot Isolation's
-- first-committer-wins conflict detection never fires. Only a true
-- SERIALIZABLE isolation level (PostgreSQL's Serializable Snapshot
-- Isolation, SSI) detects the read-write dependency cycle between the two
-- transactions and aborts one of them with a serialization failure.

-- Re-run the identical scenario with ISOLATION LEVEL SERIALIZABLE instead of
-- REPEATABLE READ, and PostgreSQL will abort one of the two COMMITs with:
--   ERROR: could not serialize access due to read/write dependencies
--          among transactions
-- forcing the application to retry the losing transaction, which will then
-- correctly observe on_call = FALSE for the other account and refuse to also
-- go off-call.
