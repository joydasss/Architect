-- InnoDB next-key locking and gap locking, demonstrated as an interleaved
-- two-session script. Run the "Session A" and "Session B" blocks in two
-- separate mysql client connections, in the numbered order, under
-- REPEATABLE READ (InnoDB's default isolation level) with
-- innodb_locks_unsafe_for_binlog = OFF (the default).

CREATE TABLE accounts (
    id      INT NOT NULL,
    balance INT NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB;

INSERT INTO accounts (id, balance) VALUES (10, 500), (20, 300), (30, 900);
-- Existing primary-key values: 10, 20, 30. The "gaps" InnoDB tracks are
-- (-inf, 10), (10, 20), (20, 30), (30, +inf).

-- ============================================================
-- Step 1 -- Session A: a locking read that takes a next-key lock.
-- ============================================================
START TRANSACTION;
SELECT * FROM accounts WHERE id BETWEEN 10 AND 20 FOR UPDATE;
-- InnoDB does NOT lock only rows id=10 and id=20. Under REPEATABLE READ,
-- a range-scanning locking read takes a NEXT-KEY LOCK: an exclusive lock
-- on each matched index record PLUS the gap immediately before it. Here
-- that covers the gap (-inf,10], the record 10, the gap (10,20], and the
-- record 20 -- i.e. it locks the half-open interval up to and including
-- 20, blocking any insert anywhere in (-inf, 20].
-- (Leave this transaction open -- do not COMMIT yet.)

-- ============================================================
-- Step 2 -- Session B: try to insert id=15, which falls in the LOCKED GAP.
-- ============================================================
START TRANSACTION;
INSERT INTO accounts (id, balance) VALUES (15, 100);
-- BLOCKS. There is no row with id=15 yet, so a plain row lock could never
-- explain this -- this is the gap lock component of Session A's next-key
-- lock preventing a phantom row from appearing inside the range Session A
-- already "saw." This is exactly how InnoDB satisfies REPEATABLE READ's
-- promise that a repeated range query returns the same rows, closing the
-- phantom-read anomaly that pure row-locking cannot close on its own.

-- ============================================================
-- Step 3 -- Session A: commit, releasing the next-key lock.
-- ============================================================
-- COMMIT;
-- Session B's blocked INSERT now proceeds and commits normally.

-- ============================================================
-- Isolating the PURE gap-lock case with GAP-only intent (no existing row)
-- ============================================================
-- A locking read for a non-existent key still takes a lock -- just a pure
-- GAP LOCK (no record lock component, since there is no record):
START TRANSACTION;
SELECT * FROM accounts WHERE id = 25 FOR UPDATE;
-- id=25 doesn't exist. InnoDB takes a gap lock on (20, 30) to guarantee
-- that if this transaction re-runs the same query, no row can have
-- appeared at id=25 in the meantime. Another session's
-- INSERT INTO accounts VALUES (25, ...) now blocks until this COMMITs.

-- ============================================================
-- Opting OUT of gap locking: READ COMMITTED narrows locks to row-only
-- ============================================================
-- SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- START TRANSACTION;
-- SELECT * FROM accounts WHERE id BETWEEN 10 AND 20 FOR UPDATE;
-- Under READ COMMITTED, InnoDB disables next-key/gap locking for
-- non-unique-index scans and uses plain record locks only -- a concurrent
-- INSERT INTO accounts VALUES (15, ...) succeeds immediately. This is the
-- direct mechanical trade-off: READ COMMITTED buys higher write
-- concurrency by re-permitting phantom reads that REPEATABLE READ's
-- gap locks exist specifically to prevent.

-- ============================================================
-- Diagnosing a lock wait / deadlock caused by gap locks in production
-- ============================================================
SELECT * FROM performance_schema.data_locks;         -- current lock holders
SELECT * FROM performance_schema.data_lock_waits;    -- current blocking waits
SHOW ENGINE INNODB STATUS\G                          -- includes LATEST DETECTED DEADLOCK
