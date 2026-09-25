-- InnoDB Buffer Pool sizing and runtime diagnostics: the single highest-
-- leverage InnoDB tuning knob, plus the queries that tell you whether it
-- is actually sized correctly for the working set.

-- ============================================================
-- Sizing: my.cnf (requires a restart unless innodb_buffer_pool_instances
-- and chunk size allow the newer online-resize path in MySQL 8)
-- ============================================================
-- [mysqld]
-- innodb_buffer_pool_size       = 12G     -- rule of thumb: ~60-75% of RAM on a dedicated DB host
-- innodb_buffer_pool_instances  = 8       -- shard the pool to reduce mutex contention on large pools
-- innodb_buffer_pool_chunk_size = 128M    -- pool_size must be a multiple of instances * chunk_size
-- innodb_page_size              = 16K     -- default; matches the pool's internal page-frame accounting

-- Online resize without a restart (MySQL 5.7.5+), useful for right-sizing
-- gradually under production load instead of guessing at start-up time:
SET GLOBAL innodb_buffer_pool_size = 12884901888;  -- bytes; rounds to nearest chunk multiple
SELECT * FROM performance_schema.global_status
WHERE variable_name = 'Innodb_buffer_pool_resize_status';

-- ============================================================
-- Diagnostic 1 -- Buffer Pool hit ratio: the primary health signal.
-- A healthy OLTP workload should sit well above 99%; anything trending
-- down toward 95% or lower means the working set no longer fits in
-- memory and InnoDB is falling back to physical disk reads on the
-- buffer-miss path (see chapter Section 4.11's read/eviction pipeline).
-- ============================================================
SELECT
    (1 - (Innodb_buffer_pool_reads / Innodb_buffer_pool_read_requests)) * 100
        AS buffer_pool_hit_ratio_pct
FROM (
    SELECT
        (SELECT variable_value FROM performance_schema.global_status
         WHERE variable_name = 'Innodb_buffer_pool_reads') AS Innodb_buffer_pool_reads,
        (SELECT variable_value FROM performance_schema.global_status
         WHERE variable_name = 'Innodb_buffer_pool_read_requests') AS Innodb_buffer_pool_read_requests
) AS stats;

-- ============================================================
-- Diagnostic 2 -- free vs. dirty vs. total pages, and LRU-eviction
-- pressure. A near-zero Free_buffers with high Pages_flushed_LRU/second
-- means the pool is under eviction pressure -- growing the pool (or
-- shrinking the working set via better indexing/archiving) will help
-- more than any query-level tuning.
-- ============================================================
SELECT
    POOL_ID,
    POOL_SIZE,
    FREE_BUFFERS,
    DATABASE_PAGES,
    OLD_DATABASE_PAGES,        -- pages in the "old" sublist of the midpoint-insertion LRU
    MODIFIED_DATABASE_PAGES,   -- dirty pages awaiting flush to disk
    PENDING_DECOMPRESS,
    PENDING_READS,
    PENDING_FLUSH_LRU,
    PENDING_FLUSH_LIST
FROM information_schema.INNODB_BUFFER_POOL_STATS;

-- ============================================================
-- Diagnostic 3 -- what's actually resident in the pool right now, by
-- table: identifies whether one runaway table/index is monopolizing the
-- cache and evicting everything else's working set.
-- ============================================================
SELECT
    TABLE_NAME,
    INDEX_NAME,
    COUNT(*)                          AS pages_cached,
    ROUND(SUM(DATA_SIZE) / 1024 / 1024, 1) AS mb_cached,
    SUM(NUMBER_RECORDS)                AS rows_represented
FROM information_schema.INNODB_BUFFER_PAGE
WHERE TABLE_NAME IS NOT NULL
GROUP BY TABLE_NAME, INDEX_NAME
ORDER BY pages_cached DESC
LIMIT 20;

-- ============================================================
-- Diagnostic 4 -- warm the pool proactively after a restart (MySQL 8
-- dumps/reloads the "hottest" page list automatically by default via
-- innodb_buffer_pool_dump_at_shutdown / innodb_buffer_pool_load_at_startup,
-- but this manual pair is useful for a planned failover or migration):
SET GLOBAL innodb_buffer_pool_dump_now = ON;
-- ... after restarting/promoting the target instance ...
SET GLOBAL innodb_buffer_pool_load_now = ON;
SELECT variable_value FROM performance_schema.global_status
WHERE variable_name = 'Innodb_buffer_pool_load_status';
