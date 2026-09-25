// Fencing-token failover example (CH07_Replication.md Section 4.8, 10).
// A monotonically increasing token guarantees a fenced-out old leader
// cannot successfully write to shared storage after a new leader is promoted.
package replication;

import java.util.concurrent.atomic.AtomicLong;

class FailoverFencingToken {

    /** Issues strictly increasing fencing tokens on each leader (re)election. */
    static final class FencingTokenAuthority {
        private final AtomicLong currentToken = new AtomicLong(0);

        long electNewLeader() {
            return currentToken.incrementAndGet();
        }
    }

    /** Shared storage layer that only accepts writes carrying the highest token it has seen. */
    static final class FencedStorage {
        private long highestTokenSeen = 0;
        private String value;

        synchronized boolean write(long token, String newValue) {
            if (token < highestTokenSeen) {
                return false; // stale leader - write rejected, split-brain averted
            }
            highestTokenSeen = token;
            value = newValue;
            return true;
        }

        synchronized String read() {
            return value;
        }
    }

    static final class DatabaseLeader {
        private final long fencingToken;
        private final FencedStorage storage;

        DatabaseLeader(long fencingToken, FencedStorage storage) {
            this.fencingToken = fencingToken;
            this.storage = storage;
        }

        boolean write(String data) {
            return storage.write(fencingToken, data);
        }
    }

    public static void main(String[] args) {
        FencingTokenAuthority authority = new FencingTokenAuthority();
        FencedStorage storage = new FencedStorage();

        long tokenA = authority.electNewLeader(); // token = 1
        DatabaseLeader leaderA = new DatabaseLeader(tokenA, storage);
        System.out.println("Leader A write succeeded: " + leaderA.write("order-101"));

        // Network partition: monitoring plane believes leaderA is dead and
        // promotes a new leader, but leaderA is still alive and unaware.
        long tokenB = authority.electNewLeader(); // token = 2
        DatabaseLeader leaderB = new DatabaseLeader(tokenB, storage);
        System.out.println("Leader B write succeeded: " + leaderB.write("order-101-corrected"));

        // The old leader (leaderA), still holding token=1, attempts a write
        // after the partition heals - this is exactly the split-brain scenario.
        boolean staleWriteAccepted = leaderA.write("order-101-STALE-OVERWRITE");
        System.out.println("Stale Leader A write succeeded (should be false): " + staleWriteAccepted);
        System.out.println("Final durable value: " + storage.read());
    }
}
