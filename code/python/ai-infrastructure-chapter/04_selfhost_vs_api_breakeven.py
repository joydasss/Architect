"""Self-hosting versus hosted API break-even calculator (standard library only).

All prices and throughputs are ILLUSTRATIVE ASSUMPTIONS. Replace them with your
own quotes and measured tokens per second before deciding anything.
"""

HOURS_PER_MONTH = 730


def api_monthly_cost(tokens_in_m, tokens_out_m, price_in, price_out):
    """Token volumes in millions per month, prices in dollars per million."""
    return tokens_in_m * price_in + tokens_out_m * price_out


def selfhost_monthly_cost(gpus, gpu_hour, utilization_hours_frac=1.0,
                          ops_fixed=0.0, redundancy=1.0):
    return gpus * redundancy * gpu_hour * HOURS_PER_MONTH * utilization_hours_frac + ops_fixed


def capacity_tokens_per_month(gpus, tokens_per_s_per_gpu, avg_utilization):
    return gpus * tokens_per_s_per_gpu * avg_utilization * 3600 * HOURS_PER_MONTH / 1e6


def main():
    # assumptions
    price_in, price_out = 0.30, 1.20          # $ per million tokens (hosted API, illustrative)
    in_share = 0.80                            # share of tokens that are input
    gpu_hour = 3.00                            # $ per GPU hour on demand (illustrative)
    tps = 5000                                 # mixed tokens/s per GPU at target batching (small model)
    avg_util = 0.50                            # average fraction of peak that traffic fills
    gpus_min = 2                               # two replicas for availability
    ops_fixed = 6000.0                         # monthly share of engineer time and tooling

    blended = in_share * price_in + (1 - in_share) * price_out
    print(f"Blended API price: ${blended:.3f} per million tokens")

    fixed = selfhost_monthly_cost(gpus_min, gpu_hour, ops_fixed=ops_fixed)
    print(f"Self-host fixed cost ({gpus_min} GPUs + ops): ${fixed:,.0f} per month")
    cap = capacity_tokens_per_month(gpus_min, tps, avg_util)
    print(f"Usable capacity at {avg_util:.0%} average utilization: {cap:,.0f} M tokens/month")
    per_gpu_cap = capacity_tokens_per_month(1, tps, avg_util)
    marginal = gpu_hour * HOURS_PER_MONTH / per_gpu_cap
    print(f"Marginal GPU cost per million tokens at that utilization: ${marginal:.3f}")
    print(f"Self-host cost per million at the 2-GPU capacity: ${fixed / cap:.3f}")
    crossover = None
    for vol in range(100, 200001, 100):
        n = max(gpus_min, -(-vol // int(per_gpu_cap)))
        if vol * blended > selfhost_monthly_cost(n, gpu_hour, ops_fixed=ops_fixed):
            crossover = vol
            break
    print(f"Break-even volume vs API (with GPU count stepping): {crossover:,} M tokens/month")

    print("\nVolume table (M tokens/month):")
    print(f"{'volume':>10} {'API $':>12} {'self-host $':>14} {'cheaper':>10}")
    for vol in (500, 5000, 20000, 40000, 60000, 100000):
        api = vol * blended
        n = max(gpus_min, -(-vol // int(capacity_tokens_per_month(1, tps, avg_util))))
        sh = selfhost_monthly_cost(n, gpu_hour, ops_fixed=ops_fixed)
        print(f"{vol:>10,} {api:>12,.0f} {sh:>14,.0f} {'API' if api < sh else 'self-host':>10}")

    print("\nSensitivity: break-even volume (M tokens/month) by GPU price and ops cost")
    for g in (2.0, 3.0, 4.5):
        m = g * HOURS_PER_MONTH / per_gpu_cap
        cells = []
        for ops in (0, 6000, 15000):
            # Region 1: only the two-GPU floor is running, so cost is flat.
            floor_cost = selfhost_monthly_cost(gpus_min, g, ops_fixed=ops)
            v = floor_cost / blended
            if v > cap:
                # Region 2: GPUs scale with volume, cost ~ ops + marginal * volume.
                v = ops / (blended - m) if blended > m else float("inf")
            cells.append(f"ops ${ops:>6,}: {v:8,.0f}")
        print(f"GPU ${g:.2f}/h (marginal ${m:.3f}/M): " + "  ".join(cells))


if __name__ == "__main__":
    main()
