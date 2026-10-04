"""Estimate worker nodes for workload requests and system reservations."""

from math import ceil


def required_nodes(
    pod_cpu_millicores: int,
    pod_memory_mib: int,
    node_cpu_millicores: int,
    node_memory_mib: int,
    system_cpu_millicores: int,
    system_memory_mib: int,
) -> int:
    usable_cpu = node_cpu_millicores - system_cpu_millicores
    usable_memory = node_memory_mib - system_memory_mib
    if usable_cpu <= 0 or usable_memory <= 0:
        raise ValueError("system reservations must leave positive allocatable capacity")
    nodes_for_cpu = ceil(pod_cpu_millicores / usable_cpu)
    nodes_for_memory = ceil(pod_memory_mib / usable_memory)
    return max(nodes_for_cpu, nodes_for_memory)


def main() -> None:
    nodes = required_nodes(
        pod_cpu_millicores=18_000,
        pod_memory_mib=48_000,
        node_cpu_millicores=8_000,
        node_memory_mib=32_768,
        system_cpu_millicores=700,
        system_memory_mib=2_048,
    )
    print(f"Minimum nodes for modeled requests: {nodes}")
    print("Add zone-loss and upgrade headroom before choosing pool size.")


if __name__ == "__main__":
    main()