-- Referenced from 06_Databases_and_Storage/CH03_Indexes.md (Section 10).
-- Demonstrates the leftmost-prefix rule: a composite index's column order
-- determines which queries can use it as a seek and which cannot.

CREATE TABLE support_tickets (
    ticket_id    BIGSERIAL PRIMARY KEY,
    tenant_id    BIGINT NOT NULL,
    priority     TEXT NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL,
    subject      TEXT NOT NULL
);

INSERT INTO support_tickets (tenant_id, priority, created_at, subject)
SELECT
    (random() * 2000)::BIGINT,
    (ARRAY['LOW','MEDIUM','HIGH','URGENT'])[1 + floor(random() * 4)::INT],
    TIMESTAMPTZ '2023-01-01' + (random() * 1000) * INTERVAL '1 day',
    'Ticket subject ' || g
FROM generate_series(1, 2000000) AS g;

-- Composite index: (tenant_id, priority, created_at). Column order matters
-- because a B+tree composite index physically sorts entries by the first
-- column, then the second within each first-column value, then the third
-- within each second-column value -- see Section 4.5.
CREATE INDEX idx_tickets_tenant_priority_created
    ON support_tickets (tenant_id, priority, created_at);

ANALYZE support_tickets;

-- USES the index as a seek: tenant_id is the leftmost column, so the planner
-- can jump straight to the matching range of leaf entries.
EXPLAIN (ANALYZE, BUFFERS)
SELECT ticket_id, subject
FROM support_tickets
WHERE tenant_id = 42;

-- STILL uses the index as a seek: tenant_id + priority together form a valid
-- leftmost prefix, narrowing the leaf-entry range further than tenant_id alone.
EXPLAIN (ANALYZE, BUFFERS)
SELECT ticket_id, subject
FROM support_tickets
WHERE tenant_id = 42 AND priority = 'URGENT';

-- STILL uses the index, and can use the third column as a range bound within
-- the (tenant_id, priority) prefix, because created_at is a contiguous suffix
-- of the indexed columns actually being filtered.
EXPLAIN (ANALYZE, BUFFERS)
SELECT ticket_id, subject
FROM support_tickets
WHERE tenant_id = 42 AND priority = 'URGENT'
  AND created_at >= TIMESTAMPTZ '2023-06-01';

-- CANNOT use idx_tickets_tenant_priority_created as a seek: priority is not
-- the leftmost column, so the planner cannot binary-search into the tree by
-- priority alone -- it would have to read every tenant_id's priority=URGENT
-- entries, which is not meaningfully cheaper than a full scan. Expect a
-- Seq Scan (or, if a separate priority-only index exists, use of that one).
EXPLAIN (ANALYZE, BUFFERS)
SELECT ticket_id, subject
FROM support_tickets
WHERE priority = 'URGENT';

-- Fix for the query above: either reorder a dedicated index with priority
-- leftmost, or (more common in practice) accept that this access pattern
-- needs its own index if it is a genuinely frequent query shape.
CREATE INDEX idx_tickets_priority_created ON support_tickets (priority, created_at);
ANALYZE support_tickets;

EXPLAIN (ANALYZE, BUFFERS)
SELECT ticket_id, subject
FROM support_tickets
WHERE priority = 'URGENT';
