"""Load model, Little's Law, capacity planning, break-even, and scale-up lag.

Standard library only. Every price and traffic figure is an ILLUSTRATIVE
assumption stated in the code. Replace them with your own measurements.

Part A  open-loop versus closed-loop load against the same G/G/c server pool
Part B  Little's Law
Part C  traffic to GPU count to monthly cost, and self-host versus hosted API
Part D  scale-up lag arithmetic
"""
import heapq
import math
import random


# ---------------------------------------------------------------- Part A
def service_time(rng):
    # lognormal with mean about 8.4 s: median 7 s, heavy right tail
    return rng.lognormvariate(math.log(7.0), 0.6)


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(p * len(xs)))]


def open_loop(rate, slots, n, seed):
    """Poisson arrivals that ignore how the server is doing."""
    rng = random.Random(seed)
    free = [0.0] * slots
    heapq.heapify(free)
    t, lat = 0.0, []
    for _ in range(n):
        t += rng.expovariate(rate)
        start = max(t, heapq.heappop(free))
        end = start + service_time(rng)
        heapq.heappush(free, end)
        lat.append(end - t)
    return lat, n / t


def closed_loop(users, slots, n, seed, think=0.0):
    """Each user sends the next request only after the previous reply."""
    rng = random.Random(seed)
    free = [0.0] * slots
    heapq.heapify(free)
    ready = [(0.0, u) for u in range(users)]
    heapq.heapify(ready)
    lat, done, last = [], 0, 0.0
    while done < n:
        t, u = heapq.heappop(ready)
        start = max(t, heapq.heappop(free))
        end = start + service_time(rng)
        heapq.heappush(free, end)
        lat.append(end - t)
        heapq.heappush(ready, (end + think, u))
        done += 1
        last = max(last, end)
    return lat, n / last


def part_a():
    slots = 32
    mean_service = sum(service_time(random.Random(i)) for i in range(20000)) / 20000
    cap = slots / (sum(service_time(random.Random(100 + i)) for i in range(20000)) / 20000)
    print(f"== Part A: {slots} slots, mean service about {mean_service:.1f} s, capacity about {cap:.2f} req/s ==")
    print(f"{'load':<24} {'req/s':>6} {'p50 s':>7} {'p95 s':>7} {'p99 s':>8}")
    for lam in (2.0, 3.5, 3.8, 4.2):
        lat, thr = open_loop(lam, slots, 20000, seed=11)
        print(f"open  lambda={lam:<12} {thr:>6.2f} {pct(lat,.5):>7.1f} {pct(lat,.95):>7.1f} {pct(lat,.99):>8.1f}")
    for users in (16, 32, 48):
        lat, thr = closed_loop(users, slots, 20000, seed=11)
        print(f"closed users={users:<13} {thr:>6.2f} {pct(lat,.5):>7.1f} {pct(lat,.95):>7.1f} {pct(lat,.99):>8.1f}")
    print("The closed loop at 32 users reports near-capacity throughput and a flat latency: it never")
    print("offers more than the server can take, so it cannot show the open-loop queue.")


# ---------------------------------------------------------------- Part B
def part_b():
    print("\n== Part B: Little's Law  L = lambda * W ==")
    lam, w = 4.0, 9.0
    print(f"{lam} req/s x {w} s mean residence = {lam*w:.0f} requests in flight")
    slots = 32
    print(f"with {slots} slots per replica: {math.ceil(lam*w/slots)} replicas needed at 100% slot use,")
    print(f"{math.ceil(lam*w/slots/0.7)} replicas at a 70% slot-use ceiling")
    q = 60
    print(f"a queue of {q} waiting requests at {lam} req/s drains in {q/lam:.0f} s if capacity were unlimited;")
    print(f"if capacity is {lam*1.1:.1f} req/s against {lam} arriving, net drain is {lam*1.1-lam:.1f} req/s -> {q/(lam*1.1-lam):.0f} s")


# ---------------------------------------------------------------- Part C
def part_c():
    print("\n== Part C: capacity plan (illustrative assumptions) ==")
    req_day, p_in, p_out = 3_000_000, 1500, 250
    peak_factor = 3.0
    prefill_rate, decode_rate = 14_129, 2_975        # tokens/s per 4-GPU group (script 01)
    gpus_per_group, usd_gpu_hr, target_util = 4, 4.0, 0.60
    hours_month = 730
    avg_in = req_day * p_in / 86400
    avg_out = req_day * p_out / 86400
    print(f"average input {avg_in:,.0f} tok/s, output {avg_out:,.0f} tok/s; peak x{peak_factor}")
    results = {}
    for label, hit in (("no prefix cache", 0.0), ("60% prefix hit", 0.6)):
        pre = avg_in * peak_factor * (1 - hit) / prefill_rate
        dec = avg_out * peak_factor / decode_rate
        groups_busy = pre + dec
        groups = math.ceil(groups_busy / target_util)
        gpus = groups * gpus_per_group
        cost = gpus * usd_gpu_hr * hours_month
        results[label] = (gpus, cost)
        print(f"{label:<16} prefill {pre:5.2f} + decode {dec:5.2f} = {groups_busy:5.2f} group-s/s "
              f"-> {groups} groups at {target_util:.0%} = {gpus} GPUs -> ${cost:,.0f}/month")
    month_in = req_day * 30 * p_in / 1e6
    month_out = req_day * 30 * p_out / 1e6
    print(f"monthly tokens: {month_in:,.0f} M input, {month_out:,.0f} M output")
    api_in, api_out = 0.60, 2.40                       # ILLUSTRATIVE $ per million tokens
    api_cost = month_in * api_in + month_out * api_out
    print(f"hosted API at ${api_in}/M in and ${api_out}/M out (placeholder prices): ${api_cost:,.0f}/month")
    for label, (gpus, cost) in results.items():
        print(f"  self-host '{label}': ${cost:,.0f} vs API ${api_cost:,.0f} -> ratio {cost/api_cost:.2f}")
    # utilization at average load for the cached plan
    gpus, cost = results["60% prefix hit"]
    groups = gpus // gpus_per_group
    avg_busy = (avg_in * 0.4 / prefill_rate + avg_out / decode_rate)
    print(f"average utilization of the cached plan = {avg_busy:.2f}/{groups} = {avg_busy/groups:.0%}")
    # break-even: volume multiplier at which self-host (fixed fleet scaled to the multiple) equals API
    print("break-even versus traffic volume (fleet scales with volume, peak factor held):")
    for pf in (3.0, 2.0, 1.5, 1.2):
        pre = avg_in * pf * 0.4 / prefill_rate
        dec = avg_out * pf / decode_rate
        g = math.ceil((pre + dec) / target_util)
        c = g * gpus_per_group * usd_gpu_hr * hours_month
        print(f"  peak/average {pf:<4} -> {g*gpus_per_group:>3} GPUs, ${c:,.0f}/month, ratio to API {c/api_cost:.2f}")


