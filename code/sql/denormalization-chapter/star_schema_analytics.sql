-- Star schema for order analytics (OLAP), plus a precomputed rollup
-- materialized view built on top of it.
--
-- Referenced from 06_Databases_and_Storage/CH02_Denormalization.md (Section 10).
-- Written for PostgreSQL syntax (MATERIALIZED VIEW, REFRESH ... CONCURRENTLY).

-- ---------------------------------------------------------------------------
-- Dimension tables: denormalized on purpose. dim_product embeds the category
-- and brand name directly (no separate category/brand tables to join) --
-- this is the star-schema choice, traded against a snowflake schema's
-- normalized category_id -> categories table indirection (see Section 4.6).
-- ---------------------------------------------------------------------------
CREATE TABLE dim_date (
    date_key        INTEGER PRIMARY KEY,      -- e.g. 20260315
    full_date       DATE NOT NULL,
    day_of_week     TEXT NOT NULL,
    month_name      TEXT NOT NULL,
    quarter         SMALLINT NOT NULL,
    year            SMALLINT NOT NULL,
    is_weekend      BOOLEAN NOT NULL
);

CREATE TABLE dim_customer (
    customer_key    SERIAL PRIMARY KEY,
    customer_id     BIGINT NOT NULL,           -- natural key back to the OLTP system
    customer_name   TEXT NOT NULL,
    segment         TEXT NOT NULL,             -- denormalized, not a separate segments table
    country         TEXT NOT NULL,             -- denormalized, not a separate countries table
    signup_date_key INTEGER NOT NULL REFERENCES dim_date(date_key)
);

CREATE TABLE dim_product (
    product_key     SERIAL PRIMARY KEY,
    product_id      BIGINT NOT NULL,
    product_name    TEXT NOT NULL,
    category_name   TEXT NOT NULL,             -- denormalized: category name inlined, not category_id FK
    brand_name      TEXT NOT NULL              -- denormalized: brand name inlined, not brand_id FK
);

-- ---------------------------------------------------------------------------
-- Fact table: one row per order line item, all measures numeric and additive.
-- ---------------------------------------------------------------------------
CREATE TABLE fact_order_line (
    order_line_key  BIGSERIAL PRIMARY KEY,
    order_id        BIGINT NOT NULL,
    date_key        INTEGER NOT NULL REFERENCES dim_date(date_key),
    customer_key     INTEGER NOT NULL REFERENCES dim_customer(customer_key),
    product_key     INTEGER NOT NULL REFERENCES dim_product(product_key),
    quantity        INTEGER NOT NULL,
    unit_price_cents BIGINT NOT NULL,
    line_total_cents BIGINT NOT NULL           -- precomputed = quantity * unit_price_cents
);

CREATE INDEX idx_fact_order_line_date ON fact_order_line(date_key);
CREATE INDEX idx_fact_order_line_customer ON fact_order_line(customer_key);
CREATE INDEX idx_fact_order_line_product ON fact_order_line(product_key);

-- ---------------------------------------------------------------------------
-- Analytical query that this schema is designed to make fast: a single-hop
-- join from the fact table straight to fully-denormalized dimensions, with
-- no multi-level dimension-hierarchy joins (contrast with the snowflake
-- version discussed in Section 4.6, which would need an extra join per
-- normalized dimension level).
-- ---------------------------------------------------------------------------
SELECT
    d.year,
    d.quarter,
    p.category_name,
    c.segment,
    SUM(f.line_total_cents) AS revenue_cents,
    COUNT(DISTINCT f.order_id) AS order_count
FROM fact_order_line f
JOIN dim_date d     ON d.date_key = f.date_key
JOIN dim_product p  ON p.product_key = f.product_key
JOIN dim_customer c ON c.customer_key = f.customer_key
WHERE d.year = 2026
GROUP BY d.year, d.quarter, p.category_name, c.segment
ORDER BY revenue_cents DESC;

-- ---------------------------------------------------------------------------
-- Precomputed aggregate / rollup, as a materialized view: pre-aggregates
-- revenue per (quarter, category) so a dashboard query becomes a single
-- indexed lookup instead of a scan-and-aggregate over the full fact table.
-- Chosen here as an eager-on-refresh, lazy-on-read view: the query only sees
-- the data as of the last REFRESH, not the live fact table.
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW mv_quarterly_category_revenue AS
SELECT
    d.year,
    d.quarter,
    p.category_name,
    SUM(f.line_total_cents) AS revenue_cents,
    COUNT(DISTINCT f.order_id) AS order_count
FROM fact_order_line f
JOIN dim_date d    ON d.date_key = f.date_key
JOIN dim_product p ON p.product_key = f.product_key
GROUP BY d.year, d.quarter, p.category_name
WITH DATA;

-- A unique index is required for CONCURRENTLY refresh (avoids locking readers
-- out of the view while a refresh is in progress — see Section 11).
CREATE UNIQUE INDEX idx_mv_quarterly_category_revenue
    ON mv_quarterly_category_revenue (year, quarter, category_name);

-- Run on a schedule (e.g. every 15 minutes) by an external job/cron/orchestrator:
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_quarterly_category_revenue;
