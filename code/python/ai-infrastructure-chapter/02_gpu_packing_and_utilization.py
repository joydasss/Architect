"""GPU bin-packing and utilization arithmetic (standard library only).

Part 1: first-fit-decreasing packing of model replicas onto 80 GB GPUs.
Part 2: MIG-style slice packing (7 compute slices, 80 GB split into 10 GB units).
Part 3: gang-scheduling fragmentation for a 16-GPU training job.
All sizes are illustrative.
"""


def ffd(items, capacity):
    bins = []
    for name, size in sorted(items, key=lambda x: -x[1]):
        for b in bins:
            if b["free"] >= size:
                b["items"].append(name)
                b["free"] -= size
                break
        else:
            bins.append({"items": [name], "free": capacity - size})
    return bins


def part1():
    print("== Part 1: replicas by memory footprint (GB) onto 80 GB GPUs ==")
    items = [("A", 45), ("B", 40), ("C", 30), ("D", 25), ("E", 20),
             ("F", 20), ("G", 15), ("H", 10), ("I", 10), ("J", 5)]
    total = sum(s for _, s in items)
    bins = ffd(items, 80)
    print(f"Total demand {total} GB, lower bound {-(-total // 80)} GPUs")
    for i, b in enumerate(bins):
        used = 80 - b["free"]
        print(f"GPU{i}: {b['items']} used {used} GB ({used / 80:.0%})")
    print(f"FFD uses {len(bins)} GPUs, memory utilization {total / (80 * len(bins)):.1%}")
    one_each = len(items)
    print(f"One workload per GPU would use {one_each} GPUs, "
          f"utilization {total / (80 * one_each):.1%}")


def part2():
    print("\n== Part 2: MIG-style slices (7 slices per GPU) ==")
    # profile name -> (compute slices, memory GB)
    profiles = {"1g.10gb": (1, 10), "2g.20gb": (2, 20), "3g.40gb": (3, 40)}
    demand = [("embed-a", "1g.10gb"), ("embed-b", "1g.10gb"), ("rerank", "2g.20gb"),
              ("small-llm", "3g.40gb")]
    used_c = sum(profiles[p][0] for _, p in demand)
    used_m = sum(profiles[p][1] for _, p in demand)
    print(f"Demand: {used_c} of 7 compute slices, {used_m} of 80 GB on one GPU")
    print(f"Compute slice use {used_c / 7:.0%}, memory use {used_m / 80:.0%}")
    print("3g.40gb twice would use 6 slices and 80 GB; a 7th slice has no memory left")


def part3():
    print("\n== Part 3: gang scheduling fragmentation ==")
    nodes = 8
    gpus_per_node = 8
    # free GPUs per node after small jobs scattered across the cluster
    free = [3, 5, 2, 6, 4, 1, 7, 4]
    total_free = sum(free)
    print(f"Free GPUs per node: {free} (total {total_free} of {nodes * gpus_per_node})")
    job_nodes, job_gpus_per_node = 2, 8
    fits = sum(1 for f in free if f == gpus_per_node) // job_nodes
    print(f"A 16-GPU job needing {job_nodes} whole nodes: placeable copies = {fits}")
    print(f"Yet {total_free} GPUs are free, enough for {total_free // 16} such jobs by count")
    pct = total_free / (nodes * gpus_per_node)
    print(f"Free fraction {pct:.0%} is unusable for this job: fragmentation")


if __name__ == "__main__":
    part1()
    part2()
    part3()
