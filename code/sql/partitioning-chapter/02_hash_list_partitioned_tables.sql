-- 02_hash_list_partitioned_tables.sql
-- HASH partitioning (even write distribution, no natural ranges) and LIST
-- partitioning (a small, known set of discrete key values) side by side, to
-- contrast both against the RANGE example in 01_range_partitioned_table.sql.

-- ---------------------------------------------------------------------
-- HASH partitioning: "user_sessions" has no natural range or short list of
-- values to partition by, but customer_id is written and read uniformly, so
-- hashing spreads both writes and storage evenly across a fixed partition
-- count chosen up front (adding partitions later requires a rehash/reload,
-- unlike RANGE where a new partition is simply attached — see Section 4.3
-- and Section 4.5's key-selection trade-offs).
-- ---------------------------------------------------------------------
CREATE TABLE user_sessions (
    session_id    UUID NOT NULL DEFAULT gen_random_uuid(),
    customer_id   BIGINT NOT NULL,
    started_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    payload       JSONB,
    PRIMARY KEY (session_id, customer_id)
) PARTITION BY HASH (customer_id);

-- Four partitions, MODULUS 4 total, each claiming one REMAINDER bucket.
-- PostgreSQL hashes customer_id and routes the row to the partition whose
-- remainder matches (hash(customer_id) % 4).
CREATE TABLE user_sessions_p0 PARTITION OF user_sessions
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE user_sessions_p1 PARTITION OF user_sessions
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE user_sessions_p2 PARTITION OF user_sessions
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE user_sessions_p3 PARTITION OF user_sessions
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);

-- ---------------------------------------------------------------------
-- LIST partitioning: "billing_accounts" has a small, known, discrete set of
-- region values that map directly to a compliance/data-residency boundary —
-- a natural fit for LIST rather than RANGE (regions have no ordering) or
-- HASH (the discrete values themselves are meaningful to queries and to
-- operational placement, e.g. co-locating the EU partition's tablespace on
-- EU-resident storage).
-- ---------------------------------------------------------------------
CREATE TABLE billing_accounts (
    account_id    BIGINT GENERATED ALWAYS AS IDENTITY,
    region        TEXT NOT NULL,
    plan_tier     TEXT NOT NULL,
    PRIMARY KEY (account_id, region)
) PARTITION BY LIST (region);

CREATE TABLE billing_accounts_eu PARTITION OF billing_accounts
    FOR VALUES IN ('eu-west', 'eu-central', 'eu-north');
CREATE TABLE billing_accounts_us PARTITION OF billing_accounts
    FOR VALUES IN ('us-east', 'us-west');
CREATE TABLE billing_accounts_apac PARTITION OF billing_accounts
    FOR VALUES IN ('ap-southeast', 'ap-northeast');

-- A LIST partition also accepts a DEFAULT, exactly like RANGE, to catch any
-- region value introduced before the schema is updated to list it explicitly.
CREATE TABLE billing_accounts_default PARTITION OF billing_accounts DEFAULT;
