-- 04_columnstore_index_analytics.sql
-- Columnstore index demo for CH14_SQLServer.md, Section 4.5 and 10.
-- Creates a clustered columnstore index over a wide fact table,
-- inspects rowgroup/Deltastore state, and contrasts a batch-mode
-- aggregate plan against the equivalent rowstore plan.

-- ============================================================
-- Step 1: a wide sales-fact table, initially on a rowstore clustered
-- index -- the "before" state from Section 4.5's scenario.
-- ============================================================
CREATE TABLE dbo.SalesFact_Rowstore
(
    SaleId       BIGINT IDENTITY(1,1) NOT NULL,
    SaleDate     DATE   NOT NULL,
    Region       VARCHAR(50) NOT NULL,
    StoreId      INT NOT NULL,
    ProductId    INT NOT NULL,
    CustomerId   INT NOT NULL,
    Amount       DECIMAL(12,2) NOT NULL,
    Quantity     INT NOT NULL,
    -- ...additional descriptive columns omitted for brevity...
    CONSTRAINT PK_SalesFact_Rowstore PRIMARY KEY CLUSTERED (SaleId)
);
GO

-- ============================================================
-- Step 2: convert to a clustered columnstore index. This REPLACES the
-- rowstore clustered index entirely -- the columnstore becomes the
-- table's storage, exactly as Section 4.5 describes; the "before"
-- table above is created separately here only for comparison purposes.
-- ============================================================
CREATE TABLE dbo.SalesFact_Columnstore
(
    SaleId       BIGINT NOT NULL,
    SaleDate     DATE   NOT NULL,
    Region       VARCHAR(50) NOT NULL,
    StoreId      INT NOT NULL,
    ProductId    INT NOT NULL,
    CustomerId   INT NOT NULL,
    Amount       DECIMAL(12,2) NOT NULL,
    Quantity     INT NOT NULL,
    INDEX CCI_SalesFact_Columnstore CLUSTERED COLUMNSTORE
);
GO

-- Bulk-load rows so they land directly in compressed rowgroups rather
-- than the uncompressed Deltastore (Section 4.5's bulk-load-friendly
-- path).
INSERT INTO dbo.SalesFact_Columnstore
    (SaleId, SaleDate, Region, StoreId, ProductId, CustomerId, Amount, Quantity)
SELECT SaleId, SaleDate, Region, StoreId, ProductId, CustomerId, Amount, Quantity
FROM dbo.SalesFact_Rowstore;
GO

-- ============================================================
-- Step 3: inspect rowgroup state -- compressed rowgroups (state
-- COMPRESSED) versus the open, uncompressed Deltastore rowgroup
-- (state OPEN), tied to Section 4.5's tuple-mover explanation.
-- ============================================================
SELECT
    object_name(object_id) AS table_name,
    partition_number,
    row_group_id,
    state_desc,           -- OPEN (Deltastore) vs COMPRESSED
    total_rows,
    deleted_rows,
    size_in_bytes
FROM sys.dm_db_column_store_row_group_physical_stats
WHERE object_id = OBJECT_ID('dbo.SalesFact_Columnstore')
ORDER BY row_group_id;
GO

-- ============================================================
-- Step 4: the aggregate query both tables serve -- compare actual
-- execution plans between the two. The columnstore plan shows batch-
-- mode operators (Actual Execution Mode = Batch) reading only the
-- Amount and Region segments; the rowstore plan reads every column of
-- every qualifying row (Section 4.5).
-- ============================================================
SET STATISTICS XML ON;

SELECT Region, SUM(Amount) AS TotalSales
FROM dbo.SalesFact_Rowstore
WHERE SaleDate >= '2026-01-01'
GROUP BY Region;

SELECT Region, SUM(Amount) AS TotalSales
FROM dbo.SalesFact_Columnstore
WHERE SaleDate >= '2026-01-01'
GROUP BY Region;

SET STATISTICS XML OFF;
GO
