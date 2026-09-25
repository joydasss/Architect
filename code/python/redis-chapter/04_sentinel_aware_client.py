"""Demonstrates a Sentinel-aware client that discovers the current primary
dynamically and re-resolves it after a failover, per Section 4.5
(CH16_Redis.md).

Requires: pip install redis
Requires a reachable Sentinel deployment. Example docker-compose topology:
  3 Sentinel processes watching one primary + N replicas, service name
  "mymaster" (Sentinel's default example name).
"""
import time
import redis
from redis.sentinel import Sentinel

SENTINEL_HOSTS = [
    ("localhost", 26379),
    ("localhost", 26380),
    ("localhost", 26381),
]
SERVICE_NAME = "mymaster"


def resolve_and_write(sentinel: Sentinel, key: str, value: str):
    """Always re-resolves the primary through Sentinel before writing -
    never caches a raw connection to a primary address across calls."""
    primary = sentinel.master_for(SERVICE_NAME, socket_timeout=1.0, decode_responses=True)
    primary.set(key, value)
    address = sentinel.discover_master(SERVICE_NAME)
    print(f"Wrote {key}={value} via primary at {address[0]}:{address[1]}")
    return address


def resolve_and_read_from_replica(sentinel: Sentinel, key: str):
    replica = sentinel.slave_for(SERVICE_NAME, socket_timeout=1.0, decode_responses=True)
    value = replica.get(key)
    print(f"Read {key}={value} via a replica")
    return value


def main():
    sentinel = Sentinel(SENTINEL_HOSTS, socket_timeout=1.0)

    print("--- Discovering current primary/replicas via Sentinel ---")
    try:
        master_address = sentinel.discover_master(SERVICE_NAME)
        replica_addresses = sentinel.discover_slaves(SERVICE_NAME)
    except redis.exceptions.ConnectionError as exc:
        print(f"(no reachable Sentinel deployment - exiting demo: {exc})")
        return

    print(f"Current primary: {master_address}")
    print(f"Known replicas : {replica_addresses}")

    last_address = resolve_and_write(sentinel, "demo:key", "value-before-failover")
    resolve_and_read_from_replica(sentinel, "demo:key")

    print("\n--- Simulating operator-triggered failover ---")
    print("(run: redis-cli -p <sentinel-port> SENTINEL failover mymaster)")
    print("Polling for the primary address to change (up to 30s)...")

    for _ in range(30):
        time.sleep(1)
        current_address = sentinel.discover_master(SERVICE_NAME)
        if current_address != last_address:
            print(f"Primary changed: {last_address} -> {current_address}")
            resolve_and_write(sentinel, "demo:key", "value-after-failover")
            break
    else:
        print("No failover observed in the poll window (expected if none was triggered).")


if __name__ == "__main__":
    main()
