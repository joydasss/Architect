-- ============================================================================
-- EXPLAIN / EXPLAIN ANALYZE walkthrough (PostgreSQL dialect)
-- Companion to 06_Databases_and_Storage/CH04_Query_Optimizers.md, Section 10.
--
-- Goal: read a real execution plan bottom-up / inside-out and map every
-- number back to the cost-based optimization concepts taught in Section 4.
-- ============================================================================

-- Schema used throughout this example (assume already populated):
--   orders(order_id PK, customer_id FK, status TEXT, total_cents INT, created_at TIMESTAMPTZ)
--   customers(customer_id PK, region TEXT, signup_at TIMESTAMPTZ)
--   1,000,000 rows in orders, 50,000 rows in customers.

-- Refresh planner statistics before capturing the plan so the numbers below
-- reflect a "healthy statistics" baseline (see 02_stale_statistics_fix.sql
-- for what happens when this step is skipped after a bulk load).
ANALYZE orders;
ANALYZE customers;

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT c.region, COUNT(*) AS order_count, SUM(o.total_cents) AS revenue_cents
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.status = 'completed'
  AND o.created_at >= NOW() - INTERVAL '30 days'
GROUP BY c.region
ORDER BY revenue_cents DESC;

-- ----------------------------------------------------------------------------
-- Representative output (annotated). Read bottom-up: each node's children are
-- executed first and their rows are pipelined upward as input.
-- ----------------------------------------------------------------------------
--
-- Sort  (cost=18420.55..18420.80 rows=100 width=48) (actual time=42.311..42.313 rows=6 loops=1)
--   Sort Key: revenue_cents DESC
--   Sort Method: quicksort  Memory: 25kB
--   ->  HashAggregate  (cost=18416.00..18417.00 rows=100 width=48) (actual time=42.260..42.264 rows=6 loops=1)
--         Group Key: c.region
--         Batches: 1  Memory Usage: 40kB
--         ->  Hash Join  (cost=1633.00..17891.00 rows=42000 width=16)
--                        (actual time=8.402..38.905 rows=41870 loops=1)
--               Hash Cond: (o.customer_id = c.customer_id)
--               ->  Seq Scan on orders o  (cost=0.00..16000.00 rows=42000 width=12)
--                                          (actual time=0.020..25.114 rows=41870 loops=1)
--                     Filter: ((status = 'completed'::text)
--                              AND (created_at >= (now() - '30 days'::interval)))
--                     Rows Removed by Filter: 958130
--               ->  Hash  (cost=883.00..883.00 rows=50000 width=12)
--                          (actual time=8.331..8.332 rows=50000 loops=1)
--                     Buckets: 65536  Batches: 1  Memory Usage: 2969kB
--                     ->  Seq Scan on customers c
--                                (cost=0.00..883.00 rows=50000 width=12)
--                                (actual time=0.008..3.912 rows=50000 loops=1)
-- Planning Time: 0.412 ms
-- Execution Time: 42.401 ms
--
-- ----------------------------------------------------------------------------
-- WHAT EACH FIELD MEANS (Section 4.9's mental model applied to real output)
-- ----------------------------------------------------------------------------
-- cost=A..B     : A = estimated cost to return the FIRST row, B = estimated
--                 cost to return ALL rows. Cost is an abstract unit (roughly
--                 "sequential page fetches"), not milliseconds -- it exists
--                 purely to let the optimizer COMPARE candidate plans.
-- rows=N        : the optimizer's *cardinality estimate* for how many rows
--                 this node will produce -- derived from table/column
--                 statistics and histograms (Section 4.3). This is the number
--                 most likely to be wrong when statistics are stale.
-- actual time=X..Y rows=Z loops=L : only present with ANALYZE -- the plan was
--                 actually EXECUTED, and these are real measured numbers.
--                 Compare estimated rows=N against actual rows=Z: a large gap
--                 (here: none, this is the healthy-statistics baseline) is
--                 the single most useful cardinality-estimation-error signal
--                 in the whole plan.
--
-- WHY THIS SHAPE WAS CHOSEN (tying back to Section 4 join algorithms):
--   - Seq Scan on orders: no usable index for this predicate combination
--     existed at planning time (or a full scan was cheaper than an index
--     scan because ~4% of rows qualify -- see CH03_Indexes.md for the
--     selectivity threshold where the optimizer flips from index scan to
--     sequential scan).
--   - Hash Join was chosen over nested loop or merge join because neither
--     input arrives pre-sorted on customer_id, and the smaller side
--     (customers, 50,000 rows) fits comfortably in work_mem as an in-memory
--     hash table -- exactly the condition under which hash join dominates
--     (Section 4.7).
--   - HashAggregate groups by region without needing a prior sort, because
--     region has too few distinct values to justify a sort-based GROUP BY.

-- ----------------------------------------------------------------------------
-- A worse plan shape to recognize: nested loop misuse. If the optimizer's
-- cardinality estimate for `orders` were wrong (estimated rows=42000 but
-- actual rows=800000), it might instead choose:
--
--   Nested Loop  (cost=0.42..812345.00 rows=42000 width=16)
--                (actual time=0.045..9812.331 rows=800000 loops=1)
--     ->  Seq Scan on orders o ...
--     ->  Index Scan using customers_pkey on customers c
--                (cost=0.42..8.44 rows=1 width=12)
--                (actual time=0.002..0.004 rows=1 loops=800000)
--
-- Notice "loops=800000": nested loop re-probes the inner side once per outer
-- row. At an estimated 42,000 outer rows this looked cheap; at an actual
-- 800,000 outer rows it is catastrophically slow -- this is the canonical
-- "cardinality misestimation picks the wrong join algorithm" failure mode
-- covered in Section 4.3 and Section 15.
