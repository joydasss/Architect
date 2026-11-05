"""Break-even calculator: hosted per-token pricing vs self-hosted GPUs vs reserved.

Standard library only. All prices and throughputs are ILLUSTRATIVE placeholders.
Replace them with current quotes and your own measured throughput.

Model: monthly token demand T (millions of tokens, input+output blended).
  hosted cost      = T * price_per_mtok
  self-hosted cost = ceil(T / (per-GPU monthly capacity * target utilization))
                     * (GPU monthly cost) + fixed monthly ops cost
Self-hosted cost is a step function: GPUs come in whole units, and you need at
least min_gpus for availability (N+1).
"""

import math

HOURS = 730

HOSTED_PRICE_PER_MTOK = 1.50       # blended USD per million tokens (illustrative)
GPU_ON_DEMAND_HR = 4.00            # USD per GPU-hour on demand (illustrative)
GPU_RESERVED_HR = 2.40             # USD per GPU-hour, 1-year commitment (illustrative)
GPU_TOKENS_PER_SEC = 2500          # measured sustained blended tokens/s per GPU (illustrative)
TARGET_UTIL = 0.55                 # leave headroom for tail latency and bursts
OPS_FIXED_MONTH = 9000.0           # on-call share, monitoring, security, tooling
MIN_GPUS = 2                       # availability floor


def per_gpu_mtok_month():
    return GPU_TOKENS_PER_SEC * 3600 * HOURS / 1e6 * TARGET_UTIL


def hosted(t_mtok):
    return t_mtok * HOSTED_PRICE_PER_MTOK


def self_hosted(t_mtok, gpu_hr):
    gpus = max(MIN_GPUS, math.ceil(t_mtok / per_gpu_mtok_month()))
    return gpus, gpus * gpu_hr * HOURS + OPS_FIXED_MONTH


def main():
    cap = per_gpu_mtok_month()
    print(f"usable capacity per GPU = {cap:,.0f} Mtok/month at {TARGET_UTIL:.0%} utilization")
    print(f"{'Mtok/month':>11} {'hosted':>10} {'GPUs od':>8} {'on-demand':>10} "
          f"{'GPUs rsv':>8} {'reserved':>10}  cheapest")
    for t in (500, 1000, 2000, 5000, 10000, 20000, 50000, 100000):
        h = hosted(t)
        g1, od = self_hosted(t, GPU_ON_DEMAND_HR)
        g2, rs = self_hosted(t, GPU_RESERVED_HR)
        best = min(("hosted", h), ("on-demand", od), ("reserved", rs), key=lambda x: x[1])[0]
        print(f"{t:>11,} {h:>10,.0f} {g1:>8} {od:>10,.0f} {g2:>8} {rs:>10,.0f}  {best}")

    # Break-even volume against hosted, ignoring the step function, for reserved GPUs.
    per_mtok_self = GPU_RESERVED_HR * HOURS / cap
    fixed_floor = MIN_GPUS * GPU_RESERVED_HR * HOURS + OPS_FIXED_MONTH
    print()
    print(f"marginal self-hosted cost = {per_mtok_self:.3f} USD/Mtok (reserved, at target util)")
    if HOSTED_PRICE_PER_MTOK > per_mtok_self:
        be = (OPS_FIXED_MONTH + MIN_GPUS * GPU_RESERVED_HR * HOURS - 0) / (HOSTED_PRICE_PER_MTOK - per_mtok_self)
        print(f"fixed floor (2 GPUs + ops) = {fixed_floor:,.0f} USD/month")
        print(f"linear break-even vs hosted = {be:,.0f} Mtok/month "
              f"({be * 1e6 / (HOURS * 3600):,.0f} tokens/s average)")
        t = 100
        while self_hosted(t, GPU_RESERVED_HR)[1] > hosted(t):
            t += 100
        print(f"exact (stepped GPU count) break-even = {t:,} Mtok/month "
              f"with {self_hosted(t, GPU_RESERVED_HR)[0]} GPUs")


if __name__ == "__main__":
    main()
