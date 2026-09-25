package sharding;

import java.util.List;
import java.util.Map;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.concurrent.*;
import java.util.function.Function;

/**
 * Scatter-gather aggregator for cross-shard queries (CH06_Sharding.md Section
 * 4.7/4.8). Fans a query out to every shard concurrently, applies a per-shard
 * timeout so one slow/unreachable shard can't block the whole request
 * indefinitely, and merges results while tracking which shards responded --
 * because a cross-shard query is only ever as consistent as its slowest or
 * most-failed participant, callers must decide up front whether a partial
 * result is acceptable for the given use case.
 */
public class ScatterGatherAggregator {

    public static final class ShardResult<T> {
        public final String shardId;
        public final List<T> rows;
        public final boolean timedOut;
        public final Exception error;

        ShardResult(String shardId, List<T> rows, boolean timedOut, Exception error) {
            this.shardId = shardId;
            this.rows = rows;
            this.timedOut = timedOut;
            this.error = error;
        }
    }

    public static final class AggregatedResponse<T> {
        public final List<T> mergedRows;
        public final List<String> failedShards;
        public final boolean isPartial;

        AggregatedResponse(List<T> mergedRows, List<String> failedShards) {
            this.mergedRows = mergedRows;
            this.failedShards = failedShards;
            this.isPartial = !failedShards.isEmpty();
        }
    }

    private final ExecutorService executor;
    private final long perShardTimeoutMillis;

    public ScatterGatherAggregator(int parallelism, long perShardTimeoutMillis) {
        this.executor = Executors.newFixedThreadPool(parallelism);
        this.perShardTimeoutMillis = perShardTimeoutMillis;
    }

    /**
     * @param shardIds     every shard that must be queried (scatter phase)
     * @param queryPerShard a function issuing the same logical query against one shard's connection
     */
    public <T> AggregatedResponse<T> query(List<String> shardIds,
                                            Function<String, List<T>> queryPerShard) {
        Map<String, Future<List<T>>> inFlight = new HashMap<>();
        for (String shardId : shardIds) {
            inFlight.put(shardId, executor.submit(() -> queryPerShard.apply(shardId)));
        }

        List<T> merged = new ArrayList<>();
        List<String> failedShards = new ArrayList<>();

        for (Map.Entry<String, Future<List<T>>> entry : inFlight.entrySet()) {
            String shardId = entry.getKey();
            try {
                List<T> rows = entry.getValue().get(perShardTimeoutMillis, TimeUnit.MILLISECONDS);
                merged.addAll(rows);
            } catch (TimeoutException e) {
                entry.getValue().cancel(true);
                failedShards.add(shardId); // gather phase: degrade to partial result, don't block forever
            } catch (InterruptedException | ExecutionException e) {
                failedShards.add(shardId);
            }
        }

        return new AggregatedResponse<>(merged, failedShards);
    }

    public void shutdown() {
        executor.shutdown();
    }

    // --- Example usage (simulated shard latencies, one shard intentionally slow) ---
    public static void main(String[] args) throws Exception {
        ScatterGatherAggregator aggregator = new ScatterGatherAggregator(8, 200);

        List<String> shards = List.of("shard-1", "shard-2", "shard-3", "shard-4");
        AggregatedResponse<String> response = aggregator.query(shards, shardId -> {
            try {
                long simulatedLatencyMs = shardId.equals("shard-3") ? 500 : 30; // shard-3 is the straggler
                Thread.sleep(simulatedLatencyMs);
            } catch (InterruptedException ignored) {
                Thread.currentThread().interrupt();
            }
            return List.of(shardId + ":row-A", shardId + ":row-B");
        });

        System.out.println("Merged rows: " + response.mergedRows);
        System.out.println("Failed/timed-out shards: " + response.failedShards);
        System.out.println("Result is partial: " + response.isPartial);

        aggregator.shutdown();
    }
}
