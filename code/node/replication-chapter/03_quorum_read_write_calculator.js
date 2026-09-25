/**
 * Quorum read/write calculator + sloppy-quorum/hinted-handoff + read-repair demo.
 * CH07_Replication.md Section 4.7, 10.
 */
"use strict";

// Section 4.7 correctness rule: a read quorum and a write quorum are
// guaranteed to overlap on at least one node iff W + R > N.
function quorumOverlaps(n, w, r) {
  return w + r > n;
}

function describeQuorum(n, w, r) {
  return {
    n,
    w,
    r,
    guaranteesOverlap: quorumOverlaps(n, w, r),
    note: quorumOverlaps(n, w, r)
      ? "Every write quorum and read quorum share at least one node."
      : "No guaranteed overlap - reads may miss the most recent write.",
  };
}

// A tiny in-memory replica set, used to simulate sloppy quorum + hinted handoff + read repair.
class ReplicaSet {
  constructor(nodeNames) {
    this.nodes = new Map(nodeNames.map((name) => [name, new Map()]));
    this.hints = new Map(nodeNames.map((name) => [name, []])); // hinted handoff inbox per node
  }

  isReachable(name, downNodes) {
    return !downNodes.has(name);
  }

  // Writes to the first W reachable "home" nodes; if fewer than W home nodes
  // are reachable, falls back to substitute nodes (sloppy quorum) and stores
  // a hint so the write can later be forwarded to its real home node.
  write(key, value, version, homeNodes, w, downNodes, allNodeNames) {
    const acked = [];
    for (const name of homeNodes) {
      if (acked.length >= w) break;
      if (this.isReachable(name, downNodes)) {
        this.nodes.get(name).set(key, { value, version });
        acked.push(name);
      }
    }
    if (acked.length < w) {
      const substitutes = allNodeNames.filter(
        (n) => !homeNodes.includes(n) && this.isReachable(n, downNodes)
      );
      for (const sub of substitutes) {
        if (acked.length >= w) break;
        this.hints.get(sub).push({ key, value, version, intendedFor: homeNodes });
        acked.push(`${sub}(sloppy-hint)`);
      }
    }
    return { acked, satisfiedW: acked.length >= w };
  }

  // Delivers any hinted-handoff writes back to their intended home node once reachable again.
  deliverHints(homeNodes, downNodes) {
    for (const [holder, queued] of this.hints.entries()) {
      const remaining = [];
      for (const hint of queued) {
        const target = hint.intendedFor.find((n) => this.isReachable(n, downNodes));
        if (target) {
          this.nodes.get(target).set(hint.key, { value: hint.value, version: hint.version });
        } else {
          remaining.push(hint);
        }
      }
      this.hints.set(holder, remaining);
    }
  }

  // Reads from R nodes, reconciles by highest version, and performs read repair
  // on any node found holding a stale version.
  read(key, homeNodes, r, downNodes) {
    const responses = [];
    for (const name of homeNodes) {
      if (responses.length >= r) break;
      if (this.isReachable(name, downNodes)) {
        responses.push({ name, entry: this.nodes.get(name).get(key) });
      }
    }
    const withValue = responses.filter((r) => r.entry);
    if (withValue.length === 0) return { value: undefined, repaired: [] };

    const winner = withValue.reduce((best, cur) =>
      cur.entry.version > best.entry.version ? cur : best
    );
    const repaired = [];
    for (const r of withValue) {
      if (r.entry.version < winner.entry.version) {
        this.nodes.get(r.name).set(key, winner.entry);
        repaired.push(r.name);
      }
    }
    return { value: winner.entry.value, version: winner.entry.version, repaired };
  }
}

function demo() {
  console.log(describeQuorum(3, 2, 2)); // overlap guaranteed
  console.log(describeQuorum(3, 1, 1)); // "quorum theater" - no overlap guaranteed

  const homeNodes = ["nodeA", "nodeB", "nodeC"];
  const rs = new ReplicaSet(homeNodes);

  // nodeB is down; write with W=2 falls back to a sloppy-quorum substitute is
  // unnecessary here since nodeA+nodeC still satisfy W=2 directly.
  const down = new Set(["nodeB"]);
  const writeResult = rs.write("cart:42", { items: ["sku-1"] }, 1, homeNodes, 2, down, [
    ...homeNodes,
    "nodeD",
  ]);
  console.log("write result:", writeResult);

  // nodeB comes back but missed the write; a read with R=2 should detect the
  // stale replica and trigger read repair.
  const readResult = rs.read("cart:42", homeNodes, 2, new Set());
  console.log("read result (before nodeB catches up):", readResult);
}

demo();

module.exports = { quorumOverlaps, describeQuorum, ReplicaSet };
