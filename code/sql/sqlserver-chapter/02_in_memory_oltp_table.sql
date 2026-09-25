-- 02_in_memory_oltp_table.sql
-- In-Memory OLTP (Hekaton) demo for CH14_SQLServer.md, Section 4.4 and 10.
-- Shows the memory-optimized filegroup prerequisite, a lock-free hash-
-- indexed memory-optimized table, a natively compiled stored procedure,
-- and the optimistic-conflict retry pattern applications must implement
-- since Hekaton has no locking fallback to queue against.

-- ============================================================
-- Step 1: a database must have a MEMORY_OPTIMIZED_DATA filegroup before
-- it can host memory-optimized tables -- this is where their on-disk
-- checkpoint files (used for durability/recovery) are stored.
-- ============================================================
ALTER DATABASE TicketingPlatform
    ADD FILEGROUP TicketingPlatform_MOD CONTAINS MEMORY_OPTIMIZED_DATA;
GO

ALTER DATABASE TicketingPlatform
    ADD FILE (
        NAME = N'TicketingPlatform_MOD_1',
        FILENAME = N'D:\SQLData\TicketingPlatform_MOD_1'
    ) TO FILEGROUP TicketingPlatform_MOD;
GO

-- ============================================================
-- Step 2: the memory-optimized seat-inventory table (Section 4.4's
-- scenario). SCHEMA_AND_DATA persists both the schema and the rows
-- across restarts via the checkpoint-file stream + transaction log.
-- The hash index is the lock-free structure backing equality lookups
-- by SeatId; BUCKET_COUNT should be sized to roughly 1-2x expected
-- distinct key cardinality.
-- ============================================================
CREATE TABLE dbo.SeatInventory
(
    SeatId          INT             NOT NULL,
    EventId         INT             NOT NULL,
    AvailableCount  INT             NOT NULL,
    LastUpdatedUtc  DATETIME2       NOT NULL DEFAULT SYSUTCDATETIME(),

    CONSTRAINT PK_SeatInventory
        PRIMARY KEY NONCLUSTERED HASH (SeatId, EventId)
        WITH (BUCKET_COUNT = 1000000)
)
WITH (MEMORY_OPTIMIZED = ON, DURABILITY = SCHEMA_AND_DATA);
GO

-- ============================================================
-- Step 3: a natively compiled stored procedure -- compiled ahead of
-- time to native machine code, removing interpreter overhead entirely
-- for the hottest code path in the on-sale event (Section 4.4).
-- ============================================================
CREATE OR ALTER PROCEDURE dbo.ReserveSeat
    @SeatId INT,
    @EventId INT,
    @Quantity INT
WITH NATIVE_COMPILATION, SCHEMABINDING
AS
BEGIN ATOMIC WITH
(
    TRANSACTION ISOLATION LEVEL = SNAPSHOT,
    LANGUAGE = N'us_english'
)
    UPDATE dbo.SeatInventory
    SET AvailableCount = AvailableCount - @Quantity,
        LastUpdatedUtc = SYSUTCDATETIME()
    WHERE SeatId = @SeatId
      AND EventId = @EventId
      AND AvailableCount >= @Quantity;

    IF @@ROWCOUNT = 0
        THROW 51000, N'Seat unavailable or insufficient inventory.', 1;
END;
GO

-- ============================================================
-- Step 4: application-side retry pattern (illustrative; the actual
-- retry loop lives in the calling application, not T-SQL). Hekaton's
-- optimistic multi-version design (Section 4.4) means a write-write
-- conflict is surfaced as an error (SQL error 41302/41305/etc.)
-- immediately rather than the transaction blocking and queuing the
-- way a classical locked table would -- callers MUST retry.
-- Pseudocode, shown here as commented T-SQL-adjacent guidance:
--
--   retries = 0
--   while retries < MAX_RETRIES:
--       try:
--           EXEC dbo.ReserveSeat @SeatId, @EventId, @Quantity
--           break  -- success
--       except (conflict error 41302, 41305, 41325, 41301):
--           retries += 1
--           continue  -- re-run the whole procedure call from scratch
--       except (other errors):
--           raise  -- not a concurrency conflict, do not retry blindly
-- ============================================================

-- ============================================================
-- Step 5: confirm there is no PAGELATCH contention against this table
-- (there should be none -- Hekaton has no pages or latches at all),
-- contrasted against the classical-engine PAGELATCH_EX waits this
-- migration was designed to eliminate.
-- ============================================================
SELECT wait_type, waiting_tasks_count, wait_time_ms
FROM sys.dm_os_wait_stats
WHERE wait_type LIKE 'PAGELATCH%'
ORDER BY wait_time_ms DESC;
GO
