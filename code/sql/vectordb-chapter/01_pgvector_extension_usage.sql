-- CH21 Vector Databases: pgvector extension usage (Sections 4.1, 4.5, 8)
-- Demonstrates adding vector search to PostgreSQL via its extension
-- architecture (recapped from CH11_PostgreSQL.md Section 4.5), including a
-- HNSW ANN index, cosine-distance nearest-neighbor queries, and hybrid
-- search combining a metadata WHERE clause with vector similarity ordering.

-- 1. Install the extension (one-time, per database).
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. A table that mixes structured columns with a vector column, exactly
--    the pattern that lets vector search share a transaction boundary with
--    ordinary relational writes (Section 8).
CREATE TABLE IF NOT EXISTS support_articles (
    article_id      BIGSERIAL PRIMARY KEY,
    title           TEXT NOT NULL,
    body            TEXT NOT NULL,
    department      TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'published',
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- 1536 dimensions matches a common text-embedding-model output size.
    embedding       VECTOR(1536) NOT NULL
);

-- 3. Build an HNSW index (Section 4.3) under cosine distance. pgvector
--    exposes cosine distance as the `<=>` operator; `m` and
--    `ef_construction` map directly to HNSW's neighbor-degree and
--    build-time beam-width parameters from Section 4.3.
CREATE INDEX IF NOT EXISTS support_articles_embedding_hnsw_idx
    ON support_articles
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- 4. Tune the search-time beam width (ef_search, Section 4.3) for this
--    session. Higher values trade latency for recall.
SET hnsw.ef_search = 100;

-- 5. Plain nearest-neighbor query: top 5 articles closest to a query
--    embedding under cosine distance. In application code, :query_embedding
--    would be bound to the embedded user query vector (Section 4.1).
-- SELECT article_id, title, embedding <=> :query_embedding AS distance
-- FROM support_articles
-- ORDER BY embedding <=> :query_embedding
-- LIMIT 5;

-- 6. Hybrid search (Section 4.5): pre-filter on metadata first via the
--    WHERE clause, then rank the filtered candidates by vector distance.
--    PostgreSQL's planner can use the department/status predicate to
--    narrow the row set before the ORDER BY distance sort runs, which is
--    the SQL-level analogue of the pre-filtering strategy this chapter
--    recommends for highly selective filters over post-filtering.
-- SELECT article_id, title, embedding <=> :query_embedding AS distance
-- FROM support_articles
-- WHERE department = 'legal'
--   AND status = 'published'
-- ORDER BY embedding <=> :query_embedding
-- LIMIT 5;

-- 7. Verify the planner is actually using the HNSW index (not a sequential
--    scan) for a representative query -- the discipline this chapter's
--    Testing section (16) recommends running before trusting any recall
--    or latency measurement.
-- EXPLAIN ANALYZE
-- SELECT article_id
-- FROM support_articles
-- ORDER BY embedding <=> :query_embedding
-- LIMIT 5;
