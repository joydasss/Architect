"""Roofline arithmetic for LLM decode and prefill (standard library only).

All hardware numbers are ILLUSTRATIVE, rounded from public H100 SXM class
datasheet figures (80 GB HBM3, about 3.35 TB/s, about 989 TFLOP/s dense BF16).
Replace them with your accelerator's datasheet and your own measurements.

Model: a 70B-class dense decoder with grouped-query attention
(80 layers, 8 KV heads, head width 128, model width 8192), 16-bit weights.
"""

N_PARAMS = 70e9
LAYERS, KV_HEADS, HEAD_DIM, D_MODEL = 80, 8, 128, 8192
WEIGHT_BYTES = 2            # BF16
KV_BYTES = 2                # BF16 cache

GPU_MEM = 80e9
GPU_BW = 3.35e12            # bytes/s
GPU_FLOPS = 989e12          # FLOP/s dense BF16
BW_EFF = 0.70               # achievable fraction of peak bandwidth
MFU = 0.50                  # achievable fraction of peak FLOP/s in large matmuls
NVLINK_BW = 300e9           # bytes/s effective per GPU for all-reduce (assumed)
ALLREDUCE_LAT = 8e-6        # seconds per all-reduce launch + sync (assumed)


def kv_bytes_per_token():
    return 2 * LAYERS * KV_HEADS * HEAD_DIM * KV_BYTES


def decode_step(batch, ctx, tp):
    """Return (t_mem, t_compute, t_comm, bound) for one decode step."""
    weight_bytes = N_PARAMS * WEIGHT_BYTES
    kv_read = batch * ctx * kv_bytes_per_token()
    t_mem = (weight_bytes + kv_read) / (tp * GPU_BW * BW_EFF)
    t_cmp = (2 * N_PARAMS * batch) / (tp * GPU_FLOPS * MFU)
    # two all-reduces per layer; ring all-reduce moves 2(n-1)/n of the payload
    payload = batch * D_MODEL * 2
    per_ar = ALLREDUCE_LAT + 2 * (tp - 1) / tp * payload / NVLINK_BW
    t_comm = 0.0 if tp == 1 else 2 * LAYERS * per_ar
    bound = "memory" if t_mem >= t_cmp else "compute"
    return t_mem, t_cmp, t_comm, bound


def main():
    print("== Per-token KV cache ==")
    kvb = kv_bytes_per_token()
    print(f"KV bytes/token = 2*{LAYERS}*{KV_HEADS}*{HEAD_DIM}*{KV_BYTES} = {kvb} ({kvb/1024:.0f} KiB)")
    print(f"KV for one 8,192-token sequence = {kvb*8192/1e9:.2f} GB")

    print("\n== Ridge point (arithmetic intensity at which compute = memory time) ==")
    ridge = GPU_FLOPS / GPU_BW
    print(f"peak ridge = {GPU_FLOPS:.3e}/{GPU_BW:.3e} = {ridge:.0f} FLOP/byte")
    print(f"achievable ridge = {ridge*MFU/BW_EFF:.0f} FLOP/byte")
    print("decode intensity at batch B (weights only) = 2*N*B/(N*2 bytes) = B FLOP/byte")
    print(f"=> weight-bound until B ~ {ridge*MFU/BW_EFF:.0f}")

    tp = 4
    print(f"\n== Decode step, 70B BF16, TP={tp}, context 2,000 tokens ==")
    print("weights per GPU = %.1f GB; free for KV (90%% usable) = %.1f GB"
          % (N_PARAMS * WEIGHT_BYTES / tp / 1e9,
             0.9 * GPU_MEM / 1e9 - N_PARAMS * WEIGHT_BYTES / tp / 1e9))
    print(f"{'B':>4} {'t_mem ms':>9} {'t_cmp ms':>9} {'t_comm ms':>9} {'step ms':>8} {'tok/s':>8} {'bound':>8}")
    for b in (1, 4, 16, 32, 64, 128, 256, 512):
        tm, tc, tcomm, bound = decode_step(b, 2000, tp)
        step = max(tm, tc) + tcomm
        print(f"{b:>4} {tm*1e3:>9.2f} {tc*1e3:>9.2f} {tcomm*1e3:>9.2f} {step*1e3:>8.2f} {b/step:>8.0f} {bound:>8}")

    print("\n== Concurrency limit from KV memory (TP=4, 8,192-token sequences) ==")
    free = tp * (0.9 * GPU_MEM) - N_PARAMS * WEIGHT_BYTES
    per_seq = kvb * 8192
    print(f"free = {free/1e9:.0f} GB, per sequence = {per_seq/1e9:.2f} GB, max sequences = {int(free // per_seq)}")
    free8 = 8 * (0.9 * GPU_MEM) - N_PARAMS * WEIGHT_BYTES
    print(f"TP=8: free = {free8/1e9:.0f} GB, max sequences = {int(free8 // per_seq)}")

    print("\n== Prefill (compute-bound), TP=4 ==")
    for n in (512, 2000, 8000):
        t = 2 * N_PARAMS * n / (tp * GPU_FLOPS * MFU)
        print(f"prompt {n:>5} tokens: {t*1e3:7.1f} ms  ({n/t:,.0f} tok/s)")

    print("\n== Single-stream decode speed ceiling ==")
    tm, _, tcomm, _ = decode_step(1, 2000, tp)
    print(f"B=1 step = {(tm+tcomm)*1e3:.1f} ms -> {1/(tm+tcomm):.0f} tokens/s")
    tm1, _, _, _ = decode_step(1, 2000, 1)
    print(f"(TP=1 would need 140 GB of weights; bandwidth-only step {tm1*1e3:.1f} ms)")

    print("\n== Cost per million output tokens at B=64, TP=4, $4.00/GPU-hour (assumed) ==")
    tm, tc, tcomm, _ = decode_step(64, 2000, tp)
    step = max(tm, tc) + tcomm
    toks = 64 / step
    dollars_per_s = 4.0 * tp / 3600
    print(f"throughput {toks:.0f} tok/s, cost ${dollars_per_s/toks*1e6:.2f} per 1M output tokens (decode only, 100% busy)")


if __name__ == "__main__":
    main()
