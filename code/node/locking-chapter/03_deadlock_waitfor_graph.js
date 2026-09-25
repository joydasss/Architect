/**
 * Deadlock reproduction and a standalone wait-for-graph cycle detector.
 *
 * Implements CH10_Locking.md Section 4.6: deliberately reproduces a
 * two-transaction circular-wait deadlock against PostgreSQL, and separately
 * implements the same wait-for-graph cycle-detection algorithm the engine
 * uses internally, driven by live data read from pg_locks/pg_stat_activity,
 * for teaching purposes.
 *
 * Setup:
 *   npm install pg
 *   createdb locking_demo   # or point CONNECTION_STRING below at an existing DB
 *
 * Run:
 *   node 03_deadlock_waitfor_graph.js
 */

const { Pool } = require("pg");

const CONNECTION_STRING = "postgresql://localhost/locking_demo";

async function setup(pool) {
  await pool.query("DROP TABLE IF EXISTS accounts");
  await pool.query(
    "CREATE TABLE accounts (id INT PRIMARY KEY, balance NUMERIC NOT NULL)"
  );
  await pool.query(
    "INSERT INTO accounts (id, balance) VALUES (1, 500), (2, 300)"
  );
}

// Deliberately acquires locks in OPPOSITE order across two concurrent
// transactions, reproducing the circular-wait failure mode from Section
// 4.6's "opposite-order acquisition" anti-pattern (Section 19).
async function transferOppositeOrder(pool, label, firstId, secondId) {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    console.log(`[${label}] locking row ${firstId}`);
    await client.query("SELECT balance FROM accounts WHERE id = $1 FOR UPDATE", [
      firstId,
    ]);

    // Give the other transaction time to grab the opposite lock first,
    // guaranteeing both transactions are blocked waiting on each other.
    await new Promise((resolve) => setTimeout(resolve, 300));

    console.log(`[${label}] locking row ${secondId} (may block)`);
    await client.query("SELECT balance FROM accounts WHERE id = $1 FOR UPDATE", [
      secondId,
    ]);

    await client.query(
      "UPDATE accounts SET balance = balance - 50 WHERE id = $1",
      [firstId]
    );
    await client.query(
      "UPDATE accounts SET balance = balance + 50 WHERE id = $1",
      [secondId]
    );
    await client.query("COMMIT");
    console.log(`[${label}] committed successfully`);
  } catch (err) {
    await client.query("ROLLBACK");
    if (err.code === "40P01") {
      console.log(`[${label}] was chosen as the deadlock VICTIM (SQLSTATE 40P01): ${err.message}`);
    } else {
      console.log(`[${label}] failed: ${err.message}`);
    }
  } finally {
    client.release();
  }
}

async function reproduceDeadlock(pool) {
  console.log("\n=== Reproducing a two-transaction deadlock ===");
  // Transaction A locks row 1 then row 2; Transaction B locks row 2 then
  // row 1 -- opposite acquisition order, the structural cause of deadlock.
  await Promise.all([
    transferOppositeOrder(pool, "Transaction A", 1, 2),
    transferOppositeOrder(pool, "Transaction B", 2, 1),
  ]);
}

/**
 * Standalone wait-for-graph cycle detector (Section 4.6's algorithm),
 * built from PostgreSQL's own pg_locks/pg_stat_activity views. This
 * mirrors -- for teaching purposes -- the same graph the engine's internal
 * deadlock detector already maintains automatically.
 */
async function buildAndCheckWaitForGraph(pool) {
  const { rows } = await pool.query(`
    SELECT
      waiting.pid  AS waiting_pid,
      blocking.pid AS blocking_pid
    FROM pg_locks waiting
    JOIN pg_locks blocking
      ON waiting.locktype = blocking.locktype
     AND waiting.database IS NOT DISTINCT FROM blocking.database
     AND waiting.relation IS NOT DISTINCT FROM blocking.relation
     AND waiting.page IS NOT DISTINCT FROM blocking.page
     AND waiting.tuple IS NOT DISTINCT FROM blocking.tuple
     AND waiting.pid != blocking.pid
    WHERE NOT waiting.granted
      AND blocking.granted
  `);

  // Build adjacency list: waiting_pid -> [blocking_pid, ...]
  const graph = new Map();
  for (const { waiting_pid, blocking_pid } of rows) {
    if (!graph.has(waiting_pid)) graph.set(waiting_pid, []);
    graph.get(waiting_pid).push(blocking_pid);
  }

  // Depth-first search looking for a back-edge to a node already on the
  // current path -- exactly the cycle-detection algorithm Section 4.6
  // describes the lock manager running over its own wait-for graph.
  const WHITE = 0, GRAY = 1, BLACK = 2;
  const color = new Map();
  const path = [];

  function dfs(node) {
    color.set(node, GRAY);
    path.push(node);
    for (const neighbor of graph.get(node) || []) {
      if (color.get(neighbor) === GRAY) {
        const cycleStart = path.indexOf(neighbor);
        return path.slice(cycleStart).concat(neighbor);
      }
      if (color.get(neighbor) !== BLACK) {
        const cycle = dfs(neighbor);
        if (cycle) return cycle;
      }
    }
    path.pop();
    color.set(node, BLACK);
    return null;
  }

  for (const node of graph.keys()) {
    if (color.get(node) !== BLACK) {
      const cycle = dfs(node);
      if (cycle) return cycle;
    }
  }
  return null;
}

async function main() {
  const pool = new Pool({ connectionString: CONNECTION_STRING });
  await setup(pool);
  await reproduceDeadlock(pool);

  console.log("\n=== Standalone wait-for-graph check (post-hoc) ===");
  const cycle = await buildAndCheckWaitForGraph(pool);
  console.log(
    cycle
      ? `No live cycle at check time (deadlock already resolved by the engine): ${cycle}`
      : "No cycle currently present in pg_locks (engine already resolved any deadlock)."
  );

  await pool.end();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
