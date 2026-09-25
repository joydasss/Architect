"""Exercises Redis's core data structures and times each command family,
annotated against Section 4.2's Big-O complexity table (CH16_Redis.md).

Requires: pip install redis
Requires a reachable Redis server (default: localhost:6379).
"""
import time
import redis


def timed(label, complexity, fn):
    start = time.perf_counter()
    result = fn()
    elapsed_ms = (time.perf_counter() - start) * 1000
    print(f"{label:<32} [{complexity:<12}] {elapsed_ms:8.3f} ms  -> {result!r}")
    return result


def main():
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    r.flushdb()

    # --- String: O(1) point ops ---
    timed("SET string", "O(1)", lambda: r.set("greeting", "hello"))
    timed("GET string", "O(1)", lambda: r.get("greeting"))
    timed("INCR counter", "O(1)", lambda: r.incr("visits"))

    # --- Hash: O(1) point ops, O(N) full-scan ---
    r.hset("user:42", mapping={"name": "Alice", "age": "30", "plan": "pro"})
    timed("HGET one field", "O(1)", lambda: r.hget("user:42", "name"))
    timed("HGETALL (N fields)", "O(N)", lambda: r.hgetall("user:42"))

    # --- List: O(1) push/pop at ends, O(S+N) range ---
    for i in range(1000):
        r.rpush("recent_events", f"event:{i}")
    timed("LPUSH one element", "O(1)", lambda: r.lpush("recent_events", "event:new"))
    timed("LRANGE last 10", "O(S+N)", lambda: r.lrange("recent_events", 0, 9))

    # --- Set: O(1) point ops, O(N) full-scan ---
    for i in range(1000):
        r.sadd("tags", f"tag:{i}")
    timed("SISMEMBER", "O(1)", lambda: r.sismember("tags", "tag:500"))
    timed("SMEMBERS (N members)", "O(N)", lambda: len(r.smembers("tags")))

    # --- Sorted Set: O(log N) insert/rank, O(log N + M) range ---
    for i in range(1000):
        r.zadd("leaderboard", {f"player:{i}": i})
    timed("ZADD", "O(log N)", lambda: r.zadd("leaderboard", {"player:new": 999}))
    timed("ZRANK (point lookup)", "O(log N)", lambda: r.zrank("leaderboard", "player:500"))
    timed("ZRANGE top 10", "O(log N + M)", lambda: r.zrevrange("leaderboard", 0, 9))

    # --- Stream: O(1) amortized append, O(log N + M) range read ---
    for i in range(100):
        r.xadd("orders_stream", {"order_id": i, "status": "created"})
    timed("XADD", "O(1) amortized", lambda: r.xadd("orders_stream", {"order_id": 999}))
    timed("XRANGE (M entries)", "O(log N + M)", lambda: r.xrange("orders_stream", count=10))

    # --- HyperLogLog: O(1) add, O(1) single-key count ---
    for i in range(5000):
        r.pfadd("unique_visitors", f"user:{i}")
    timed("PFADD", "O(1)", lambda: r.pfadd("unique_visitors", "user:new"))
    timed("PFCOUNT (estimate)", "O(1)", lambda: r.pfcount("unique_visitors"))

    # --- Bitmap: O(1) bit ops, O(N) range ops ---
    for i in range(0, 10000, 3):
        r.setbit("active_days", i, 1)
    timed("SETBIT", "O(1)", lambda: r.setbit("active_days", 10001, 1))
    timed("BITCOUNT (byte range)", "O(N)", lambda: r.bitcount("active_days"))

    print("\nNote: HyperLogLog PFCOUNT is an estimate, not an exact cardinality —")
    print(f"5001 adds -> estimated {r.pfcount('unique_visitors')} unique elements.")


if __name__ == "__main__":
    main()
