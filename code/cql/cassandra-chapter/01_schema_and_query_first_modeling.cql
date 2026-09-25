-- 01_schema_and_query_first_modeling.cql
--
-- Demonstrates Cassandra's query-first data modeling discipline: instead of
-- one normalized "orders" table joined at read time (impossible in CQL --
-- Cassandra Query Language has no JOIN), each access pattern gets its own
-- denormalized table shaped exactly like the query that will read it.
-- See CH18_Cassandra.md Section 4.6 for the full reasoning.
--
-- Run with: cqlsh -f 01_schema_and_query_first_modeling.cql

-- A keyspace is Cassandra's namespace + replication-strategy unit. In
-- production, always use NetworkTopologyStrategy (even for a single
-- datacenter) so multi-DC expansion never requires a replication-strategy
-- migration later -- SimpleStrategy ignores rack/DC topology entirely and
-- is rack-blind, a common footgun in single-DC-today, multi-DC-tomorrow
-- deployments.
CREATE KEYSPACE IF NOT EXISTS ecommerce
    WITH replication = {
        'class': 'NetworkTopologyStrategy',
        'dc1': 3,
        'dc2': 3
    }
    AND durable_writes = true;

USE ecommerce;

-- Query pattern 1: "Get all orders for a customer, most recent first."
-- Partition key: customer_id (co-locates every order for one customer on
-- the same set of replicas -- the whole point of partition-key selection).
-- Clustering key: order_ts DESC (Cassandra stores clustering columns in
-- sorted order on disk within a partition, so "most recent first" is a
-- free on-disk sort, not a runtime sort).
CREATE TABLE IF NOT EXISTS orders_by_customer (
    customer_id   UUID,
    order_ts      TIMESTAMP,
    order_id      UUID,
    status        TEXT,
    total_cents   BIGINT,
    PRIMARY KEY (customer_id, order_ts, order_id)
) WITH CLUSTERING ORDER BY (order_ts DESC, order_id ASC);

-- Query pattern 2: "Get a single order by its own ID" (e.g. from an order
-- confirmation email deep link, where the customer_id isn't known to the
-- caller). This is a DIFFERENT table holding the SAME logical order data,
-- denormalized for a different access pattern -- not a foreign-key lookup.
-- Writing an order means writing to BOTH tables (see Section 4.6's
-- "denormalize for query pattern, not for storage efficiency" framing);
-- this duplicated write is the accepted cost of read-path speed.
CREATE TABLE IF NOT EXISTS orders_by_id (
    order_id      UUID PRIMARY KEY,
    customer_id   UUID,
    order_ts      TIMESTAMP,
    status        TEXT,
    total_cents   BIGINT
);

-- Query pattern 3: "Get all orders currently in a given status" (an
-- operations/support dashboard query). status is low-cardinality and
-- changes over time, which makes it a poor partition key on its own (it
-- would create a small number of enormous, hot partitions -- one per
-- status value, holding every order ever placed). Bucketing by day keeps
-- partitions bounded in size even as order volume grows.
CREATE TABLE IF NOT EXISTS orders_by_status_bucket (
    status_bucket TEXT,   -- e.g. 'PENDING#2026-09-25' (status + day)
    order_ts      TIMESTAMP,
    order_id      UUID,
    customer_id   UUID,
    PRIMARY KEY (status_bucket, order_ts, order_id)
) WITH CLUSTERING ORDER BY (order_ts DESC);

-- Writing one logical "order placed" event fans out to all three tables.
-- This is the query-first modeling tax paid at write time so every read
-- is a single-partition, no-join, predictable-latency lookup.
BEGIN BATCH
    INSERT INTO orders_by_customer (customer_id, order_ts, order_id, status, total_cents)
        VALUES (11111111-1111-1111-1111-111111111111, toTimestamp(now()), 22222222-2222-2222-2222-222222222222, 'PENDING', 4999);
    INSERT INTO orders_by_id (order_id, customer_id, order_ts, status, total_cents)
        VALUES (22222222-2222-2222-2222-222222222222, 11111111-1111-1111-1111-111111111111, toTimestamp(now()), 'PENDING', 4999);
    INSERT INTO orders_by_status_bucket (status_bucket, order_ts, order_id, customer_id)
        VALUES ('PENDING#2026-09-25', toTimestamp(now()), 22222222-2222-2222-2222-222222222222, 11111111-1111-1111-1111-111111111111);
APPLY BATCH;

-- Each table's own partition key makes reads trivial and fast -- no JOIN
-- exists in CQL, so this single-partition read is the ONLY shape a read
-- can take; there is no equivalent of an ad hoc multi-table SELECT.
SELECT order_id, order_ts, status, total_cents
FROM orders_by_customer
WHERE customer_id = 11111111-1111-1111-1111-111111111111
LIMIT 20;

-- A Cassandra Materialized View auto-maintains a denormalized projection
-- FROM a base table (the server does the fan-out write for you), unlike
-- the manual multi-table BATCH above. This recaps the general Materialized
-- View concept (see CH02_Denormalization.md) -- Cassandra's version has a
-- narrower contract: exactly one extra non-primary-key column may become
-- part of the new primary key, and view writes are best-effort/asynchronous
-- relative to the base table, so a Materialized View can transiently lag
-- (Section 4.6 covers when to prefer a Materialized View versus a manually
-- maintained denormalized table like orders_by_id above).
CREATE MATERIALIZED VIEW IF NOT EXISTS orders_by_order_id_mv AS
    SELECT customer_id, order_ts, order_id, status, total_cents
    FROM orders_by_customer
    WHERE customer_id IS NOT NULL AND order_ts IS NOT NULL AND order_id IS NOT NULL
    PRIMARY KEY (order_id, customer_id, order_ts);

-- TTL (Time To Live): rows auto-expire and become tombstones after the
-- given number of seconds -- useful for session/cache-like data where
-- unbounded growth would otherwise force ever-larger compactions
-- (Section 4.5 covers how tombstones interact with SSTable compaction).
INSERT INTO orders_by_status_bucket (status_bucket, order_ts, order_id, customer_id)
VALUES ('PENDING#2026-09-25', toTimestamp(now()), 33333333-3333-3333-3333-333333333333, 11111111-1111-1111-1111-111111111111)
USING TTL 604800; -- 7 days

-- Secondary index anti-pattern warning (Section 4.6): CREATE INDEX below
-- works but scatters the query across every node in the cluster (it is
-- NOT partition-key-scoped), turning an O(1) single-partition read into an
-- O(N) cluster-wide scatter-gather. Acceptable only for low-cardinality
-- columns queried rarely off the hot path (e.g. ad hoc ops queries), never
-- as a substitute for proper query-first table design on a hot path.
CREATE INDEX IF NOT EXISTS orders_status_idx ON orders_by_id (status);
