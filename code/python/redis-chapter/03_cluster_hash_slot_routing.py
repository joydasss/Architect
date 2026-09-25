"""Implements Redis Cluster's CRC16-mod-16384 slot function from scratch and
demonstrates hash-tag-forced co-location, per Section 4.4 (CH16_Redis.md).

Standalone CRC16 slot computation needs no dependencies. The optional
RedisCluster section requires: pip install redis
and a reachable Redis Cluster (set CLUSTER_STARTUP_NODES below).
"""
import re

# CRC16/CCITT-FALSE lookup table, the exact variant Redis Cluster uses.
_CRC16_TABLE = None


def _build_crc16_table():
    table = []
    for byte in range(256):
        crc = byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
        table.append(crc)
    return table


def crc16(data: bytes) -> int:
    global _CRC16_TABLE
    if _CRC16_TABLE is None:
        _CRC16_TABLE = _build_crc16_table()
    crc = 0
    for byte in data:
        crc = ((crc << 8) & 0xFFFF) ^ _CRC16_TABLE[((crc >> 8) ^ byte) & 0xFF]
    return crc


_HASH_TAG_PATTERN = re.compile(r"\{(.+?)\}")


def key_for_slot_computation(key: str) -> str:
    """Redis Cluster hashes only the substring inside {} if present (hash tag)."""
    match = _HASH_TAG_PATTERN.search(key)
    if match and match.group(1):
        return match.group(1)
    return key


def cluster_slot(key: str) -> int:
    """Section 4.4: slot = CRC16(key) mod 16384."""
    hashed_part = key_for_slot_computation(key)
    return crc16(hashed_part.encode("utf-8")) % 16384


def demo_slot_computation():
    print("--- Plain keys: independent slots ---")
    for key in ("user:42:profile", "user:42:sessions", "user:99:profile"):
        print(f"{key:<24} -> slot {cluster_slot(key)}")

    print("\n--- Hash-tagged keys: forced to the same slot ---")
    for key in ("{user:42}:profile", "{user:42}:sessions", "{user:42}:cart"):
        print(f"{key:<24} -> slot {cluster_slot(key)}")

    tagged_a = cluster_slot("{user:42}:profile")
    tagged_b = cluster_slot("{user:42}:sessions")
    assert tagged_a == tagged_b, "hash-tagged keys must land on the same slot"
    print(f"\nConfirmed: both hash-tagged keys map to slot {tagged_a} "
          "(safe for a multi-key Lua script or MULTI/EXEC transaction).")


CLUSTER_STARTUP_NODES = [
    {"host": "localhost", "port": "7000"},
    {"host": "localhost", "port": "7001"},
    {"host": "localhost", "port": "7002"},
]


def demo_live_cluster_routing():
    """Optional: connects to a real Redis Cluster and prints MOVED-resolved
    node ownership per key. Skips gracefully if no cluster is reachable."""
    try:
        from redis.cluster import RedisCluster
    except ImportError:
        print("\n(redis-py not installed - skipping live cluster demo)")
        return

    try:
        rc = RedisCluster(startup_nodes=CLUSTER_STARTUP_NODES, decode_responses=True)
        rc.ping()
    except Exception as exc:  # pragma: no cover - environment dependent
        print(f"\n(no reachable Redis Cluster - skipping live demo: {exc})")
        return

    print("\n--- Live cluster: node ownership per key ---")
    for key in ("user:42:profile", "{user:42}:sessions", "user:99:profile"):
        node = rc.get_node_from_key(key)
        print(f"{key:<24} -> slot {cluster_slot(key):5d} -> node {node.host}:{node.port}")


if __name__ == "__main__":
    demo_slot_computation()
    demo_live_cluster_routing()
