-- 02_indexing_gin_gist_brin_partial.sql
-- Builds a GIN trigram index (pg_trgm), a GiST spatial index (PostGIS), a
-- BRIN index on a time-ordered column, and a partial index, comparing
-- EXPLAIN ANALYZE output before and after each index exists. See
-- CH11_PostgreSQL.md Sections 4.6-4.9 and 4.14 for the mechanisms behind
-- each result below.

CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS postgis;

-- ===========================================================================
-- PART 1: GIN + pg_trgm for fuzzy text search
-- ===========================================================================
DROP TABLE IF EXISTS products;
CREATE TABLE products (
    id   SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);
INSERT INTO products (name)
SELECT 'Product ' || generate_series(1, 500000);
INSERT INTO products (name) VALUES ('Wireless Bluetooth Headphones');

-- Before the index: a similarity search forces a sequential scan across
-- every row's computed trigram similarity.
EXPLAIN ANALYZE
SELECT name FROM products WHERE name % 'Bluetooth Headphones';

CREATE INDEX idx_products_name_trgm ON products USING GIN (name gin_trgm_ops);

-- After the index: the planner can use the GIN posting-list structure to
-- find candidate rows by trigram overlap instead of scanning every row.
EXPLAIN ANALYZE
SELECT name FROM products WHERE name % 'Bluetooth Headphones';

-- ===========================================================================
-- PART 2: GiST + PostGIS for spatial containment/nearest-neighbor queries
-- ===========================================================================
DROP TABLE IF EXISTS warehouses;
CREATE TABLE warehouses (
    id       SERIAL PRIMARY KEY,
    name     TEXT NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL
);
INSERT INTO warehouses (name, location)
SELECT 'Warehouse ' || g,
       ST_MakePoint(-122.4 + (random() - 0.5) * 2, 37.8 + (random() - 0.5) * 2)::geography
FROM generate_series(1, 50000) g;

-- Before the index: distance filtering forces every row's distance to be
-- computed against the target point.
EXPLAIN ANALYZE
SELECT name FROM warehouses
WHERE ST_DWithin(location, ST_MakePoint(-122.4, 37.8)::geography, 10000);

CREATE INDEX idx_warehouses_location_gist ON warehouses USING GIST (location);

-- After the index: GiST prunes subtrees whose bounding box cannot possibly
-- overlap the search radius before ever computing an exact distance.
EXPLAIN ANALYZE
SELECT name FROM warehouses
WHERE ST_DWithin(location, ST_MakePoint(-122.4, 37.8)::geography, 10000);

-- k-nearest-neighbor query using GiST's distance-ordering support.
EXPLAIN ANALYZE
SELECT name FROM warehouses
ORDER BY location <-> ST_MakePoint(-122.4, 37.8)::geography
LIMIT 5;

-- ===========================================================================
-- PART 3: BRIN for naturally-ordered, append-only time-series data
-- ===========================================================================
DROP TABLE IF EXISTS sensor_readings;
CREATE TABLE sensor_readings (
    id          BIGSERIAL PRIMARY KEY,
    sensor_id   INT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    value       NUMERIC(10, 2) NOT NULL
);
-- Insert in recorded_at order, matching real append-only ingestion --
-- BRIN's effectiveness depends on this physical/logical correlation
-- (see CH11_PostgreSQL.md Section 4.8's failure mode).
INSERT INTO sensor_readings (sensor_id, recorded_at, value)
SELECT (random() * 100)::INT,
       TIMESTAMPTZ '2026-01-01' + (g || ' seconds')::INTERVAL,
       random() * 100
FROM generate_series(1, 5000000) g;

EXPLAIN ANALYZE
SELECT count(*) FROM sensor_readings
WHERE recorded_at BETWEEN '2026-02-01' AND '2026-02-02';

-- A BRIN index over a large, naturally-ordered column costs a tiny
-- fraction of an equivalent B-tree's storage.
CREATE INDEX idx_sensor_readings_recorded_at_brin
    ON sensor_readings USING BRIN (recorded_at) WITH (pages_per_range = 32);

SELECT pg_size_pretty(pg_relation_size('idx_sensor_readings_recorded_at_brin')) AS brin_size;

EXPLAIN ANALYZE
SELECT count(*) FROM sensor_readings
WHERE recorded_at BETWEEN '2026-02-01' AND '2026-02-02';

-- Check physical correlation directly -- BRIN degrades silently if this
-- drifts toward 0 after heavy out-of-order churn.
SELECT attname, correlation
FROM pg_stats
WHERE tablename = 'sensor_readings' AND attname = 'recorded_at';

-- ===========================================================================
-- PART 4: partial index for a narrow, hot query subset
-- ===========================================================================
DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
    id          BIGSERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    status      TEXT NOT NULL
);
INSERT INTO orders (customer_id, status)
SELECT (random() * 100000)::INT,
       CASE WHEN g % 5000 = 0 THEN 'pending' ELSE 'completed' END
FROM generate_series(1, 10000000) g;

-- A full index on (customer_id) would carry every one of the 10 million
-- rows even though "pending" orders are a tiny, constantly-churning subset.
CREATE INDEX idx_orders_customer_pending_partial
    ON orders (customer_id)
    WHERE status = 'pending';

SELECT pg_size_pretty(pg_relation_size('idx_orders_customer_pending_partial')) AS partial_index_size;

-- Planner uses the small partial index directly for this exact predicate shape.
EXPLAIN ANALYZE
SELECT * FROM orders WHERE status = 'pending' AND customer_id = 42;

-- This broader predicate cannot be proven covered by the narrower partial
-- index, so the planner falls back to a sequential/bitmap scan instead --
-- the failure mode documented in CH11_PostgreSQL.md Section 4.9.
EXPLAIN ANALYZE
SELECT * FROM orders WHERE status IN ('pending', 'processing') AND customer_id = 42;
