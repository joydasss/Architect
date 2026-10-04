"""Estimate a block volume's throughput ceiling from IOPS and size."""


def estimate_throughput_mib_per_second(
    iops: int, block_size_kib: int, provisioned_cap_mib_per_second: int
) -> float:
    iops_limited = iops * block_size_kib / 1024
    return min(iops_limited, provisioned_cap_mib_per_second)


def main() -> None:
    provisioned_cap = 250
    for block_size_kib in (4, 16, 256):
        throughput = estimate_throughput_mib_per_second(
            iops=3000,
            block_size_kib=block_size_kib,
            provisioned_cap_mib_per_second=provisioned_cap,
        )
        print(f"block={block_size_kib:>3} KiB -> ceiling={throughput:.1f} MiB/s")
    print("This upper bound omits latency, queue depth, and guest overhead.")


if __name__ == "__main__":
    main()