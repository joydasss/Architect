-- CH22 Time Series Databases — Example 1: TimescaleDB as a PostgreSQL extension
-- Demonstrates: hypertable creation (time-partitioned chunks), a continuous
-- aggregate (downsampling/rollup), and a retention policy (data lifecycle).
-- TimescaleDB extends PostgreSQL (see CH11_PostgreSQL.md) rather than
-- replacing it, so every statement below is still ordinary SQL executed
-- against a regular Postgres connection.

-- 1. Enable the extension once per database.
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 2. Create the source table exactly like any other Postgres table: no
-- special syntax at the table-definition level. Tags are modeled as plain
-- columns here (a fixed, low-cardinality tag set); a JSONB column is the
-- alternative for a more open-ended tag set, at some query-planning cost.
CREATE TABLE IF NOT EXISTS cpu_metrics (
    "time"       TIMESTAMPTZ         NOT NULL,
    host         TEXT                NOT NULL,
    region       TEXT                NOT NULL,
    usage_pct    DOUBLE PRECISION    NOT NULL,
    load_1m      DOUBLE PRECISION
);

-- 3. Convert the table into a hypertable: this is the one TimescaleDB-
-- specific call in the whole example. Internally it partitions the table
-- into a chain of child tables ("chunks") by time range (default 7 days per
-- chunk here), each with its own indexes and, once closed, its own
-- immutable on-disk footprint (Section 4.2 of the chapter explains why this
-- append-mostly, time-ordered chunk layout is faster to write than a
-- general-purpose OLTP B-tree table).
SELECT create_hypertable(
    'cpu_metrics',
    by_range('time', INTERVAL '7 days'),
    if_not_exists => TRUE
);

-- 4. A composite index that puts the tag columns first lets the planner
-- prune both by chunk (time) and by tag equality within a chunk — this is
-- the SQL-side analogue of the chapter's high-cardinality discussion
-- (Section 4.4): an index built on host+region only stays cheap as long as
-- the number of distinct (host, region) pairs stays bounded.
CREATE INDEX IF NOT EXISTS ix_cpu_metrics_host_region_time
    ON cpu_metrics (host, region, "time" DESC);

-- 5. Insert some representative rows (in production this is a
-- high-frequency batched INSERT from a collector, not hand-typed values).
INSERT INTO cpu_metrics ("time", host, region, usage_pct, load_1m) VALUES
    (now() - INTERVAL '2 hours', 'web-01', 'us-east-1', 42.5, 1.2),
    (now() - INTERVAL '2 hours', 'web-02', 'us-east-1', 55.1, 1.8),
    (now() - INTERVAL '1 hour',  'web-01', 'us-east-1', 61.3, 2.1),
    (now() - INTERVAL '1 hour',  'web-02', 'us-east-1', 48.9, 1.5),
    (now(),                       'web-01', 'us-east-1', 39.0, 0.9);

-- 6. A continuous aggregate is TimescaleDB's rollup mechanism (chapter
-- Section 4.3): it is defined once as a materialized view over a bucketed
-- time_bucket() expression, and TimescaleDB incrementally refreshes only
-- the buckets whose underlying raw data changed, instead of recomputing
-- the whole aggregate on every refresh. This is the downsampled,
-- pre-aggregated series a dashboard queries for a 30-day view instead of
-- scanning millions of raw 10-second-resolution rows.
CREATE MATERIALIZED VIEW IF NOT EXISTS cpu_metrics_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', "time") AS bucket,
    host,
    region,
    AVG(usage_pct) AS avg_usage_pct,
    MAX(usage_pct) AS max_usage_pct,
    MIN(usage_pct) AS min_usage_pct,
    COUNT(*)        AS sample_count
FROM cpu_metrics
GROUP BY bucket, host, region
WITH NO DATA;

-- 7. A refresh policy keeps the continuous aggregate up to date on a
-- schedule without a manual REFRESH MATERIALIZED VIEW call; the
-- start_offset/end_offset window controls how much of the recent, still-
-- possibly-late-arriving raw data is deliberately excluded from each
-- refresh pass, trading a small amount of rollup staleness for avoiding
-- rewriting the same recent bucket on every late-arriving row.
SELECT add_continuous_aggregate_policy('cpu_metrics_hourly',
    start_offset      => INTERVAL '3 hours',
    end_offset        => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
);

-- 8. A retention policy is the data-lifecycle half of Section 4.3: once raw
-- rows age past 30 days, TimescaleDB drops the whole chunk (a metadata-only
-- operation, the same mechanism the chapter's Partitioning sibling chapter
-- (CH05_Partitioning.md, Section 4.8) already uses for rolling-window
-- maintenance) rather than issuing a row-by-row DELETE.
SELECT add_retention_policy('cpu_metrics', INTERVAL '30 days');

-- 9. Optional: compress chunks older than 7 days. TimescaleDB's native
-- columnar compression is a different, coarser-grained technique than the
-- chapter's delta-of-delta/XOR bit-level encodings (Sections 4.5-4.6), but
-- it exists for the identical reason: time-series columns are highly
-- repetitive/monotonic and compress far better than a general-purpose
-- row-oriented OLTP table's columns do.
ALTER TABLE cpu_metrics SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'host, region',
    timescaledb.compress_orderby   = '"time" DESC'
);

SELECT add_compression_policy('cpu_metrics', INTERVAL '7 days');

-- 10. A query against the rollup instead of the raw table: this is the
-- point of Section 4.3 — a 30-day dashboard panel scans hourly buckets
-- (hundreds of rows per host) instead of raw 10-second samples (hundreds
-- of thousands of rows per host).
-- SELECT bucket, host, avg_usage_pct
-- FROM cpu_metrics_hourly
-- WHERE host = 'web-01' AND bucket > now() - INTERVAL '30 days'
-- ORDER BY bucket;
