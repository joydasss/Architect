/**
 * 04_TokenRingRoutingSimulation.java
 *
 * Self-contained simulation of Cassandra's consistent-hashing token ring
 * with virtual nodes (vnodes): assigns tokens to physical nodes, routes a
 * partition key to its owning replicas via token-aware routing, and models
 * the phi-accrual-style suspicion scoring gossip uses to distinguish a
 * slow node from a dead one. No external driver dependency -- compiles and
 * runs with a plain JDK. See CH18_Cassandra.md Sections 4.1 and 4.3.
 *
 * Compile: javac 04_TokenRingRoutingSimulation.java
 * Run:     java TokenRingRoutingSimulation
 */

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

class TokenRingRoutingSimulation {

    /** One physical node contributing several virtual-node tokens to the ring. */
    static final class PhysicalNode {
        final String nodeId;
        final String datacenter;
        double heartbeatIntervalHistoryMean = 1000.0; // ms, gossip round-trip baseline
        long lastHeartbeatAt;
        boolean alive = true;

        PhysicalNode(String nodeId, String datacenter) {
            this.nodeId = nodeId;
            this.datacenter = datacenter;
            this.lastHeartbeatAt = System.currentTimeMillis();
        }
    }

    /**
     * The token ring: a sorted map from token -> owning physical node.
     * Each physical node owns `vnodesPerNode` tokens scattered around the
     * ring (default historically 256, tuned down to 16 in newer versions
     * to reduce streaming/repair overhead per Section 4.1's mechanism
     * explanation) instead of one contiguous range -- this is what bounds
     * rebalancing cost to roughly 1/N of the data on node add/remove,
     * instead of one node inheriting an entire neighbor's full range.
     */
    static final class TokenRing {
        final TreeMap<Long, PhysicalNode> ring = new TreeMap<>();
        final int vnodesPerNode;

        TokenRing(int vnodesPerNode) {
            this.vnodesPerNode = vnodesPerNode;
        }

        void addNode(PhysicalNode node, long seed) {
            // Deterministic pseudo-random token placement, standing in for
            // Cassandra's actual token-allocation algorithm.
            long token = seed;
            for (int v = 0; v < vnodesPerNode; v++) {
                token = nextToken(token);
                ring.put(token, node);
            }
        }

        private static long nextToken(long previous) {
            // Simple linear-congruential step -- deterministic and
            // reproducible for this demo, not cryptographically anything.
            return (previous * 6364136223846793005L + 1442695040888963407L);
        }

        /** Murmur3-style partitioner stand-in: hash a key to a token. */
        static long tokenForKey(String partitionKey) {
            long h = 1125899906842597L;
            for (int i = 0; i < partitionKey.length(); i++) {
                h = 31 * h + partitionKey.charAt(i);
            }
            return h;
        }

        /**
         * Token-aware routing: walk the ring clockwise from the key's token
         * to find the first vnode >= that token; that vnode's owning node
         * is the first replica. The next `replicationFactor - 1` DISTINCT
         * physical nodes encountered continuing clockwise are the
         * remaining replicas -- this is exactly what a token-aware client
         * driver precomputes so it can route a request directly to a
         * replica, skipping an extra coordinator hop (Section 4.1).
         */
        List<PhysicalNode> replicasForKey(String partitionKey, int replicationFactor) {
            long token = tokenForKey(partitionKey);
            List<PhysicalNode> replicas = new ArrayList<>();
            Map.Entry<Long, PhysicalNode> entry = ring.ceilingEntry(token);
            if (entry == null) {
                entry = ring.firstEntry(); // wrap around the ring
            }
            Long startKey = entry.getKey();
            Long cursor = startKey;
            do {
                PhysicalNode candidate = ring.get(cursor);
                if (!replicas.contains(candidate)) {
                    replicas.add(candidate);
                }
                Map.Entry<Long, PhysicalNode> next = ring.higherEntry(cursor);
                cursor = (next != null) ? next.getKey() : ring.firstKey();
            } while (replicas.size() < replicationFactor && !cursor.equals(startKey));
            return replicas;
        }
    }

    /**
     * Phi Accrual failure detector (Section 4.3): rather than a binary
     * alive/dead threshold, gossip tracks the distribution of recent
     * heartbeat inter-arrival times and computes a continuous suspicion
     * level (phi). A high phi means "this silence is now statistically
     * very unlikely for a healthy node," which lets each node set its own
     * effective timeout adaptively instead of one fixed global timeout
     * that is either too twitchy on a slow WAN link or too slow on a
     * healthy LAN link.
     */
    static double phiSuspicionLevel(PhysicalNode node, long nowMillis) {
        double elapsed = nowMillis - node.lastHeartbeatAt;
        double mean = node.heartbeatIntervalHistoryMean;
        if (elapsed <= 0) {
            return 0.0;
        }
        // Simplified exponential-distribution-based phi approximation:
        // phi grows the further "elapsed" exceeds the historical mean.
        double ratio = elapsed / mean;
        return ratio <= 1.0 ? 0.0 : Math.log10(ratio) * 8.0;
    }

    public static void main(String[] args) {
        TokenRing ring = new TokenRing(16); // 16 vnodes/node, modern default
        PhysicalNode n1 = new PhysicalNode("10.0.1.1", "dc1");
        PhysicalNode n2 = new PhysicalNode("10.0.1.2", "dc1");
        PhysicalNode n3 = new PhysicalNode("10.0.1.3", "dc1");
        ring.addNode(n1, 11L);
        ring.addNode(n2, 22L);
        ring.addNode(n3, 33L);

        System.out.println("=== Token-aware routing for 3 partition keys, RF=3 ===");
        for (String key : new String[]{"customer-1042", "customer-8873", "order-55219"}) {
            List<PhysicalNode> replicas = ring.replicasForKey(key, 3);
            StringBuilder sb = new StringBuilder();
            for (PhysicalNode r : replicas) {
                sb.append(r.nodeId).append(" ");
            }
            System.out.println("key=" + key + " -> replicas=[" + sb.toString().trim() + "]");
        }

        System.out.println("\n=== Phi Accrual suspicion after a gossip silence ===");
        long now = System.currentTimeMillis();
        n2.lastHeartbeatAt = now - 1200; // node-2 healthy: 1.2s since last heartbeat
        n3.lastHeartbeatAt = now - 15000; // node-3 suspicious: 15s of silence
        System.out.printf("node-2 phi=%.2f (below suspicion threshold, still UP)%n",
                phiSuspicionLevel(n2, now));
        System.out.printf("node-3 phi=%.2f (exceeds typical threshold ~8-12, marked DOWN)%n",
                phiSuspicionLevel(n3, now));
    }
}
