"""Vector store capacity and cost sizing calculator (standard library only).

Estimates raw vector bytes, HNSW graph overhead, quantization savings,
replicas, and node counts for RAM-resident and SSD-resident deployments.
All constants are illustrative defaults; replace them with measured values.
"""

from math import ceil

GIB = 1024 ** 3


def raw_bytes(n, dim, bytes_per_dim):
    return n * dim * bytes_per_dim


def hnsw_graph_bytes(n, m, id_bytes=4, layer0_factor=2.0, upper_factor=0.07):
    """Graph links: layer 0 holds up to 2*M links per node, upper layers add a few percent."""
    layer0 = n * layer0_factor * m * id_bytes
    return layer0 * (1.0 + upper_factor)


def size(n, dim, m=16, vector_bytes=4.0, rescore_float32_on_disk=False,
         metadata_bytes=300, replicas=2, headroom=0.30, node_ram_gib=64,
         ram_fraction_for_index=0.70):
    vec = raw_bytes(n, dim, vector_bytes)
    graph = hnsw_graph_bytes(n, m)
    meta = n * metadata_bytes
    hot = vec + graph  # what should sit in RAM for low latency
    originals = raw_bytes(n, dim, 4.0) if rescore_float32_on_disk else 0
    hot_with_headroom = hot * (1.0 + headroom)
    usable = node_ram_gib * GIB * ram_fraction_for_index
    shards = max(1, ceil(hot_with_headroom / usable))
    nodes = shards * replicas
    return {
        "vectors_gib": vec / GIB,
        "graph_gib": graph / GIB,
        "metadata_gib": meta / GIB,
        "hot_gib": hot / GIB,
        "originals_on_ssd_gib": originals / GIB,
        "hot_with_headroom_gib": hot_with_headroom / GIB,
        "shards": shards,
        "nodes": nodes,
    }


def show(title, r):
    print(f"--- {title}")
    for k, v in r.items():
        print(f"  {k:24s} {v:10.2f}" if isinstance(v, float) else f"  {k:24s} {v:10d}")


def qps_nodes(target_qps, per_replica_qps, shards, headroom=0.5):
    """Replica groups needed so each runs at <= (1 - headroom) of its measured limit."""
    usable = per_replica_qps * (1.0 - headroom)
    return ceil(target_qps / usable)


if __name__ == "__main__":
    n, dim = 50_000_000, 1024
    print(f"Corpus: {n:,} chunks, {dim} dimensions, M=16, 2 replicas, 30% headroom, 64 GiB nodes")
    show("float32 (4 bytes/dim)", size(n, dim, vector_bytes=4.0))
    show("float16 (2 bytes/dim)", size(n, dim, vector_bytes=2.0))
    show("int8 scalar quantization (1 byte/dim) + float32 rescoring on SSD",
         size(n, dim, vector_bytes=1.0, rescore_float32_on_disk=True))
    show("binary quantization (1 bit/dim) + float32 rescoring on SSD",
         size(n, dim, vector_bytes=1 / 8, rescore_float32_on_disk=True))
    groups = qps_nodes(target_qps=400, per_replica_qps=120, shards=1)
    print("\nQPS: target 400 qps, measured 120 qps per replica group at the p95 target, 50% headroom")
    print(f"  replica groups needed: {groups}")
    print("  every query fans out to every shard, so total nodes = shards x replica groups")
    for label, vb, resc in (("float32", 4.0, False), ("int8 + rescore", 1.0, True), ("binary + rescore", 1 / 8, True)):
        r = size(n, dim, vector_bytes=vb, rescore_float32_on_disk=resc)
        total = r["shards"] * max(2, groups)
        print(f"  {label:18s} shards={r['shards']} groups={max(2, groups)} total nodes={total}")
    # unit-price illustration (hypothetical): 64 GiB node at 0.50 USD per hour, 730 hours per month
    price = 0.50 * 730
    print(f"  at an illustrative {price:.0f} USD per node-month: float32 {6 * 7 * price:,.0f}, "
          f"int8 {2 * 7 * price:,.0f}, binary {1 * 7 * price:,.0f} USD per month (compute only)")
