'use strict';

/**
 * Directory-based (shard-map) router referenced in CH06_Sharding.md Section
 * 4.3/4.6. Unlike algorithmic hash-mod routing, the mapping from key-range to
 * physical shard is explicit, persisted state, which is what makes live
 * rebalancing possible: moving a range is a metadata update plus a data copy,
 * not a global recomputation of every key's owner.
 */

class ShardMapRouter {
  constructor() {
    // Sorted list of { start, end, shardId } ranges over a hashed key-space
    // (0..2^32-1). Ranges are contiguous and non-overlapping by construction.
    this.ranges = [];
  }

  /** Bootstraps N equal ranges across the given shard IDs. */
  initializeEqualRanges(shardIds) {
    const SPACE = 2 ** 32;
    const step = Math.floor(SPACE / shardIds.length);
    this.ranges = shardIds.map((shardId, i) => ({
      start: i * step,
      end: i === shardIds.length - 1 ? SPACE - 1 : (i + 1) * step - 1,
      shardId,
    }));
  }

  hashKey(key) {
    // FNV-1a 32-bit: deterministic, fast, adequate distribution for routing.
    let hash = 0x811c9dc5;
    for (let i = 0; i < key.length; i += 1) {
      hash ^= key.charCodeAt(i);
      hash = Math.imul(hash, 0x01000193);
    }
    return hash >>> 0;
  }

  routeKey(key) {
    const position = this.hashKey(key);
    const range = this.ranges.find((r) => position >= r.start && position <= r.end);
    if (!range) throw new Error(`No shard owns hash position ${position}`);
    return range.shardId;
  }

  /**
   * Splits an overloaded shard's range in half and assigns the new half to
   * `newShardId`. This is the metadata-only step of live rebalancing —
   * the caller is still responsible for copying the affected rows before
   * traffic is cut over (see the dual-write migration example in
   * code/sql/sharding-chapter/rebalance_migration.sql).
   */
  splitRangeForRebalance(hotShardId, newShardId) {
    const idx = this.ranges.findIndex((r) => r.shardId === hotShardId);
    if (idx === -1) throw new Error(`Unknown shard ${hotShardId}`);
    const { start, end } = this.ranges[idx];
    const midpoint = start + Math.floor((end - start) / 2);

    const lowerHalf = { start, end: midpoint, shardId: hotShardId };
    const upperHalf = { start: midpoint + 1, end, shardId: newShardId };
    this.ranges.splice(idx, 1, lowerHalf, upperHalf);
    return { lowerHalf, upperHalf };
  }

  describeTopology() {
    return this.ranges.map((r) => `[${r.start}-${r.end}] -> ${r.shardId}`);
  }
}

function demo() {
  const router = new ShardMapRouter();
  router.initializeEqualRanges(['shard-1', 'shard-2', 'shard-3']);
  console.log('Initial topology:', router.describeTopology());

  const testKeys = ['tenant-042', 'tenant-999', 'tenant-777'];
  for (const key of testKeys) {
    console.log(`${key} -> ${router.routeKey(key)}`);
  }

  // shard-1 is hot (e.g. one large tenant) -> split its range onto a new shard.
  const split = router.splitRangeForRebalance('shard-1', 'shard-4');
  console.log('After splitting shard-1 for rebalance:', split);
  console.log('New topology:', router.describeTopology());
}

module.exports = { ShardMapRouter };

if (require.main === module) {
  demo();
}
