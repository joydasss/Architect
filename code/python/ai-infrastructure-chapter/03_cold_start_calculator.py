"""Cold-start arithmetic for model serving replicas (standard library only).

cold start = image pull + weight read + deserialize/copy to GPU + engine init + warmup
Bandwidths are illustrative assumptions, not measurements.
"""

GB = 1e9


def seconds(size_gb, gbit_per_s=None, gbyte_per_s=None):
    if gbit_per_s is not None:
        return size_gb / (gbit_per_s / 8)
    return size_gb / gbyte_per_s


def scenario(name, weights_gb, source_gbyte_s, image_gb=0.0, image_gbyte_s=0.5,
             pcie_gbyte_s=25.0, init_s=30.0, warmup_s=15.0, parallel_ranks=1):
    pull = image_gb / image_gbyte_s
    read = weights_gb / source_gbyte_s
    # tensor-parallel ranks each read their own shard in parallel
    read /= parallel_ranks
    copy = (weights_gb / parallel_ranks) / pcie_gbyte_s
    total = pull + read + copy + init_s + warmup_s
    print(f"{name:<42} pull {pull:5.1f}  read {read:6.1f}  copy {copy:5.1f}  "
          f"init {init_s:4.0f}  warm {warmup_s:3.0f}  total {total:6.1f} s")
    return total


def main():
    w8 = 16.0    # 8B BF16
    w70 = 70.0   # 70B FP8
    w70b = 140.0  # 70B BF16
    print("Weights: 8B BF16 = 16 GB, 70B FP8 = 70 GB, 70B BF16 = 140 GB")
    print("Sources: object store over 10 Gbit/s = 1.25 GB/s, 25 Gbit/s = 3.125 GB/s,")
    print("         network file system 2 GB/s, local NVMe 6 GB/s, page cache 20 GB/s\n")
    scenario("8B, object store 10 Gbit/s, cold node", w8, 1.25, image_gb=12)
    scenario("8B, local NVMe cache", w8, 6.0, image_gb=0)
    scenario("8B, page cache (second start on node)", w8, 20.0, image_gb=0)
    scenario("70B FP8 TP=4, object store 10 Gbit/s", w70, 1.25, image_gb=12,
             parallel_ranks=1, init_s=60, warmup_s=30)
    scenario("70B FP8 TP=4, shards from NVMe", w70, 6.0, parallel_ranks=4,
             init_s=60, warmup_s=30)
    scenario("70B BF16 TP=8, object store 25 Gbit/s", w70b, 3.125, image_gb=12,
             init_s=70, warmup_s=30)
    print("\nScale-up reaction time example (8B, cold node):")
    t = scenario("  total", w8, 1.25, image_gb=12)
    print(f"  A request burst waits about {t:.0f} s for new capacity; "
          f"with a 20 s latency objective, keep warm replicas or a pre-pulled cache.")


if __name__ == "__main__":
    main()
