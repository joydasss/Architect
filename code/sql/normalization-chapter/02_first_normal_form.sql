-- Example 2 — 1NF (First Normal Form): eliminate repeating groups by giving
-- every line item its own row instead of its own set of columns. Every
-- column now holds a single atomic value, and there is no cap on the number
-- of items an order can have.

CREATE TABLE orders_1nf (
    order_id            INTEGER,
    line_number         INTEGER,
    order_date          DATE,
    customer_name       VARCHAR(100),
    customer_email      VARCHAR(100),
    customer_address    VARCHAR(200),
    sales_rep_name      VARCHAR(100),
    sales_rep_region    VARCHAR(50),
    product_sku         VARCHAR(20),
    product_name        VARCHAR(100),
    product_price       DECIMAL(10, 2),
    quantity            INTEGER,
    PRIMARY KEY (order_id, line_number)
);

-- 1NF removed the repeating-group anomaly, but every non-key column here
-- still depends on only *part* of the composite key (product_name depends
-- on product_sku alone, not on order_id) or on nothing in the key at all
-- (customer_email depends on the customer, not on this order) — these are
-- the partial and transitive dependencies that 2NF and 3NF target next.
INSERT INTO orders_1nf VALUES
    (1001, 1, '2026-01-15', 'Aria Chen', 'aria@example.com', '12 Birch St, Austin, TX',
     'Devon Ruiz', 'South', 'SKU-100', 'Wireless Mouse', 24.99, 2),
    (1001, 2, '2026-01-15', 'Aria Chen', 'aria@example.com', '12 Birch St, Austin, TX',
     'Devon Ruiz', 'South', 'SKU-204', 'USB-C Hub', 39.99, 1),
    (1002, 1, '2026-01-16', 'Aria Chen', 'aria@example.com', '12 Birch St, Austin, TX',
     'Devon Ruiz', 'South', 'SKU-311', 'Mechanical Keyboard', 89.99, 1);
