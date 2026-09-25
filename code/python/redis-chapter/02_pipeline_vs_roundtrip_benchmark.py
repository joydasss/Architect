"""Benchmarks N individual round trips vs. one pipelined batch of N commands,
making Section 4.1's single-threaded/one-round-trip-per-command cost concrete
(CH16_Redis.md, Section 9 - Implementation).

Requires: pip install redis
Requires a reachable Redis server (default: localhost:6379).
"""
import time
import redis


def benchmark_individual_roundtrips(r, count):
    start = time.perf_counter()
    for i in range(count):
        r.set(f"bench:individual:{i}", i)
    return time.perf_counter() - start


def benchmark_pipelined(r, count):
    start = time.perf_counter()
    pipe = r.pipeline(transaction=False)
    for i in range(count):
        pipe.set(f"bench:pipelined:{i}", i)
    pipe.execute()
    return time.perf_counter() - start


def main():
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    r.flushdb()

    for count in (100, 1000, 5000):
        individual_seconds = benchmark_individual_roundtrips(r, count)
        pipelined_seconds = benchmark_pipelined(r, count)
        speedup = individual_seconds / pipelined_seconds if pipelined_seconds else float("inf")

        print(f"\n--- Batch size: {count} SET commands ---")
        print(f"Individual round trips : {individual_seconds * 1000:9.2f} ms "
              f"({individual_seconds / count * 1e6:7.1f} us/command)")
        print(f"Pipelined single batch  : {pipelined_seconds * 1000:9.2f} ms "
              f"({pipelined_seconds / count * 1e6:7.1f} us/command)")
        print(f"Speedup from pipelining : {speedup:5.1f}x")

    print("\nExecution itself is still single-threaded and fast (Section 4.1) —")
    print("the speedup here comes entirely from amortizing network round-trip")
    print("latency across the batch, not from parallel command execution.")


if __name__ == "__main__":
    main()
