-- 03_jsonb_and_partitioning.sql
-- Models a JSONB column with a jsonb_path_ops GIN index, and a range-
-- partitioned time-series table with automated ATTACH PARTITION, showing
-- partition pruning in EXPLAIN output. See CH11_PostgreSQL.md Sections
-- 4.10-4.11.

-- ===========================================================================
-- PART 1: JSONB storage + jsonb_path_ops GIN index
-- ===========================================================================
DROP TABLE IF EXISTS analytics_events;
CREATE TABLE analytics_events (
    id         BIGSERIAL PRIMARY KEY,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    properties JSONB NOT NULL
);

INSERT INTO analytics_events (properties) VALUES
    ('{"event_type": "page_view", "url": "/home"}'),
    ('{"event_type": "page_view", "url": "/pricing"}'),
    ('{"event_type": "purchase", "amount": 49.99, "currency": "USD"}'),
    ('{"event_type": "purchase", "amount": 12.50, "currency": "EUR"}');

-- Duplicate/reordered keys demonstrate JSONB's write-time normalization:
-- later duplicate keys win, and keys are stored sorted internally.
INSERT INTO analytics_events (properties)
VALUES ('{"event_type": "signup", "event_type": "signup_confirmed", "plan": "pro"}');

SELECT properties FROM analytics_events WHERE properties @> '{"plan": "pro"}';

-- jsonb_path_ops indexes only value-hash paths: smaller and faster than the
-- default GIN operator class, but supports only the containment operator (@>).
CREATE INDEX idx_analytics_events_properties_gin
    ON analytics_events USING GIN (properties jsonb_path_ops);

EXPLAIN ANALYZE
SELECT count(*) FROM analytics_events
WHERE properties @> '{"event_type": "purchase"}';

-- Frequently-filtered scalar attributes deserve an expression index rather
-- than relying purely on the whole-document GIN index for every predicate
-- shape (see CH11_PostgreSQL.md Section 4.10's decision implications).
CREATE INDEX idx_analytics_events_amount
    ON analytics_events (((properties ->> 'amount')::NUMERIC))
    WHERE properties @> '{"event_type": "purchase"}';

EXPLAIN ANALYZE
SELECT (properties ->> 'amount')::NUMERIC AS amount
FROM analytics_events
WHERE properties @> '{"event_type": "purchase"}'
  AND (properties ->> 'amount')::NUMERIC > 20;

-- ===========================================================================
-- PART 2: declarative range partitioning with automated ATTACH PARTITION
-- ===========================================================================
DROP TABLE IF EXISTS metrics CASCADE;
CREATE TABLE metrics (
    id          BIGSERIAL,
    recorded_at TIMESTAMPTZ NOT NULL,
    value       NUMERIC(12, 4) NOT NULL,
    PRIMARY KEY (id, recorded_at)
) PARTITION BY RANGE (recorded_at);

-- Each partition is a real, independently vacuumed physical table (see
-- CH11_PostgreSQL.md Section 4.11's decision implications).
CREATE TABLE metrics_2026_01 PARTITION OF metrics
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE metrics_2026_02 PARTITION OF metrics
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
CREATE TABLE metrics_2026_03 PARTITION OF metrics
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

INSERT INTO metrics (recorded_at, value)
SELECT TIMESTAMPTZ '2026-01-01' + (g || ' minutes')::INTERVAL, random() * 1000
FROM generate_series(1, 500000) g;

-- Row automatically routes to the correct partition based on recorded_at --
-- no INSERT trigger required, unlike the older inheritance-based pattern.
SELECT tableoid::regclass AS routed_partition, count(*)
FROM metrics
GROUP BY tableoid
ORDER BY routed_partition;

-- Partition pruning: EXPLAIN should list only metrics_2026_02, not all
-- three partitions, because the planner can statically compare the
-- predicate against each partition's declared bounds.
EXPLAIN
SELECT count(*) FROM metrics
WHERE recorded_at BETWEEN '2026-02-10' AND '2026-02-15';

-- A function-wrapped predicate the planner cannot statically evaluate
-- against partition bounds defeats pruning -- every partition is scanned.
-- This is the failure mode documented in CH11_PostgreSQL.md Section 4.11.
EXPLAIN
SELECT count(*) FROM metrics
WHERE date_trunc('day', recorded_at) = '2026-02-10';

-- Automated rolling-window maintenance: attach next month, detach and
-- archive the oldest month -- a fast metadata operation, not a row-by-row
-- delete (see the Python companion script for a full scheduled version).
CREATE TABLE metrics_2026_04 PARTITION OF metrics
    FOR VALUES FROM ('2026-04-01') TO ('2026-05-01');

ALTER TABLE metrics DETACH PARTITION metrics_2026_01;
-- metrics_2026_01 is now a standalone table -- archive it to cold storage,
-- then DROP TABLE metrics_2026_01; once the archive is confirmed durable.
