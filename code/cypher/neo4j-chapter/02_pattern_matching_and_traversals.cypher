// Section 4.3 — Cypher pattern matching: fixed-depth, bounded variable-length,
// shortestPath(), and a two-hop recommendation pattern.
// Assumes the graph created by 01_property_graph_schema_and_constraints.cypher.

// --- 1. Fixed-depth pattern (one hop) ----------------------------------
// "Who works at Acme Robotics, and in what role?"
MATCH (p:Person)-[w:WORKS_AT]->(c:Company {name: "Acme Robotics"})
RETURN p.name AS employee, w.role AS role
ORDER BY employee;

// --- 2. Bounded variable-length path (Section 4.2/4.3) -----------------
// "Everyone reachable from Alice by following FOLLOWS, one to four hops."
// The upper bound (4) is a deliberate, domain-justified limit — an
// unbounded [:FOLLOWS*] pattern is Section 4.3's common failure mode
// against a densely connected graph.
MATCH (start:Person {name: "Alice"})-[:FOLLOWS*1..4]->(reached:Person)
RETURN DISTINCT reached.name AS reachablePerson;

// --- 3. shortestPath() — bidirectional BFS, not path enumeration -------
// "What is the shortest FOLLOWS chain between Alice and Carol?"
MATCH path = shortestPath(
    (a:Person {name: "Alice"})-[:FOLLOWS*]-(c:Person {name: "Carol"})
)
RETURN [n IN nodes(path) | n.name] AS chain, length(path) AS hops;

// --- 4. Two-hop co-purchase recommendation pattern (Section 4.3 scenario)
// "Products purchased by people who also purchased what this customer
// bought, excluding products the customer already owns." Anchored from
// both ends (me AND NOT already-purchased) to bound the search space,
// per Section 4.3's guidance on anchoring both ends of a pattern.
MATCH (me:Person {name: "Alice"})-[:PURCHASED]->(:Product)<-[:PURCHASED]-(other:Person)-[:PURCHASED]->(rec:Product)
WHERE NOT (me)-[:PURCHASED]->(rec)
RETURN rec.name AS recommendedProduct, count(*) AS strength
ORDER BY strength DESC
LIMIT 10;

// --- 5. Relationship-property traversal (Section 4.1's payoff) ---------
// Reads a relationship's own property (quantity) in the SAME step that
// follows the relationship — no join to a separate "order line" table.
MATCH (p:Person)-[purchase:PURCHASED]->(pr:Product)
RETURN p.name AS buyer, pr.name AS product, purchase.quantity AS quantity
ORDER BY buyer;