# ---------------------------------------------------------------- Part D
def part_d():
    print("\n== Part D: scale-up lag ==")
    detect, provision, download, init, warm = 30, 90, 70, 60, 30   # seconds, assumed
    lag = detect + provision + download + init + warm
    print(f"lag = detect {detect} + provision {provision} + download {download} + init {init} + warmup {warm} = {lag} s")
    print("download = 140 GB / 2 GB/s = 70 s; warm pool with weights resident reduces lag to detect + warmup = "
          f"{detect + warm} s")
    base, peak, ramp = 10.0, 20.0, 120      # busy group-seconds per second; ramp duration (s)
    capacity = 12.0
    print(f"demand ramps {base:.0f} -> {peak:.0f} group-s/s over {ramp} s; capacity {capacity:.0f} until new replicas arrive")
    for name, l in (("cold scale-out", lag), ("warm pool", detect + warm)):
        backlog, t, dt, new_cap = 0.0, 0.0, 1.0, 22.0
        worst = 0.0
        while t < 900:
            demand = base + (peak - base) * min(1.0, t / ramp)
            cap = capacity if t < l else new_cap
            backlog = max(0.0, backlog + (demand - cap) * dt)
            worst = max(worst, backlog)
            t += dt
        drain = worst / (new_cap - peak)
        print(f"{name:<15} lag {l:>3} s: peak backlog {worst:7.0f} group-seconds of work, "
              f"drain after capacity arrives about {drain:.0f} s")


# ---------------------------------------------------------------- Part E
def part_e():
    """Case-study stages: GPUs and monthly cost at peak for the same traffic as Part C."""
    print("\n== Part E: case study stages (same traffic as Part C, peak x3, 60% target) ==")
    avg_in, avg_out = 3_000_000 * 1500 / 86400, 3_000_000 * 250 / 86400
    peak, util, usd, hrs = 3.0, 0.60, 4.0, 730
    useful_static = 0.30                      # Section 6.1: mean/max output in a batch of 32
    stages = [
        # name, gpus/group, prefill tok/s, decode tok/s, prefix hit, output waste factor
        ("S0 BF16 TP4, request-level", 4, 14_129, 1_697 * useful_static, 0.0, 1.00),
        ("S1 + continuous + paged KV", 4, 14_129, 2_975, 0.0, 1.00),
        ("S2 + prefix cache (60%)", 4, 14_129, 2_975, 0.6, 1.00),
        ("S3 + FP8 weights/acts/KV, TP2", 2, 14_129, 3_019, 0.6, 1.00),
        ("S4 + cancellation propagation", 2, 14_129, 3_019, 0.6, 0.94),
    ]
    base_cost = None
    for name, g, pre_r, dec_r, hit, waste in stages:
        busy = avg_in * peak * (1 - hit) / pre_r + avg_out * peak * waste / dec_r
        groups = math.ceil(busy / util)
        gpus = groups * g
        cost = gpus * usd * hrs
        base_cost = base_cost or cost
        per_group_rps = 3_000_000 / 86400 * peak / groups
        print(f"{name:<32} busy {busy:6.2f} -> {groups:>3} groups, {gpus:>3} GPUs, ${cost:>10,.0f}/mo "
              f"({cost/base_cost:5.1%} of S0), peak {per_group_rps:4.2f} req/s per group")
    print("FP8 TP2 decode check (B=64, ctx 2000, FP8 weights 70 GB, FP8 KV 163,840 B/token):")
    t_mem = (70e9 + 64 * 2000 * 163_840) / (2 * 3.35e12 * 0.70)
    payload = 64 * 8192 * 2
    t_comm = 2 * 80 * (8e-6 + 2 * (2 - 1) / 2 * payload / 300e9)
    step = t_mem + t_comm
    print(f"  t_mem {t_mem*1e3:.1f} ms + comm {t_comm*1e3:.1f} ms = {step*1e3:.1f} ms -> {64/step:.0f} tok/s per 2-GPU group")


if __name__ == "__main__":
    part_a()
    part_b()
    part_c()
    part_d()
    part_e()
