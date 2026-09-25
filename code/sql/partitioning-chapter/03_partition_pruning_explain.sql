-- 03_partition_pruning_explain.sql
-- Annotated EXPLAIN output demonstrating partition pruning: the planner
-- eliminating whole partitions from the plan BEFORE execution, based on the
-- query's WHERE clause and each partition's range constraint. Run against
-- the "orders" table from 01_range_partitioned_table.sql.

-- ---------------------------------------------------------------------
-- Case 1: sargable predicate directly on the partition key -> full pruning.
-- ---------------------------------------------------------------------
EXPLAIN (COSTS OFF)
SELECT order_id, total_cents
FROM orders
WHERE created_at >= '2026-02-01' AND created_at < '2026-03-01';

-- Expected shape of the plan (annotated):
--   Append
--     ->  Seq Scan on orders_2026_02          -- only this ONE partition appears
--           Filter: created_at range predicate
--
-- Partitions orders_2026_01, orders_2026_03, orders_default never appear in
-- the plan at all — they were eliminated at planning time by comparing the
-- query's constant range literals against each partition's stored range
-- constraint (declarative partition pruning). This is what Section 4.7 means
-- by "pruning happens before the optimizer's cost-based search even runs" —
-- it shrinks the candidate table set first, then Query Optimizers'
-- (../CH04_Query_Optimizers.md) access-path and join-order search operates
-- only on what survives.

-- ---------------------------------------------------------------------
-- Case 2: predicate wraps the partition-key column in a function -> pruning
-- defeated. This is the most common real-world partitioning mistake
-- (Section 4.7's common failure mode and Section 17).
-- ---------------------------------------------------------------------
EXPLAIN (COSTS OFF)
SELECT order_id, total_cents
FROM orders
WHERE date_trunc('month', created_at) = '2026-02-01';

-- Expected shape of the plan (annotated):
--   Append
--     ->  Seq Scan on orders_2026_01   -- ALL partitions still appear
--     ->  Seq Scan on orders_2026_02
--     ->  Seq Scan on orders_2026_03
--     ->  Seq Scan on orders_default
--
-- The planner cannot prove which partitions date_trunc('month', created_at)
-- could possibly match without evaluating the function per row, so it must
-- scan every partition — identical cost to an unpartitioned table for this
-- query shape. Rewriting as an equivalent sargable range predicate
-- (created_at >= '2026-02-01' AND created_at < '2026-03-01', as in Case 1)
-- restores pruning with no change in the result set.

-- ---------------------------------------------------------------------
-- Case 3: no predicate on the partition key at all -> the query is correct
-- (all data is still visible through the parent), but every partition must
-- be scanned. Partitioning never changes correctness, only which partitions
-- must be touched to answer a given query.
-- ---------------------------------------------------------------------
EXPLAIN (COSTS OFF)
SELECT status, count(*) FROM orders GROUP BY status;
