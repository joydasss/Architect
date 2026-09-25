-- Live shard-rebalance migration pattern (CH06_Sharding.md Section 4.6).
-- Moves the key-range [split_point, range_end] from shard_1 (source) to
-- shard_4 (target) with zero-downtime cutover: backfill -> dual-write ->
-- checksum verify -> atomic router flip -> drain-and-delete old copy.
-- Run the numbered steps against the two shard connections shown in the
-- comments; this file documents the sequence, it is not a single-transaction
-- script (a cross-shard migration cannot be one ACID transaction, that is
-- the whole point of Section 4.8's 2PC-cost discussion).

-- =========================================================================
-- STEP 1 (run on shard_1, the source): identify the range being split off.
-- Assumes the shard key is `tenant_hash`, a 32-bit hash of tenant_id already
-- stored on every sharded row (recap: CH05_Partitioning owns *how* a hash
-- partition function is computed; this migration only consumes its output).
-- =========================================================================
-- SELECT MIN(tenant_hash), MAX(tenant_hash) FROM orders
-- WHERE tenant_hash BETWEEN 2147483648 AND 4294967295;

-- =========================================================================
-- STEP 2 (run on shard_4, the target): create the destination table with
-- the identical schema, including indexes, BEFORE backfill starts.
-- =========================================================================
CREATE TABLE IF NOT EXISTS orders (
    order_id     BIGINT PRIMARY KEY,
    tenant_id    BIGINT NOT NULL,
    tenant_hash  BIGINT NOT NULL,
    total_cents  BIGINT NOT NULL,
    status       VARCHAR(32) NOT NULL,
    created_at   TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_orders_tenant_hash ON orders (tenant_hash);

-- =========================================================================
-- STEP 3 (backfill, source -> target, via application-level batch job, not
-- a single cross-database statement): copy the range in bounded batches so
-- the source shard's transaction log / replication lag stays healthy.
-- Pseudocode for the batch loop (executed by an external migration worker):
--
--   last_id = 0
--   loop:
--     rows = SELECT * FROM orders
--            WHERE tenant_hash BETWEEN 2147483648 AND 4294967295
--              AND order_id > last_id
--            ORDER BY order_id LIMIT 5000
--     if rows is empty: break
--     bulk_insert(target_shard, rows)   -- INSERT ... ON CONFLICT DO NOTHING
--     last_id = rows[-1].order_id
--     sleep(backfill_throttle_ms)       -- keep source shard I/O headroom
-- =========================================================================

-- =========================================================================
-- STEP 4: enable dual-write in the application's router for the range being
-- migrated (writes to the moving range go to BOTH shard_1 and shard_4 for
-- the remainder of the migration window; reads still go to shard_1 only).
-- No SQL for this step -- it is a router/application-config change.
-- =========================================================================

-- =========================================================================
-- STEP 5 (run on BOTH shards): checksum verification before cutover. Row
-- counts alone are not sufficient -- compare a content checksum per batch.
-- =========================================================================
SELECT
    COUNT(*)                                   AS row_count,
    SUM(CAST(('x' || SUBSTRING(MD5(CAST(order_id AS TEXT) || total_cents || status), 1, 8)) AS BIT(32))::BIGINT)
                                                AS checksum_sum
FROM orders
WHERE tenant_hash BETWEEN 2147483648 AND 4294967295;
-- Run identically on shard_4; row_count and checksum_sum must match exactly
-- before proceeding, otherwise the migration worker must re-diff and repair.

-- =========================================================================
-- STEP 6: atomic router cutover (metadata-only, see shard-router.js
-- splitRangeForRebalance) -- reads AND writes for the migrated range now go
-- to shard_4 exclusively. This is the single point where in-flight
-- requests can observe a brief routing inconsistency; routers should treat
-- this update as compare-and-swap on a version number to avoid a split-brain
-- window where two router instances disagree about ownership.

-- =========================================================================
-- STEP 7 (run on shard_1, the source, only AFTER a safe drain window with
-- no dual-write errors and no read traffic still hitting the old range):
-- delete the now-migrated rows to reclaim space.
-- =========================================================================
-- DELETE FROM orders
-- WHERE tenant_hash BETWEEN 2147483648 AND 4294967295;
