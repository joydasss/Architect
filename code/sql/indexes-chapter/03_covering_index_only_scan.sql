-- Referenced from 06_Databases_and_Storage/CH03_Indexes.md (Section 10).
-- Demonstrates a covering index turning an index-scan-plus-heap-lookup into
-- an index-only scan -- see Section 4.6.

CREATE TABLE product_catalog (
    product_id   BIGSERIAL PRIMARY KEY,
    sku          TEXT NOT NULL,
    category_id  INT NOT NULL,
    price_cents  INTEGER NOT NULL,
    description  TEXT NOT NULL   -- large column we do NOT want in the index
);

INSERT INTO product_catalog (sku, category_id, price_cents, description)
SELECT
    'SKU-' || g,
    (random() * 200)::INT,
    (random() * 500000)::INT,
    repeat('lorem ipsum descriptive text ', 20)  -- simulate a wide row
FROM generate_series(1, 3000000) AS g;

-- A plain (non-covering) index on category_id: satisfies the WHERE clause
-- but still requires a heap fetch per matching row to read price_cents,
-- because price_cents is not stored in this index's leaf entries.
CREATE INDEX idx_products_category ON product_catalog (category_id);
ANALYZE product_catalog;

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id, price_cents
FROM product_catalog
WHERE category_id = 17;
-- Expect "Index Scan" (not "Index Only Scan") plus a nonzero "Heap Fetches"
-- count, because price_cents lives only in the heap row, not this index.

-- Covering index: include price_cents in the index leaf entries (via
-- INCLUDE, which stores it without making it part of the sort key) so the
-- planner can answer the query from the index B+tree alone.
CREATE INDEX idx_products_category_covering
    ON product_catalog (category_id) INCLUDE (price_cents);
ANALYZE product_catalog;

EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id, price_cents
FROM product_catalog
WHERE category_id = 17;
-- Expect "Index Only Scan using idx_products_category_covering" with
-- "Heap Fetches: 0" (after a VACUUM has made the visibility map current),
-- because every selected/filtered column is present in the index leaf.

-- Adding description to the SELECT list defeats the covering index again --
-- description is not stored in the index, so this forces a heap fetch per
-- row, illustrating that "covering" is defined per query shape, not per table.
EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id, price_cents, description
FROM product_catalog
WHERE category_id = 17;
