-- ============================================================================
-- Before/after: stale statistics degrading a query plan, and the fix.
-- Companion to 06_Databases_and_Storage/CH04_Query_Optimizers.md, Section 10.
--
-- Scenario: a nightly batch job inserts 2,000,000 new rows into `events`
-- (previously ~100,000 rows) inside a single transaction, then the
-- application immediately re-runs a dashboard query. Autovacuum/auto-analyze
-- has not yet run (large bulk loads commonly land outside its trigger
-- window), so the planner's statistics still describe the OLD, much smaller
-- table.
-- ============================================================================

-- --- Step 0: baseline state before the load ---------------------------------
-- events currently has ~100,000 rows; event_type = 'checkout_failed' is rare
-- (a few hundred rows), so the planner's stale-but-still-accurate statistics
-- correctly favor an index scan.

EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM events
WHERE event_type = 'checkout_failed'
  AND created_at >= NOW() - INTERVAL '1 day';

-- Index Scan using events_type_created_idx on events
--   (cost=0.42..120.55 rows=340 width=96) (actual time=0.031..0.812 rows=352 loops=1)
--   Index Cond: ((event_type = 'checkout_failed'::text)
--                AND (created_at >= (now() - '1 day'::interval)))
-- Planning Time: 0.201 ms
-- Execution Time: 0.887 ms

-- --- Step 1: the bulk load happens, no ANALYZE afterward --------------------
-- (Illustrative only -- run inside the batch job's transaction.)
-- INSERT INTO events (event_type, created_at, payload)
-- SELECT 'checkout_failed', NOW(), '{}'::jsonb
-- FROM generate_series(1, 2000000);

-- --- Step 2: same query, run immediately after the load ---------------------
-- pg_stat_user_tables.n_mod_since_analyze is now huge but ANALYZE hasn't run;
-- reltuples/pg_stats still reflect the pre-load ~100,000-row table, so the
-- planner still believes 'checkout_failed' is rare when it is now common.

EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM events
WHERE event_type = 'checkout_failed'
  AND created_at >= NOW() - INTERVAL '1 day';

-- Index Scan using events_type_created_idx on events
--   (cost=0.42..120.55 rows=340 width=96)
--   (actual time=0.045..38210.902 rows=2000180 loops=1)
--   Index Cond: ((event_type = 'checkout_failed'::text)
--                AND (created_at >= (now() - '1 day'::interval)))
-- Planning Time: 0.198 ms
-- Execution Time: 38214.117 ms      <-- ~43,000x slower, same SQL text
--
-- Diagnosis: estimated rows=340 vs actual rows=2,000,180 -- a six-order-of-
-- magnitude cardinality miss. The plan SHAPE never changed (still an index
-- scan), but an index scan that has to fetch two million heap tuples one
-- random I/O at a time is far worse than a sequential scan would have been
-- at this selectivity. This is exactly the "same query, wildly different
-- performance, after a data/statistics change and NO code change" scenario
-- this chapter exists to explain.

-- --- Step 3: the fix ---------------------------------------------------------
ANALYZE events;

EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM events
WHERE event_type = 'checkout_failed'
  AND created_at >= NOW() - INTERVAL '1 day';

-- Seq Scan on events
--   (cost=0.00..45210.00 rows=1998500 width=96)
--   (actual time=0.021..612.334 rows=2000180 loops=1)
--   Filter: ((event_type = 'checkout_failed'::text)
--            AND (created_at >= (now() - '1 day'::interval)))
--   Rows Removed by Filter: 41320
-- Planning Time: 0.312 ms
-- Execution Time: 645.902 ms      <-- ~59x faster than the stale-stats plan
--
-- With fresh statistics the planner correctly estimates ~2,000,000 matching
-- rows out of ~2,041,500 total, recognizes an index scan would touch almost
-- every heap page anyway (with random I/O on top), and switches to a
-- sequential scan -- still not fast in absolute terms (a data-model problem:
-- 'checkout_failed' should not realistically be ~98% of a table), but
-- dramatically better than the mis-costed index scan, and a signal that this
-- event stream now needs partitioning or a differently-shaped index rather
-- than accepting either scan strategy as "done."

-- --- Step 4: closing the gap for next time ----------------------------------
-- Options, cheapest first:
--   1. Lower the table's autovacuum_analyze_scale_factor so auto-analyze
--      triggers sooner relative to table size for high-churn tables.
--   2. Run ANALYZE explicitly as the last step of the batch load job itself,
--      rather than relying on autovacuum's schedule.
--   3. For extreme, predictable skew like this one, consider a partial index
--      or partitioning by event_type/created_at so 'checkout_failed' isn't
--      forced to share one histogram with every other event type.
ALTER TABLE events SET (autovacuum_analyze_scale_factor = 0.02);
