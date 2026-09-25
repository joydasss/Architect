-- Chapter: Normalization (06_Databases_and_Storage/CH01_Normalization.md)
-- Example 1 — the starting point: a single, unnormalized "flat file" table
-- (violates 1NF via repeating groups, and would still violate 2NF/3NF even
-- if the repeating groups were removed naively). This is the shape a
-- spreadsheet-to-database migration typically produces.

CREATE TABLE orders_unnormalized (
    order_id            INTEGER,
    order_date          DATE,
    customer_name       VARCHAR(100),
    customer_email      VARCHAR(100),
    customer_address    VARCHAR(200),
    sales_rep_name      VARCHAR(100),
    sales_rep_region    VARCHAR(50),
    -- Repeating group #1: line item 1 (violates 1NF)
    product_1_sku       VARCHAR(20),
    product_1_name      VARCHAR(100),
    product_1_price     DECIMAL(10, 2),
    product_1_qty       INTEGER,
    -- Repeating group #2: line item 2 (violates 1NF)
    product_2_sku       VARCHAR(20),
    product_2_name      VARCHAR(100),
    product_2_price     DECIMAL(10, 2),
    product_2_qty       INTEGER
);

-- Sample data showing the anomalies this shape invites:
--  * customer_email/customer_address are repeated on every order row for the
--    same customer (update anomaly: fixing a typo in one row leaves others stale).
--  * An order with 3+ items has nowhere to go (insert anomaly: the schema
--    caps line items at 2, or forces a NULL-padded third repeating group).
--  * Deleting the one order a brand-new customer ever placed deletes the only
--    record of that customer's email/address (delete anomaly).
INSERT INTO orders_unnormalized VALUES
    (1001, '2026-01-15', 'Aria Chen', 'aria@example.com', '12 Birch St, Austin, TX',
     'Devon Ruiz', 'South',
     'SKU-100', 'Wireless Mouse', 24.99, 2,
     'SKU-204', 'USB-C Hub', 39.99, 1),
    (1002, '2026-01-16', 'Aria Chen', 'aria@example.com', '12 Birch St, Austin, TX',
     'Devon Ruiz', 'South',
     'SKU-311', 'Mechanical Keyboard', 89.99, 1,
     NULL, NULL, NULL, NULL);
