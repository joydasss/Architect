-- 01_range_partitioned_table.sql
-- Declarative RANGE partitioning (PostgreSQL 10+) for a time-series "orders"
-- table, partitioned by month on created_at. Demonstrates: parent table
-- definition, monthly child partitions, a DEFAULT catch-all partition, and
-- per-partition local indexes.

-- 1. The partitioned parent table. It holds no rows itself — it is routing
--    metadata plus the shared column definitions and constraints.
CREATE TABLE orders (
    order_id      BIGINT GENERATED ALWAYS AS IDENTITY,
    customer_id   BIGINT NOT NULL,
    status        TEXT NOT NULL,
    total_cents   BIGINT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (order_id, created_at)   -- partition key must be part of any UNIQUE/PK constraint
) PARTITION BY RANGE (created_at);

-- 2. One physical partition per month. Each is a real table under the hood;
--    the FOR VALUES clause is the partition's range constraint.
CREATE TABLE orders_2026_01 PARTITION OF orders
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE orders_2026_02 PARTITION OF orders
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

CREATE TABLE orders_2026_03 PARTITION OF orders
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

-- 3. A DEFAULT partition catches any row whose created_at falls outside every
--    explicit range — a safety net against insert failures if the rolling-
--    window maintenance job (see 01_rolling_window_partition_maintenance.py)
--    ever falls behind schedule. Rows landing here should trigger an alert:
--    it means a future partition is missing, not that the data is invalid.
CREATE TABLE orders_default PARTITION OF orders DEFAULT;

-- 4. Indexes are declared once on the parent and PostgreSQL automatically
--    creates one matching local index per existing/future partition ("local
--    indexes" — see chapter Section 4.9 and Section 5).
CREATE INDEX idx_orders_customer_id ON orders (customer_id);
CREATE INDEX idx_orders_status ON orders (status);

-- 5. A query that filters on the partition key lets the planner prune every
--    partition except orders_2026_02 before execution even begins — see
--    03_partition_pruning_explain.sql for the EXPLAIN output that proves it.
-- SELECT * FROM orders WHERE created_at >= '2026-02-01' AND created_at < '2026-02-15';
