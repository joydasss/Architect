// Section 4.1 — Property graph model + optional schema (constraints/indexes).
// Demonstrates: nodes with labels/properties, typed+directed relationships
// with their own properties, and Neo4j's opt-in schema layer on top of an
// otherwise schema-optional model.

// --- Create a small property graph -----------------------------------

CREATE (alice:Person {personId: "p-1001", name: "Alice", age: 34})
CREATE (bob:Person {personId: "p-1002", name: "Bob", age: 29})
CREATE (carol:Person {personId: "p-1003", name: "Carol", age: 41})
CREATE (acme:Company {companyId: "c-01", name: "Acme Robotics"})
CREATE (widget:Product {productId: "sku-500", name: "Widget Pro", price: 49.99})
CREATE (gadget:Product {productId: "sku-501", name: "Gadget Max", price: 89.99})

// Relationships carry their own properties (Section 4.1) — no join table
// needed to attach "since" or "quantity" to the connection itself.
CREATE (alice)-[:FOLLOWS {since: date("2021-03-01")}]->(bob)
CREATE (bob)-[:FOLLOWS {since: date("2022-07-15")}]->(carol)
CREATE (alice)-[:WORKS_AT {role: "Engineer", startDate: date("2018-01-10")}]->(acme)
CREATE (bob)-[:WORKS_AT {role: "Designer", startDate: date("2020-05-01")}]->(acme)
CREATE (alice)-[:PURCHASED {quantity: 2, purchasedAt: datetime("2024-02-10T09:15:00Z")}]->(widget)
CREATE (bob)-[:PURCHASED {quantity: 1, purchasedAt: datetime("2024-02-11T14:30:00Z")}]->(widget)
CREATE (carol)-[:PURCHASED {quantity: 1, purchasedAt: datetime("2024-02-12T11:00:00Z")}]->(gadget);

// --- Optional schema: constraints and indexes -------------------------
// Uniqueness constraint: no two Person nodes may share the same personId.
// This also implicitly creates a backing index, accelerating lookups by
// personId the same way a UNIQUE column + index would in a relational table.
CREATE CONSTRAINT person_id_unique IF NOT EXISTS
FOR (p:Person) REQUIRE p.personId IS UNIQUE;

// Node-key constraint (Enterprise Edition): every Product must have BOTH
// productId and name present, and the combination must be unique — the
// graph-native equivalent of a composite primary key.
CREATE CONSTRAINT product_key IF NOT EXISTS
FOR (pr:Product) REQUIRE (pr.productId, pr.name) IS NODE KEY;

// Property (B-tree) index on Company.name — accelerates the anchor lookup
// in patterns like: MATCH (c:Company {name: $name}) ...
// (Recapped from Indexes: same B-tree structure/selectivity reasoning as
// a relational secondary index — see CH03_Indexes.md.)
CREATE INDEX company_name_index IF NOT EXISTS
FOR (c:Company) ON (c.name);

// Verify: list all constraints and indexes just created.
SHOW CONSTRAINTS;
SHOW INDEXES;
