-- Pessimistic locking with SELECT ... FOR UPDATE (PostgreSQL syntax)
-- Implements CH10_Locking.md Sections 4.1 and 4.3.
--
-- Run this against a scratch database. Open two psql sessions ("Session A"
-- and "Session B") and follow the numbered steps to interleave them and
-- observe row-level exclusive locking block a conflicting writer.

-- Setup (run once, in either session)
DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts (
    id      INT PRIMARY KEY,
    balance NUMERIC NOT NULL CHECK (balance >= 0)
);
INSERT INTO accounts (id, balance) VALUES (1, 500), (2, 300);

-- =====================================================================
-- Demo 1: FOR UPDATE blocks a concurrent writer on the same row
-- =====================================================================

-- --- Session A ---
BEGIN;
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;
-- balance = 500. Do NOT commit yet -- keep this transaction open.

-- --- Session B (run while Session A's transaction is still open) ---
-- This will BLOCK until Session A commits or rolls back, because the
-- exclusive lock Session A's FOR UPDATE acquired conflicts with the
-- exclusive lock this UPDATE needs (see the lock-compatibility matrix,
-- Section 4.1).
UPDATE accounts SET balance = balance - 100 WHERE id = 1;

-- --- Session A ---
-- Now commit; Session B's blocked UPDATE will proceed immediately.
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;

-- =====================================================================
-- Demo 2: consistent lock ordering as deadlock prevention (Section 4.6)
-- =====================================================================
-- Two transfer functions below both lock the LOWER account id first,
-- regardless of which account is the transfer's source or destination --
-- this is the fix for the "opposite-order acquisition" anti-pattern
-- (Section 19) that would otherwise let two concurrent transfers deadlock.

-- Transfer A pays B (accounts 1 -> 2): lock ordering is (1, 2)
BEGIN;
SELECT balance FROM accounts WHERE id = LEAST(1, 2) FOR UPDATE;
SELECT balance FROM accounts WHERE id = GREATEST(1, 2) FOR UPDATE;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- Transfer B pays A (accounts 2 -> 1): lock ordering is STILL (1, 2),
-- even though the logical direction of the transfer is reversed --
-- this is what eliminates the circular-wait condition structurally.
BEGIN;
SELECT balance FROM accounts WHERE id = LEAST(1, 2) FOR UPDATE;
SELECT balance FROM accounts WHERE id = GREATEST(1, 2) FOR UPDATE;
UPDATE accounts SET balance = balance - 100 WHERE id = 2;
UPDATE accounts SET balance = balance + 100 WHERE id = 1;
COMMIT;

-- =====================================================================
-- Demo 3: fail-fast with an explicit lock_timeout (Section 4.7)
-- =====================================================================

-- --- Session A ---
BEGIN;
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;
-- keep this open

-- --- Session B ---
BEGIN;
SET LOCAL lock_timeout = '2s';
-- This raises a "canceling statement due to lock timeout" error after
-- 2 seconds instead of queuing indefinitely behind Session A.
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;
ROLLBACK;

-- --- Session A ---
COMMIT;
