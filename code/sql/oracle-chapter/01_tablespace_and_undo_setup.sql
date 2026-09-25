-- 01_tablespace_and_undo_setup.sql
-- Creates a dedicated data tablespace and an intentionally small undo
-- tablespace, then inspects the resulting physical layout via data
-- dictionary / dynamic performance views. Run as a DBA-privileged user
-- (e.g. SYS or a user granted CREATE TABLESPACE).
--
-- Ties to Chapter Sections 4.5 (Tablespaces and Datafiles) and 4.6 (Undo
-- Segments and Read Consistency).

-- ---------------------------------------------------------------------------
-- 1. Create a dedicated, locally managed data tablespace
-- ---------------------------------------------------------------------------
CREATE TABLESPACE oracle_ch_data
    DATAFILE '/u01/app/oracle/oradata/ORCL/oracle_ch_data01.dbf'
    SIZE 200M
    AUTOEXTEND ON NEXT 50M MAXSIZE 2G
    EXTENT MANAGEMENT LOCAL
    SEGMENT SPACE MANAGEMENT AUTO;

-- ---------------------------------------------------------------------------
-- 2. Create a deliberately small, short-retention undo tablespace
--    (do NOT do this in production -- this is for the ORA-01555
--    reproduction in 02_read_consistency_demo.sql / Exercise 24.1)
-- ---------------------------------------------------------------------------
CREATE UNDO TABLESPACE oracle_ch_undo_small
    DATAFILE '/u01/app/oracle/oradata/ORCL/oracle_ch_undo01.dbf'
    SIZE 50M
    AUTOEXTEND OFF
    RETENTION GUARANTEE;

-- Switch the instance to use the small undo tablespace and force a short
-- retention window (in real production, UNDO_RETENTION is sized to cover
-- the longest-running concurrent query, not shortened like this).
ALTER SYSTEM SET UNDO_TABLESPACE = oracle_ch_undo_small SCOPE = BOTH;
ALTER SYSTEM SET UNDO_RETENTION = 60 SCOPE = BOTH; -- seconds

-- ---------------------------------------------------------------------------
-- 3. Sample table + index placed explicitly in the new data tablespace
-- ---------------------------------------------------------------------------
CREATE TABLE oracle_ch_accounts (
    account_id   NUMBER PRIMARY KEY,
    owner_name   VARCHAR2(100) NOT NULL,
    balance      NUMBER(12, 2) NOT NULL,
    updated_at   TIMESTAMP DEFAULT SYSTIMESTAMP
) TABLESPACE oracle_ch_data;

CREATE INDEX oracle_ch_accounts_owner_ix
    ON oracle_ch_accounts (owner_name)
    TABLESPACE oracle_ch_data;

INSERT INTO oracle_ch_accounts (account_id, owner_name, balance)
SELECT level, 'owner_' || level, 1000 + level
FROM dual CONNECT BY level <= 10000;
COMMIT;

-- ---------------------------------------------------------------------------
-- 4. Inspect the resulting layout: tablespace -> datafile -> segment
-- ---------------------------------------------------------------------------
SELECT tablespace_name, file_name, bytes / 1024 / 1024 AS size_mb, autoextensible
FROM   dba_data_files
WHERE  tablespace_name IN ('ORACLE_CH_DATA', 'ORACLE_CH_UNDO_SMALL');

SELECT segment_name, segment_type, tablespace_name, bytes / 1024 / 1024 AS size_mb
FROM   dba_segments
WHERE  tablespace_name = 'ORACLE_CH_DATA';

-- Live undo consumption / retention pressure (Section 4.6)
SELECT begin_time, end_time, undoblks, maxquerylen, ssolderrcnt
FROM   v$undostat
ORDER  BY begin_time DESC
FETCH FIRST 5 ROWS ONLY;
