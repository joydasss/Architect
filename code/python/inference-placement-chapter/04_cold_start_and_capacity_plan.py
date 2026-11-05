"""Cold-start arithmetic and a forecast-to-fleet capacity plan (standard library only).

All figures are illustrative. Part 1 computes model load time from weight size
and storage bandwidth. Part 2 turns a product forecast into a GPU count.
"""

import math


def load_time_s(params_b, bytes_per_param, bw_gbps_effective, fixed_s):
    size_gb = params_b * bytes_per_param
    return size_gb, size_gb / bw_gbps_effective + fixed_s


def cold_start():
    print("Cold start (pull weights + init runtime + warm kernels):")
    print(f"{'model':>14} {'size GB':>8} {'source':>16} {'GB/s':>5} {'total s':>8}")
    cases = [
        ("8B bf16", 8, 2, "object store", 1.0, 40),
        ("8B bf16", 8, 2, "node-local NVMe", 3.0, 40),
        ("70B bf16", 70, 2, "object store", 1.0, 60),
        ("70B bf16", 70, 2, "node-local NVMe", 3.0, 60),
        ("70B fp8", 70, 1, "node-local NVMe", 3.0, 60),
    ]
    for name, p, b, src, bw, fixed in cases:
        size, t = load_time_s(p, b, bw, fixed)
        print(f"{name:>14} {size:>8.0f} {src:>16} {bw:>5.1f} {t:>8.0f}")
    print("fixed = container start + runtime init + CUDA graph capture + warmup")


def capacity_plan():
    print()
    print("Capacity plan from forecast:")
    dau = 120_000
    sessions_per_user = 1.5
    req_per_session = 6
    peak_hour_share = 0.14       # share of daily traffic in the peak hour
    peak_to_hour_avg = 1.8       # peak minute vs average of peak hour
    in_tok, out_tok = 2500, 350
    daily = dau * sessions_per_user * req_per_session
    peak_hour = daily * peak_hour_share
    avg_rps = peak_hour / 3600
    peak_rps = avg_rps * peak_to_hour_avg
    print(f"daily requests = {daily:,.0f}")
    print(f"peak-hour requests = {peak_hour:,.0f}; average rps in peak hour = {avg_rps:.2f}")
    print(f"peak-minute rps = {peak_rps:.2f}")

    # Per-GPU throughput measured at the SLO (illustrative): output tok/s and prefill tok/s.
    decode_tps = 1800
    prefill_tps = 20000
    util_target = 0.6
    gpu_seconds_per_req = out_tok / decode_tps + in_tok / prefill_tps
    gpu_needed = peak_rps * gpu_seconds_per_req / util_target
    print(f"GPU-seconds per request = {out_tok}/{decode_tps} + {in_tok}/{prefill_tps}"
          f" = {gpu_seconds_per_req:.3f}")
    print(f"GPUs for peak at {util_target:.0%} utilization = {gpu_needed:.2f}")
    n = math.ceil(gpu_needed)
    with_redundancy = n + max(1, math.ceil(0.25 * n))
    print(f"round up = {n}; with N+25% (at least +1) failure headroom = {with_redundancy}")
    # Little's Law for concurrency
    w = 0.9 + out_tok * 0.025
    print(f"Little's Law: in-flight = rps*W = {peak_rps:.2f} * {w:.2f} s = {peak_rps * w:.1f} requests")


if __name__ == "__main__":
    cold_start()
    capacity_plan()
