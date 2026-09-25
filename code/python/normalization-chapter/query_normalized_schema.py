"""Chapter: Normalization (06_Databases_and_Storage/CH01_Normalization.md)

Example 4 (query-side) - reading from the normalized schema created by
code/sql/normalization-chapter/03_second_and_third_normal_form.sql.

Demonstrates the one real, structural cost of normalization that Section 11
(Performance) discusses in depth: reconstructing an "order summary" view now
requires JOINing five tables instead of reading one flat row, in exchange
for eliminating the update/insert/delete anomalies shown in Example 1.

Uses sqlite3 (stdlib) so the example runs with no external dependencies;
the same query is portable to PostgreSQL/MySQL with trivial syntax changes.
"""

import sqlite3
from pathlib import Path

SCHEMA_SQL = """
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    customer_address TEXT NOT NULL
);
CREATE TABLE sales_reps (
    sales_rep_id INTEGER PRIMARY KEY,
    sales_rep_name TEXT NOT NULL,
    sales_rep_region TEXT NOT NULL
);
CREATE TABLE products (
    product_sku TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    catalog_price NUMERIC NOT NULL
);
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    order_date TEXT NOT NULL,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    sales_rep_id INTEGER NOT NULL REFERENCES sales_reps(sales_rep_id)
);
CREATE TABLE order_items (
    order_id INTEGER NOT NULL REFERENCES orders(order_id),
    line_number INTEGER NOT NULL,
    product_sku TEXT NOT NULL REFERENCES products(product_sku),
    unit_price NUMERIC NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (order_id, line_number)
);
"""

SEED_SQL = """
INSERT INTO customers VALUES (1, 'Aria Chen', 'aria.chen@example.com', '12 Birch St, Austin, TX');
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
"""

# The query a "flat" report screen actually needs: one row per order line,
# with every human-readable attribute re-joined back together. This is the
# recurring cost of normalization -- every read-side denormalization the
# application needs must be reconstructed explicitly via JOINs (or handled
# separately, per Section 12, with a materialized read model).
ORDER_SUMMARY_QUERY = """
SELECT
    o.order_id,
    o.order_date,
    c.customer_name,
    c.customer_email,
    r.sales_rep_name,
    r.sales_rep_region,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) AS line_total
FROM orders AS o
JOIN customers AS c   ON c.customer_id = o.customer_id
JOIN sales_reps AS r  ON r.sales_rep_id = o.sales_rep_id
JOIN order_items AS oi ON oi.order_id = o.order_id
JOIN products AS p    ON p.product_sku = oi.product_sku
ORDER BY o.order_id, oi.line_number;
"""


def build_demo_database(db_path: str = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_SQL)
    conn.executescript(SEED_SQL)
    return conn


def print_order_summary(conn: sqlite3.Connection) -> None:
    cursor = conn.execute(ORDER_SUMMARY_QUERY)
    columns = [description[0] for description in cursor.description]
    for row in cursor.fetchall():
        record = dict(zip(columns, row))
        print(
            f"Order {record['order_id']} ({record['order_date']}) - "
            f"{record['customer_name']} <{record['customer_email']}> - "
            f"rep: {record['sales_rep_name']} ({record['sales_rep_region']}) - "
            f"{record['quantity']}x {record['product_name']} @ "
            f"{record['unit_price']} = {record['line_total']}"
        )


if __name__ == "__main__":
    connection = build_demo_database()
    print_order_summary(connection)
    connection.close()
