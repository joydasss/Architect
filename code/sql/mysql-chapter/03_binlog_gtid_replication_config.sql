-- MySQL binlog format / GTID / source-replica replication configuration.
-- Shown as the my.cnf stanzas plus the SQL commands each role runs, since
-- this "code example" is operational configuration, not application code.

-- ============================================================
-- SOURCE (formerly "master") -- /etc/mysql/conf.d/source.cnf
-- ============================================================
-- [mysqld]
-- server_id                    = 1
-- log_bin                      = /var/log/mysql/mysql-bin
-- binlog_format                = ROW          -- see chapter 4.9 for the tradeoffs vs STATEMENT/MIXED
-- binlog_row_image             = FULL         -- FULL logs before+after image of every changed column
-- gtid_mode                    = ON           -- Global Transaction Identifiers (chapter 4.10)
-- enforce_gtid_consistency     = ON           -- rejects statements GTID-based replication can't safely replay
-- sync_binlog                  = 1            -- fsync the binlog on every commit (durability over raw throughput)
-- innodb_flush_log_at_trx_commit = 1          -- fsync the InnoDB redo log on every commit
-- rpl_semi_sync_source_enabled = ON           -- source side of semi-sync (chapter 4.14)
-- rpl_semi_sync_source_timeout = 1000         -- ms to wait for one ACK before falling back to async

-- Create a dedicated, minimally-privileged replication user (never reuse
-- an application credential for replication traffic):
CREATE USER 'replicator'@'%' IDENTIFIED WITH mysql_native_password BY 'REPLACE_WITH_STRONG_SECRET';
GRANT REPLICATION SLAVE ON *.* TO 'replicator'@'%';

-- Take a consistent snapshot to seed the replica (mysqldump shown for
-- clarity; Percona XtraBackup is the standard production choice because
-- it is a hot/non-blocking physical backup):
-- mysqldump --single-transaction --source-data=2 --all-databases > seed.sql

-- ============================================================
-- REPLICA (formerly "slave") -- /etc/mysql/conf.d/replica.cnf
-- ============================================================
-- [mysqld]
-- server_id                    = 2            -- MUST be unique across the whole topology
-- gtid_mode                    = ON
-- enforce_gtid_consistency     = ON
-- read_only                    = ON           -- rejects writes from anyone except the replication thread
-- super_read_only              = ON           -- also rejects writes from SUPER-privileged accounts
-- relay_log                    = /var/log/mysql/relay-bin
-- log_replica_updates          = ON           -- required if this replica will itself have sub-replicas
-- rpl_semi_sync_replica_enabled = ON          -- replica side of semi-sync

-- Point the replica at the source using GTID auto-positioning: MySQL 8's
-- GTID-based CHANGE REPLICATION SOURCE TO needs no binlog file/position
-- pair (see chapter 4.10) -- the replica and source negotiate the correct
-- resume point purely from the GTID sets each has already executed.
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST     = 'db-source.internal',
    SOURCE_USER     = 'replicator',
    SOURCE_PASSWORD = 'REPLACE_WITH_STRONG_SECRET',
    SOURCE_AUTO_POSITION = 1;

START REPLICA;

-- Verify health: Replica_IO_Running and Replica_SQL_Running must both be
-- "Yes"; Seconds_Behind_Source is the observable replication-lag signal.
SHOW REPLICA STATUS\G

-- ============================================================
-- Failover: promote a replica to source after a source outage
-- ============================================================
-- 1. Confirm the OLD source is truly unreachable (avoid split-brain --
--    fence it at the network/VIP layer first if at all possible).
STOP REPLICA;
RESET REPLICA ALL;                 -- clears replication-source metadata
-- 2. Point application traffic (via a proxy/VIP/service-discovery entry,
--    never a hardcoded hostname) at this instance.
SET GLOBAL read_only = OFF;
SET GLOBAL super_read_only = OFF;
-- 3. Re-point every OTHER surviving replica at the newly promoted source
--    using the same CHANGE REPLICATION SOURCE TO ... SOURCE_AUTO_POSITION=1
--    pattern above -- GTIDs make this safe even if replicas were at
--    slightly different apply positions, because MySQL replays only the
--    GTIDs the replica has not yet executed.
