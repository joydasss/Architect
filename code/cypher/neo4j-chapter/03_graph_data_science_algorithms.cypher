// Section 4.5 — Graph Data Science (GDS) library: pathfinding, centrality,
// and community detection. Demonstrates the mandatory in-memory-projection
// step (Section 4.5's common failure mode is skipping this and running an
// iterative algorithm directly against the transactional store).
// Requires the Neo4j Graph Data Science plugin to be installed.

// --- Step 1: project the relevant subgraph into memory ------------------
// Projects Person nodes and FOLLOWS relationships only — GDS algorithms
// run against this compact, algorithm-optimized copy, not the live
// disk-backed transactional store.
CALL gds.graph.project(
    'socialGraph',
    'Person',
    'FOLLOWS'
);

// --- 2. Pathfinding: Dijkstra shortest path -----------------------------
// Unlike Cypher's built-in shortestPath() (unweighted hop count), GDS
// Dijkstra supports weighted edges — here, a hypothetical "closeness"
// relationship-property weight, defaulting to 1.0 if absent.
MATCH (source:Person {name: "Alice"}), (target:Person {name: "Carol"})
CALL gds.shortestPath.dijkstra.stream('socialGraph', {
    sourceNode: source,
    targetNode: target,
    relationshipWeightProperty: null
})
YIELD totalCost, nodeIds
RETURN totalCost, [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS path;

// --- 3. Centrality: PageRank --------------------------------------------
// Iterative, whole-graph algorithm (Section 4.5's BSP-style execution
// model) — a node scores high if linked to by OTHER high-scoring nodes,
// not merely by many nodes (distinguishes it from raw in-degree).
CALL gds.pageRank.stream('socialGraph')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS person, score
ORDER BY score DESC;

// Write PageRank results back to the transactional graph as an ordinary
// node property, so the application can query it with plain Cypher
// (Section 4.5's "write results back" final step).
CALL gds.pageRank.write('socialGraph', {
    writeProperty: 'pagerankScore'
})
YIELD nodePropertiesWritten, ranIterations;

// --- 4. Community detection: Louvain modularity optimization ------------
// Fast, greedy, hierarchical heuristic (NOT an exhaustive/exact search —
// exact modularity optimization is NP-hard; Section 4.5's disclosed
// approximation trade-off).
CALL gds.louvain.stream('socialGraph')
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).name AS person, communityId
ORDER BY communityId;

// --- Cleanup: release the in-memory projection --------------------------
CALL gds.graph.drop('socialGraph');
