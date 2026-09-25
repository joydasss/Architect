// Section 4.7 — Decision framework in code: the same "find every manager
// in this employee's full reporting chain, regardless of depth" query,
// expressed as a bounded-depth Cypher variable-length traversal, with the
// equivalent relational recursive CTE inlined as a comment for side-by-side
// comparison.
//
// --- Relational equivalent (PostgreSQL-style recursive CTE) -------------
// WITH RECURSIVE reporting_chain AS (
//     SELECT employee_id, manager_id, 1 AS depth
//     FROM employees
//     WHERE employee_id = $employeeId
//     UNION ALL
//     SELECT e.employee_id, e.manager_id, rc.depth + 1
//     FROM employees e
//     JOIN reporting_chain rc ON e.employee_id = rc.manager_id
//     WHERE rc.depth < 10   -- depth guard, otherwise unbounded recursion
// )
// SELECT * FROM reporting_chain;
//
// Cost note (Section 4.2/4.7): each recursive level above re-executes an
// O(log n) index lookup against the employees table's primary-key/foreign-
// key index. The Cypher traversal below performs an O(1) pointer chase per
// hop instead, via index-free adjacency, regardless of total node count.

// --- Graph-native equivalent (Cypher) ------------------------------------
MATCH (employee:Person {personId: $employeeId})-[:REPORTS_TO*1..10]->(manager:Person)
RETURN manager.name AS managerInChain, manager.personId AS managerId;

// --- Unbounded-depth variant: "full chain to the top, whatever its length"
// Still bounded (here *1..20) per Section 4.3's common-failure-mode
// guidance — an organization's reporting depth is finite in practice, and
// an explicit upper bound protects against a data-entry cycle (a REPORTS_TO
// loop) turning the traversal into a runaway query.
MATCH (employee:Person {personId: $employeeId})-[:REPORTS_TO*1..20]->(topOfChain:Person)
WHERE NOT (topOfChain)-[:REPORTS_TO]->()
RETURN topOfChain.name AS ultimateManager;
