-- 03_bulk_plsql_batch.sql
-- Demonstrates PL/SQL's round-trip-eliminating BULK COLLECT / FORALL
-- constructs (Chapter Section 4.7), contrasted with an equivalent
-- row-by-row loop, against oracle_ch_accounts.

SET SERVEROUTPUT ON
SET TIMING ON

-- ---------------------------------------------------------------------------
-- Variant 1: row-by-row (slow-by-slow) loop -- one implicit context switch
-- between the SQL engine and the PL/SQL engine per iteration.
-- ---------------------------------------------------------------------------
DECLARE
    CURSOR c_accounts IS
        SELECT account_id FROM oracle_ch_accounts;
BEGIN
    FOR rec IN c_accounts LOOP
        UPDATE oracle_ch_accounts
        SET    balance = balance * 1.01
        WHERE  account_id = rec.account_id;
    END LOOP;
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Row-by-row update complete.');
END;
/

-- ---------------------------------------------------------------------------
-- Variant 2: BULK COLLECT + FORALL -- batches many rows per SQL-engine
-- round trip inside a single PL/SQL call, dramatically reducing the number
-- of PL/SQL-to-SQL engine context switches (Section 4.7's core value
-- proposition, applied inside a single stored procedure).
-- ---------------------------------------------------------------------------
CREATE OR REPLACE PACKAGE oracle_ch_batch_pkg AS
    PROCEDURE apply_interest(p_batch_size IN NUMBER DEFAULT 1000);
END oracle_ch_batch_pkg;
/

CREATE OR REPLACE PACKAGE BODY oracle_ch_batch_pkg AS
    PROCEDURE apply_interest(p_batch_size IN NUMBER DEFAULT 1000) IS
        TYPE t_id_tab IS TABLE OF oracle_ch_accounts.account_id%TYPE;
        v_ids t_id_tab;

        CURSOR c_accounts IS
            SELECT account_id FROM oracle_ch_accounts;
    BEGIN
        OPEN c_accounts;
        LOOP
            FETCH c_accounts BULK COLLECT INTO v_ids LIMIT p_batch_size;
            EXIT WHEN v_ids.COUNT = 0;

            FORALL i IN 1 .. v_ids.COUNT
                UPDATE oracle_ch_accounts
                SET    balance = balance * 1.01
                WHERE  account_id = v_ids(i);

            EXIT WHEN c_accounts%NOTFOUND;
        END LOOP;
        CLOSE c_accounts;
        COMMIT;
        DBMS_OUTPUT.PUT_LINE('BULK COLLECT/FORALL update complete.');
    END apply_interest;
END oracle_ch_batch_pkg;
/

-- One network round trip from the client's perspective, regardless of how
-- many rows oracle_ch_accounts actually holds.
EXEC oracle_ch_batch_pkg.apply_interest(p_batch_size => 500);
