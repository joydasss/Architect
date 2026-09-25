package denormalization;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Precomputed-aggregate counter cache for a "likes per post" read path.
 *
 * Referenced from 06_Databases_and_Storage/CH02_Denormalization.md (Section 10).
 *
 * The normalized source of truth is a {@code likes} table (one row per
 * like), from which "how many likes does post X have" would otherwise
 * require {@code COUNT(*) WHERE post_id = X} on every read. This class
 * models the denormalized alternative: a precomputed counter, updated
 * write-side, so the read path is an O(1) lookup instead of an aggregation
 * query — the classic write-amplification-for-read-speed trade discussed in
 * Section 4.7 of the chapter.
 */
public final class DenormalizedCounterCache {

    /** Precomputed like-count per post; this is the denormalized artifact. */
    private final Map<Long, AtomicLong> likeCountsByPostId = new ConcurrentHashMap<>();

    /**
     * Write-through update: called from the same transaction/handler that
     * inserts the normalized {@code likes} row, keeping the two in sync.
     *
     * <p>If this increment is applied but the underlying like-row insert
     * later fails or rolls back, the counter drifts from the source of
     * truth — see the reconciliation-job failure mode in Section 15.
     */
    public long recordLike(long postId) {
        return likeCountsByPostId
                .computeIfAbsent(postId, id -> new AtomicLong(0))
                .incrementAndGet();
    }

    public long recordUnlike(long postId) {
        AtomicLong counter = likeCountsByPostId.get(postId);
        if (counter == null) {
            return 0L;
        }
        // Never let a race decrement a counter below zero (defensive floor).
        return counter.updateAndGet(current -> Math.max(0, current - 1));
    }

    /** O(1) read — no aggregation query against the normalized likes table. */
    public long getLikeCount(long postId) {
        AtomicLong counter = likeCountsByPostId.get(postId);
        return counter == null ? 0L : counter.get();
    }

    /**
     * Reconciliation pass: recomputes a counter from the normalized source
     * of truth and overwrites the cached value, correcting any drift caused
     * by partial failures, crashes between the two writes, or manual data
     * fixes applied directly against the {@code likes} table.
     */
    public void reconcile(long postId, long trueCountFromSourceOfTruth) {
        likeCountsByPostId
                .computeIfAbsent(postId, id -> new AtomicLong(0))
                .set(trueCountFromSourceOfTruth);
    }

    public static void main(String[] args) {
        DenormalizedCounterCache cache = new DenormalizedCounterCache();
        cache.recordLike(42L);
        cache.recordLike(42L);
        cache.recordLike(42L);
        cache.recordUnlike(42L);
        System.out.println("Post 42 like count (denormalized read): " + cache.getLikeCount(42L));

        // Simulate detected drift (e.g. a nightly reconciliation job comparing
        // against SELECT COUNT(*) FROM likes WHERE post_id = 42) and correct it.
        cache.reconcile(42L, 5L);
        System.out.println("Post 42 like count (after reconciliation): " + cache.getLikeCount(42L));
    }
}
