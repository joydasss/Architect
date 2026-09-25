-- 03_query_store_plan_regression.sql
-- Query Store demo for CH14_SQLServer.md, Section 4.7 and 10. Enables
-- Query Store, surfaces a regressed query by comparing plan history, and
-- forces a previously known-good plan as an immediate mitigation.

-- ============================================================
-- Step 1: enable Query Store (on by default since SQL Server 2016, but
-- shown explicitly here with a retention window sized for incident
-- response, per Section 4.7's decision-implications guidance).
-- ============================================================
ALTER DATABASE ReportingWarehouse
SET QUERY_STORE = ON
(
    OPERATION_MODE = READ_WRITE,
    CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 30),
    DATA_FLUSH_INTERVAL_SECONDS = 900,
    MAX_STORAGE_SIZE_MB = 2048,
    QUERY_CAPTURE_MODE = AUTO -- throttles capture of trivial/ad-hoc queries
);
GO

-- ============================================================
-- Step 2: find queries whose average duration has regressed between
-- two time windows -- the "it feels slower" complaint turned into a
-- directly queryable fact (Section 4.7).
-- ============================================================
WITH RecentStats AS (
    SELECT
        rs.plan_id,
        q.query_id,
        AVG(rs.avg_duration) AS avg_duration_recent
    FROM sys.query_store_runtime_stats AS rs
    JOIN sys.query_store_plan AS p ON p.plan_id = rs.plan_id
    JOIN sys.query_store_query AS q ON q.query_id = p.query_id
    WHERE rs.last_execution_time >= DATEADD(DAY, -1, SYSUTCDATETIME())
    GROUP BY rs.plan_id, q.query_id
),
BaselineStats AS (
    SELECT
        rs.plan_id,
        q.query_id,
        AVG(rs.avg_duration) AS avg_duration_baseline
    FROM sys.query_store_runtime_stats AS rs
    JOIN sys.query_store_plan AS p ON p.plan_id = rs.plan_id
    JOIN sys.query_store_query AS q ON q.query_id = p.query_id
    WHERE rs.last_execution_time BETWEEN DATEADD(DAY, -8, SYSUTCDATETIME())
                                      AND DATEADD(DAY, -7, SYSUTCDATETIME())
    GROUP BY rs.plan_id, q.query_id
)
SELECT
    qt.query_sql_text,
    b.query_id,
    b.plan_id            AS baseline_plan_id,
    b.avg_duration_baseline,
    r.plan_id            AS recent_plan_id,
    r.avg_duration_recent,
    (r.avg_duration_recent - b.avg_duration_baseline) AS regression_delta_us
FROM BaselineStats AS b
JOIN RecentStats AS r ON r.query_id = b.query_id
JOIN sys.query_store_query AS qsq ON qsq.query_id = b.query_id
JOIN sys.query_store_query_text AS qt ON qt.query_text_id = qsq.query_text_id
WHERE r.avg_duration_recent > b.avg_duration_baseline * 5 -- flag 5x+ regressions
ORDER BY regression_delta_us DESC;
GO

-- ============================================================
-- Step 3: force the known-good baseline plan as an immediate
-- mitigation -- surgical, but not a root-cause fix (Section 4.7's
-- failure mode: forcing a plan and never revisiting it eventually
-- becomes worse than an unforced choice as data distribution shifts).
-- ============================================================
-- Replace @query_id / @plan_id with values identified in Step 2.
DECLARE @query_id INT = 42;
DECLARE @plan_id INT = 137;

EXEC sp_query_store_force_plan @query_id = @query_id, @plan_id = @plan_id;
GO

-- ============================================================
-- Step 4: schedule a follow-up review -- unforce the plan once the
-- underlying root cause (commonly stale statistics) has been fixed,
-- rather than leaving the forced plan in place indefinitely.
-- ============================================================
-- EXEC sp_query_store_unforce_plan @query_id = @query_id, @plan_id = @plan_id;
