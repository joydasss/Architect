-- 02_read_consistency_demo.sql
-- Two-session, interleaved walkthrough proving Oracle's undo-segment-based
-- read consistency (Chapter Section 4.6): a long-running query keeps
-- returning its original snapshot while a concurrent session commits
-- changes to the same rows.
--
-- Run "Session A" and "Session B" blocks in two separate SQL*Plus / SQLcl
-- connections to the same database, interleaving them in the numbered order.
-- Uses the oracle_ch_accounts table created by 01_tablespace_and_undo_setup.sql.

-- ===========================================================================
-- Step 1 (Session A): begin a long-running, snapshot-consistent query
-- ===========================================================================
-- Session A:
DECLARE
    v_balance NUMBER;
BEGIN
    -- Simulates a long-running report: read once, sleep, read again.
    SELECT balance INTO v_balance
    FROM   oracle_ch_accounts
    WHERE  account_id = 1;

    DBMS_OUTPUT.PUT_LINE('Session A - first read: ' || v_balance);

    -- Give Session B time to commit a change to the same row.
    DBMS_LOCK.SLEEP(15);

    SELECT balance INTO v_balance
    FROM   oracle_ch_accounts
    WHERE  account_id = 1;

    DBMS_OUTPUT.PUT_LINE('Session A - second read (same txn/snapshot): ' || v_balance);
END;
/

-- ===========================================================================
-- Step 2 (Session B): concurrently update and commit the same row,
-- WHILE Session A's block above is sleeping
-- ===========================================================================
-- Session B:
UPDATE oracle_ch_accounts
SET    balance = balance + 500
WHERE  account_id = 1;
COMMIT;

SELECT balance FROM oracle_ch_accounts WHERE account_id = 1;
-- Session B immediately sees the new, committed balance.

-- ===========================================================================
-- Expected result once Session A's block finishes:
--   - If Session A's two reads are in the SAME transaction under
--     REPEATABLE READ / SERIALIZABLE-style snapshot semantics (Oracle's
--     default READ COMMITTED re-snapshots per STATEMENT, not per
--     transaction -- each SELECT in the block above takes its own fresh
--     snapshot), Session A's second read WILL reflect Session B's commit
--     under Oracle's default isolation level.
--   - To see Oracle's stronger guarantee, wrap Session A's block in
--     `SET TRANSACTION ISOLATION LEVEL SERIALIZABLE` first: both reads
--     will then return the SAME value even though Session B committed a
--     change in between, because the entire transaction -- not just each
--     statement -- pins its read-consistency snapshot to the transaction's
--     start SCN, reconstructing the row from the undo segment (Section 4.6).
-- ===========================================================================

-- Optional: repeat with explicit SERIALIZABLE isolation to observe the
-- difference described above.
-- Session A:
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
DECLARE
    v_balance NUMBER;
BEGIN
    SELECT balance INTO v_balance FROM oracle_ch_accounts WHERE account_id = 1;
    DBMS_OUTPUT.PUT_LINE('Serializable - first read: ' || v_balance);
    DBMS_LOCK.SLEEP(15); -- Session B commits another +500 during this sleep
    SELECT balance INTO v_balance FROM oracle_ch_accounts WHERE account_id = 1;
    DBMS_OUTPUT.PUT_LINE('Serializable - second read (undo-reconstructed): ' || v_balance);
    COMMIT;
END;
/
