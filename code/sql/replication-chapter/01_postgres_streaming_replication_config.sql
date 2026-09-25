-- PostgreSQL leader/follower streaming replication: annotated primary + replica config.
-- Corresponds to CH07_Replication.md Sections 4.2, 4.3, 9.

-- ===================== ON THE LEADER (primary) =====================

-- postgresql.conf on the leader
-- wal_level must be at least 'replica' to emit enough WAL detail for streaming.
-- wal_level = replica
-- max_wal_senders = 10          -- max concurrent WAL-streaming connections (followers)
-- max_replication_slots = 10    -- one slot reserved per follower, see below

-- A replication slot pins WAL retention to a specific follower's progress,
-- preventing the leader from recycling WAL a lagging follower still needs
-- (the Section 4.2 "forced full re-seed" failure mode).
SELECT pg_create_physical_replication_slot('replica_east_1');

-- pg_hba.conf entry authorizing the replication user from the follower's host.
-- host    replication     replicator      10.0.2.0/24            scram-sha-256

-- Create a dedicated, least-privilege replication role (Section 13: never
-- reuse application credentials for replication traffic).
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'change_me_use_a_secrets_manager';

-- --- Durability/latency trade-off knobs (Section 4.3) ---

-- Fully asynchronous (default): leader never waits on a follower to commit.
-- synchronous_commit = off
-- synchronous_standby_names = ''

-- Semi-synchronous: leader waits for a follower to confirm WAL *receipt*
-- (not full apply) before acknowledging the client's commit.
-- synchronous_commit = remote_write
-- synchronous_standby_names = 'FIRST 1 (replica_east_1, replica_east_2)'

-- Fully synchronous: leader waits for the standby to confirm it has
-- *applied* (made queryable) the WAL record before acknowledging commit.
-- synchronous_commit = remote_apply
-- synchronous_standby_names = 'FIRST 1 (replica_east_1)'

-- Require TLS on replication connections, not only client connections (Section 13).
-- ssl = on
-- ssl_cert_file = 'server.crt'
-- ssl_key_file  = 'server.key'

-- ===================== ON THE FOLLOWER (replica) =====================

-- standby.signal file (empty, presence alone marks this instance as a standby)
-- touch $PGDATA/standby.signal

-- postgresql.conf on the follower: connect back to the leader over TLS,
-- and bind to the reserved replication slot created above.
-- primary_conninfo = 'host=leader.db.internal port=5432 user=replicator
--   password=change_me_use_a_secrets_manager sslmode=verify-full application_name=replica_east_1'
-- primary_slot_name = 'replica_east_1'

-- Allow read-only queries against the follower while it replays WAL.
-- hot_standby = on

-- ===================== OBSERVABILITY QUERIES (Section 14) =====================

-- On the leader: per-follower transfer + apply lag, in bytes and seconds.
SELECT
    application_name,
    client_addr,
    state,
    pg_wal_lsn_diff(sent_lsn, replay_lsn)      AS bytes_behind_total,
    write_lag,
    flush_lag,
    replay_lag
FROM pg_stat_replication;

-- On the leader: WAL retention headroom for the reserved slot (Section 4.2).
SELECT slot_name, active, pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS bytes_retained
FROM pg_replication_slots;
