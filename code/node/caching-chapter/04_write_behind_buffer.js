'use strict';

/**
 * Write-behind (write-back) cache buffer.
 *
 * CH09_Caching.md Section 4.5: writes land in the cache and an in-memory
 * dirty buffer immediately (fast, low write latency), and a background
 * flush task periodically batches the buffer to the database. This
 * demonstrates both the throughput win and the durability-window risk:
 * data acknowledged to the caller but not yet flushed is lost if the
 * process crashes before the next flush cycle runs.
 *
 * Run directly: node 04_write_behind_buffer.js
 */

class FakeDatabase {
  constructor(latencyMs = 20) {
    this.rows = new Map();
    this.latencyMs = latencyMs;
    this.batchWriteCount = 0;
  }

  async batchUpsert(entries) {
    await new Promise((resolve) => setTimeout(resolve, this.latencyMs));
    for (const [key, value] of entries) {
      this.rows.set(key, value);
    }
    this.batchWriteCount += 1;
  }
}

class WriteBehindCache {
  constructor(db, { flushIntervalMs = 100 } = {}) {
    this.db = db;
    this.cache = new Map();
    this.dirty = new Map(); // key -> value, entries not yet flushed to the DB
    this.flushIntervalMs = flushIntervalMs;
    this.timer = null;
  }

  // Acknowledges the caller immediately; durability is deferred to the next flush.
  write(key, value) {
    this.cache.set(key, value);
    this.dirty.set(key, value);
  }

  read(key) {
    return this.cache.get(key);
  }

  async flush() {
    if (this.dirty.size === 0) return;
    const batch = Array.from(this.dirty.entries());
    this.dirty.clear();
    await this.db.batchUpsert(batch);
  }

  startBackgroundFlush() {
    this.timer = setInterval(() => {
      this.flush().catch((err) => console.error('flush failed:', err));
    }, this.flushIntervalMs);
    // Do not keep the Node.js process alive solely for this timer.
    this.timer.unref();
  }

  stopBackgroundFlush() {
    if (this.timer) clearInterval(this.timer);
  }

  // Simulates a crash: unflushed writes in `dirty` are gone, illustrating the
  // durability-window risk that write-behind trades for lower write latency.
  simulateCrashLosingUnflushedWrites() {
    const lostCount = this.dirty.size;
    this.dirty.clear();
    this.cache.clear();
    return lostCount;
  }
}

async function demo() {
  const db = new FakeDatabase();
  const wb = new WriteBehindCache(db, { flushIntervalMs: 50 });

  const start = Date.now();
  wb.write('session:42:cart', JSON.stringify({ items: 3 }));
  const writeLatencyMs = Date.now() - start;
  console.log(`Write acknowledged in ${writeLatencyMs} ms (before DB flush)`);
  console.log(`Read-your-own-write from cache immediately: ${wb.read('session:42:cart')}`);

  await wb.flush();
  console.log(`After explicit flush: db.rows has ${db.rows.size} row(s), batchWriteCount=${db.batchWriteCount}`);

  // Demonstrate the durability-window risk: write, then "crash" before a flush runs.
  wb.write('session:43:cart', JSON.stringify({ items: 1 }));
  const lost = wb.simulateCrashLosingUnflushedWrites();
  console.log(`Simulated crash before flush: lost ${lost} unflushed write(s) — the write-behind durability window`);
}

demo();
