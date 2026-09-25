-- InnoDB clustered-index table organization: the primary key IS the data.
-- Demonstrates why primary-key choice drives physical row placement, why a
-- secondary-index lookup costs two B+Tree traversals, and how to read
-- EXPLAIN output that reveals this "index condition pushdown" behavior.

-- 1. A naturally-clustered table: an ascending, monotonic primary key means
--    every insert appends to the rightmost leaf page of the clustered
--    B+Tree -- no random-page splits, high page-fill factor.
CREATE TABLE orders (
    order_id      BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    customer_id   BIGINT UNSIGNED NOT NULL,
    order_status  ENUM('PENDING','PAID','SHIPPED','CANCELLED') NOT NULL,
    total_cents   INT UNSIGNED NOT NULL,
    created_at    DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    PRIMARY KEY (order_id),
    KEY idx_customer_id (customer_id),      -- secondary index: leaf stores order_id, not the row
    KEY idx_created_at (created_at)
) ENGINE=InnoDB;

-- 2. The anti-pattern: a UUID (v4, random) primary key on a high-write
--    table. Every insert lands at a random leaf page instead of the
--    rightmost page, forcing constant page splits and cache-unfriendly
--    random I/O against the clustered B+Tree -- because in InnoDB the
--    clustered index leaf pages ARE the table's on-disk rows, not just
--    pointers to them.
CREATE TABLE sessions_bad_pk (
    session_uuid  CHAR(36) NOT NULL,        -- random v4 UUID -- causes page-split thrash
    user_id       BIGINT UNSIGNED NOT NULL,
    payload_json  JSON NOT NULL,
    PRIMARY KEY (session_uuid)
) ENGINE=InnoDB;

-- The fix: keep a surrogate monotonic BIGINT clustering key and demote the
-- UUID to a secondary unique index (or use UUID v7 / ULID, whose leading
-- bytes are a timestamp so the value is monotonic and clusters well).
CREATE TABLE sessions_good_pk (
    session_seq   BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    session_uuid  CHAR(36) NOT NULL,
    user_id       BIGINT UNSIGNED NOT NULL,
    payload_json  JSON NOT NULL,
    PRIMARY KEY (session_seq),
    UNIQUE KEY uq_session_uuid (session_uuid)
) ENGINE=InnoDB;

-- 3. Observing the two-lookup cost of a secondary-index read.
-- A query filtering only on the secondary-indexed column must first find
-- the matching leaf entries in idx_customer_id (which store the primary
-- key value, order_id), then perform a SECOND B+Tree traversal into the
-- clustered index to fetch the remaining columns. EXPLAIN's "Using index
-- condition" / "key" column tells you which index InnoDB chose to satisfy
-- WHERE, but the row-fetch cost is the second, implicit clustered lookup.
EXPLAIN
SELECT order_id, order_status, total_cents
FROM orders
WHERE customer_id = 44201;
-- Expected plan: type=ref, key=idx_customer_id, key_len=8, rows=<n>,
-- Extra shows no "Using index" because order_status/total_cents are NOT
-- in idx_customer_id -- InnoDB must dereference the clustered index for
-- every matching row (the classic secondary-index-then-clustered-lookup).

-- 4. Turning the same query into a covering index avoids the second lookup
-- entirely: put every selected/filtered column into the secondary index so
-- the leaf page alone answers the query ("Using index" in EXPLAIN's Extra
-- column, i.e. an index-only scan).
ALTER TABLE orders
    ADD KEY idx_customer_covering (customer_id, order_status, total_cents);

EXPLAIN
SELECT order_id, order_status, total_cents
FROM orders
WHERE customer_id = 44201;
-- Expected plan: key=idx_customer_covering, Extra="Using index" -- no
-- clustered-index dereference needed; order_id is implicitly present in
-- every InnoDB secondary-index leaf entry as the row locator.
