-- 01_availability_group_setup.sql
-- Always On Availability Group setup for CH14_SQLServer.md, Section 4.3 and
-- 10. Annotated T-SQL: recovery-model prerequisites (Section 4.1), replica
-- creation with sync/async commit modes, listener creation, and the
-- log_reuse_wait_desc check that confirms log truncation is unblocked.
-- Run each numbered step against the primary replica instance unless noted.

-- ============================================================
-- Step 1: prerequisite -- FULL recovery model is required for
-- Availability Groups, since the group ships transaction-log records
-- (Section 4.1's WAL) to secondaries; SIMPLE recovery truncates the log
-- at every checkpoint and cannot support this.
-- ============================================================
ALTER DATABASE CoreLedger SET RECOVERY FULL;
GO

-- A full backup must exist before a database can join an Availability
-- Group -- it is the baseline the secondary replicas restore from
-- before log shipping can begin.
BACKUP DATABASE CoreLedger
    TO DISK = N'\\backupshare\CoreLedger\CoreLedger_Full.bak'
    WITH INIT, COMPRESSION;
GO

BACKUP LOG CoreLedger
    TO DISK = N'\\backupshare\CoreLedger\CoreLedger_Log.trn'
    WITH INIT, COMPRESSION;
GO

-- ============================================================
-- Step 2: create the Availability Group with one synchronous replica
-- (automatic local failover) and one asynchronous replica (disaster
-- recovery), matching the tiered topology in Section 4.3 / Section 8.
-- ============================================================
CREATE AVAILABILITY GROUP [AG_CoreLedger]
    WITH (
        AUTOMATED_BACKUP_PREFERENCE = SECONDARY,
        FAILURE_CONDITION_LEVEL = 3,
        HEALTH_CHECK_TIMEOUT = 30000
    )
    FOR DATABASE CoreLedger
    REPLICA ON
        N'SQLPRIMARY' WITH (
            ENDPOINT_URL = N'TCP://sqlprimary.corp.local:5022',
            AVAILABILITY_MODE = SYNCHRONOUS_COMMIT,
            FAILOVER_MODE = AUTOMATIC,
            SECONDARY_ROLE(ALLOW_CONNECTIONS = NO)
        ),
        N'SQLSECSYNC' WITH (
            ENDPOINT_URL = N'TCP://sqlsecsync.corp.local:5022',
            AVAILABILITY_MODE = SYNCHRONOUS_COMMIT,
            FAILOVER_MODE = AUTOMATIC,
            SECONDARY_ROLE(ALLOW_CONNECTIONS = READ_ONLY)
        ),
        N'SQLSECASYNC-DR' WITH (
            ENDPOINT_URL = N'TCP://sqlsecasync-dr.corp.local:5022',
            AVAILABILITY_MODE = ASYNCHRONOUS_COMMIT,
            FAILOVER_MODE = MANUAL,
            SECONDARY_ROLE(ALLOW_CONNECTIONS = READ_ONLY)
        );
GO

-- ============================================================
-- Step 3: on each secondary instance, join the existing group and
-- restore the database WITH NORECOVERY so log shipping can continue
-- applying redo against it (the same redo mechanism from Section 4.1,
-- applied continuously rather than only after a crash).
-- ============================================================
-- Run on SQLSECSYNC and SQLSECASYNC-DR:
-- ALTER AVAILABILITY GROUP [AG_CoreLedger] JOIN;
-- RESTORE DATABASE CoreLedger
--     FROM DISK = N'\\backupshare\CoreLedger\CoreLedger_Full.bak'
--     WITH NORECOVERY;
-- RESTORE LOG CoreLedger
--     FROM DISK = N'\\backupshare\CoreLedger\CoreLedger_Log.trn'
--     WITH NORECOVERY;
-- ALTER DATABASE CoreLedger SET HADR AVAILABILITY GROUP = [AG_CoreLedger];

-- ============================================================
-- Step 4: create the listener -- the virtual name/IP that always
-- resolves to the current primary, so application connection strings
-- never change across a failover (Section 4.3).
-- ============================================================
ALTER AVAILABILITY GROUP [AG_CoreLedger]
    ADD LISTENER N'AGL-CoreLedger' (
        WITH IP ((N'10.10.4.50', N'255.255.255.0')),
        PORT = 1433
    );
GO

-- ============================================================
-- Step 5: verify the group is healthy and every secondary is
-- synchronized before relying on automatic failover.
-- ============================================================
SELECT
    ag.name                          AS availability_group,
    ar.replica_server_name,
    ars.role_desc,
    ars.synchronization_health_desc, -- must be HEALTHY for automatic failover
    ars.connected_state_desc
FROM sys.availability_groups AS ag
JOIN sys.availability_replicas AS ar
    ON ar.group_id = ag.group_id
JOIN sys.dm_hadr_availability_replica_states AS ars
    ON ars.replica_id = ar.replica_id
WHERE ag.name = N'AG_CoreLedger';
GO

-- ============================================================
-- Step 6: confirm log truncation is not blocked (Section 4.1's
-- failure mode) -- log_reuse_wait_desc should read NOTHING or
-- LOG_BACKUP transiently, never a sustained non-NOTHING value.
-- ============================================================
SELECT name, log_reuse_wait_desc
FROM sys.databases
WHERE name = N'CoreLedger';
GO
