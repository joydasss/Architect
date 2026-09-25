-- 04_explain_plan_and_hints.sql
-- Gathers statistics, runs EXPLAIN PLAN / DBMS_XPLAN.DISPLAY, and
-- demonstrates a targeted optimizer hint changing the chosen access path
-- (Chapter Section 4.8: Oracle's Cost-Based Optimizer specifics).

SET SERVEROUTPUT ON

-- ---------------------------------------------------------------------------
-- 1. Gather fresh, representative statistics (the first, almost-always-
--    correct response to "the optimizer chose a bad plan" -- see Section
--    4.8's Decision implications, before ever reaching for a hint).
-- ---------------------------------------------------------------------------
EXEC DBMS_STATS.GATHER_TABLE_STATS(ownname => USER, tabname => 'ORACLE_CH_ACCOUNTS', cascade => TRUE);

-- ---------------------------------------------------------------------------
-- 2. Baseline plan: let the optimizer choose freely
-- ---------------------------------------------------------------------------
EXPLAIN PLAN FOR
SELECT account_id, owner_name, balance
FROM   oracle_ch_accounts
WHERE  owner_name = 'owner_42';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY(format => 'BASIC +PREDICATE +COST +ROWS'));

-- ---------------------------------------------------------------------------
-- 3. Force a full table scan via a hint, to show the optimizer's default
--    choice (an index range scan on oracle_ch_accounts_owner_ix, created in
--    01_tablespace_and_undo_setup.sql) being deliberately overridden --
--    this is the kind of targeted, last-resort override Section 4.8
--    describes, not a first-line tuning tool.
-- ---------------------------------------------------------------------------
EXPLAIN PLAN FOR
SELECT /*+ FULL(a) */ account_id, owner_name, balance
FROM   oracle_ch_accounts a
WHERE  owner_name = 'owner_42';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY(format => 'BASIC +PREDICATE +COST +ROWS'));

-- ---------------------------------------------------------------------------
-- 4. Inspect the actual (not just estimated) plan of a statement that has
--    already executed, including real row counts -- the evidence used to
--    detect an estimate-vs-actual mismatch caused by stale statistics
--    (Section 4.8's bind-variable-peeking failure mode).
-- ---------------------------------------------------------------------------
SELECT account_id FROM oracle_ch_accounts WHERE owner_name = 'owner_99';

SELECT * FROM TABLE(
    DBMS_XPLAN.DISPLAY_CURSOR(sql_id => NULL, cursor_child_no => NULL, format => 'ALLSTATS LAST')
);
