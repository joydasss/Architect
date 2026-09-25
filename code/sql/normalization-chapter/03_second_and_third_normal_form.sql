-- Example 3 — progressive decomposition from 1NF to 2NF to 3NF, ending in a
-- schema that is also BCNF (Boyce-Codd Normal Form) for this data shape,
-- because every determinant here is a candidate key of its own table.
--
-- 2NF step: split out product_sku/product_name/product_price into their own
-- table, because they depend only on product_sku (part of the orders_1nf
-- composite key), not on the full (order_id, line_number) key.
--
-- 3NF step: split out customer_* and sales_rep_* columns into their own
-- tables, because they depend on customer_id/sales_rep_id (non-key
-- attributes of the order), not on order_id itself -- a transitive
-- dependency of the form order_id -> customer_id -> customer_email.

CREATE TABLE customers (
    customer_id     INTEGER PRIMARY KEY,
    customer_name   VARCHAR(100) NOT NULL,
    customer_email  VARCHAR(100) NOT NULL,
    customer_address VARCHAR(200) NOT NULL
);

CREATE TABLE sales_reps (
    sales_rep_id    INTEGER PRIMARY KEY,
    sales_rep_name  VARCHAR(100) NOT NULL,
    sales_rep_region VARCHAR(50) NOT NULL
);

CREATE TABLE products (
    product_sku     VARCHAR(20) PRIMARY KEY,
    product_name    VARCHAR(100) NOT NULL,
    -- Price lives here, not on the order line, because *catalog* price is a
    -- fact about the product. The price actually charged on a historical
    -- order is a distinct fact captured on order_items.unit_price below --
    -- conflating the two is a common normalization mistake (Section 17).
    catalog_price   DECIMAL(10, 2) NOT NULL
);

CREATE TABLE orders (
    order_id        INTEGER PRIMARY KEY,
    order_date      DATE NOT NULL,
    customer_id     INTEGER NOT NULL REFERENCES customers(customer_id),
    sales_rep_id    INTEGER NOT NULL REFERENCES sales_reps(sales_rep_id)
);

CREATE TABLE order_items (
    order_id        INTEGER NOT NULL REFERENCES orders(order_id),
    line_number     INTEGER NOT NULL,
    product_sku     VARCHAR(20) NOT NULL REFERENCES products(product_sku),
    unit_price      DECIMAL(10, 2) NOT NULL, -- price *at the time of sale*
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (order_id, line_number)
);

-- Every functional dependency now has a candidate key on its left-hand side:
--   customers:   customer_id  -> customer_name, customer_email, customer_address
--   sales_reps:  sales_rep_id -> sales_rep_name, sales_rep_region
--   products:    product_sku  -> product_name, catalog_price
--   orders:      order_id     -> order_date, customer_id, sales_rep_id
--   order_items: (order_id, line_number) -> product_sku, unit_price, quantity
-- This is what "3NF/BCNF" means operationally: no non-key column depends on
-- anything less than a whole candidate key, and no determinant is a
-- non-candidate-key column.

INSERT INTO customers VALUES (1, 'Aria Chen', 'aria@example.com', '12 Birch St, Austin, TX');
INSERT INTO sales_reps VALUES (1, 'Devon Ruiz', 'South');
INSERT INTO products VALUES
    ('SKU-100', 'Wireless Mouse', 24.99),
    ('SKU-204', 'USB-C Hub', 39.99),
    ('SKU-311', 'Mechanical Keyboard', 89.99);
INSERT INTO orders VALUES
    (1001, '2026-01-15', 1, 1),
    (1002, '2026-01-16', 1, 1);
INSERT INTO order_items VALUES
    (1001, 1, 'SKU-100', 24.99, 2),
    (1001, 2, 'SKU-204', 39.99, 1),
    (1002, 1, 'SKU-311', 89.99, 1);

-- Fixing Aria Chen's email now requires exactly one UPDATE, on exactly one
-- row, regardless of how many orders she has ever placed -- the update
-- anomaly from 01_unnormalized_schema.sql is structurally gone.
UPDATE customers SET customer_email = 'aria.chen@example.com' WHERE customer_id = 1;
