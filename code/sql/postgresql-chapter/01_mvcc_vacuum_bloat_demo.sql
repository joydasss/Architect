-- 01_mvcc_vacuum_bloat_demo.sql
-- Demonstrates PostgreSQL's MVCC heap-tuple versioning (xmin/xmax/ctid),
-- shows heap bloat accumulating under repeated UPDATEs, and shows VACUUM
-- reclaiming dead tuples. Run in a single psql session against a scratch
-- database. Requires the pageinspect extension (bundled with PostgreSQL,
-- just not enabled by default).

-- ---------------------------------------------------------------------------
-- Setup
-- ---------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS pageinspect;

DROP TABLE IF EXISTS mvcc_demo;
CREATE TABLE mvcc_demo (
    id      INT PRIMARY KEY,
    counter INT NOT NULL
);
INSERT INTO mvcc_demo (id, counter) VALUES (1, 0);

-- ---------------------------------------------------------------------------
-- Step 1: inspect the single heap tuple's hidden system columns.
-- xmin = the transaction ID that created this tuple version.
-- xmax = 0 while the tuple is current (not yet superseded/deleted).
-- ctid = (block, offset) physical location of this tuple version.
-- ---------------------------------------------------------------------------
SELECT ctid, xmin, xmax, id, counter FROM mvcc_demo;

-- ---------------------------------------------------------------------------
-- Step 2: run several UPDATEs and inspect the tuple after each one.
-- Each UPDATE does NOT modify the row in place -- it writes a brand-new
-- heap tuple with a new ctid and a new xmin, and sets xmax on the OLD
-- tuple to mark it superseded (not immediately removed).
-- ---------------------------------------------------------------------------
UPDATE mvcc_demo SET counter = counter + 1 WHERE id = 1;
SELECT ctid, xmin, xmax, id, counter FROM mvcc_demo;  -- new ctid, new xmin

UPDATE mvcc_demo SET counter = counter + 1 WHERE id = 1;
SELECT ctid, xmin, xmax, id, counter FROM mvcc_demo;  -- ctid moved again

-- ---------------------------------------------------------------------------
-- Step 3: simulate a hot-update workload and observe heap growth.
-- 20,000 UPDATEs against a single logical row produce up to 20,000 dead
-- heap tuples before autovacuum (or an explicit VACUUM) reclaims them --
-- this is the mechanical cause of "bloat proportional to update rate, not
-- row count" described in Section 4.1/4.2 of CH11_PostgreSQL.md.
-- ---------------------------------------------------------------------------
DO $$
BEGIN
    FOR i IN 1..20000 LOOP
        UPDATE mvcc_demo SET counter = counter + 1 WHERE id = 1;
    END LOOP;
END $$;

-- Table size before VACUUM: inflated by ~20,000 dead tuple versions.
SELECT pg_size_pretty(pg_relation_size('mvcc_demo')) AS size_before_vacuum;

SELECT relname, n_dead_tup, n_live_tup, last_autovacuum, last_vacuum
FROM pg_stat_user_tables
WHERE relname = 'mvcc_demo';

-- ---------------------------------------------------------------------------
-- Step 4: VACUUM reclaims dead tuple slots for reuse (does NOT necessarily
-- shrink the file on disk -- see CH11_PostgreSQL.md Section 4.2 for the
-- distinction between plain VACUUM and VACUUM FULL).
-- ---------------------------------------------------------------------------
VACUUM (VERBOSE, ANALYZE) mvcc_demo;

SELECT pg_size_pretty(pg_relation_size('mvcc_demo')) AS size_after_vacuum;

SELECT relname, n_dead_tup, n_live_tup, last_vacuum
FROM pg_stat_user_tables
WHERE relname = 'mvcc_demo';

-- ---------------------------------------------------------------------------
-- Step 5 (optional, disruptive): VACUUM FULL actually rewrites the table
-- into a compact new file, physically shrinking disk usage, but takes an
-- ACCESS EXCLUSIVE lock for the duration -- do not run this against a live
-- production table without a maintenance window.
-- ---------------------------------------------------------------------------
-- VACUUM FULL mvcc_demo;
-- SELECT pg_size_pretty(pg_relation_size('mvcc_demo')) AS size_after_full;
