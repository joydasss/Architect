-- Referenced from 06_Databases_and_Storage/CH03_Indexes.md (Section 10).
-- Demonstrates the EXPLAIN-plan difference between a sequential scan and an
-- index scan on PostgreSQL, for the same predicate, before/after adding an index.

CREATE TABLE orders (
    order_id     BIGSERIAL PRIMARY KEY,
    customer_id  BIGINT NOT NULL,
    order_date   DATE NOT NULL,
    status       TEXT NOT NULL,
    total_cents  INTEGER NOT NULL
);

-- Populate with enough rows that the planner's cost model prefers a
-- sequential scan when there is no index (small tables are almost always
-- scanned sequentially regardless of indexes present).
INSERT INTO orders (customer_id, order_date, status, total_cents)
SELECT
    (random() * 500000)::BIGINT,                       -- customer_id: high cardinality
    DATE '2020-01-01' + (random() * 2000)::INT,         -- order_date
    (ARRAY['PENDING','PAID','SHIPPED','CANCELLED'])[1 + floor(random() * 4)::INT],
    (random() * 20000)::INT
FROM generate_series(1, 5000000);

ANALYZE orders;

-- BEFORE: no index on customer_id. Expect "Seq Scan on orders" in the plan,
-- with cost proportional to the full table's page count.
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id, order_date, total_cents
FROM orders
WHERE customer_id = 123456;

-- Add a B-tree index on the equality predicate's column.
CREATE INDEX idx_orders_customer_id ON orders (customer_id);
ANALYZE orders;

-- AFTER: expect "Index Scan using idx_orders_customer_id" (or a Bitmap Index
-- Scan if the planner estimates enough matching rows to make a bitmap
-- heap scan cheaper). customer_id is high-selectivity (500,000 distinct
-- values across 5,000,000 rows -> ~10 rows per value), so the planner should
-- switch plans even though nothing else about the query changed.
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id, order_date, total_cents
FROM orders
WHERE customer_id = 123456;

-- Contrast: status has only 4 distinct values across 5,000,000 rows
-- (selectivity ~= 0.25 -- roughly 1.25M rows per value). Even with an index
-- present, the planner will usually still choose a sequential scan here,
-- because reading ~25% of the table via random index lookups costs more
-- than one sequential pass. This is the low-selectivity failure mode from
-- Section 4.7 -- an index existing does not guarantee it will be used.
CREATE INDEX idx_orders_status ON orders (status);
ANALYZE orders;

EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id
FROM orders
WHERE status = 'PENDING';
