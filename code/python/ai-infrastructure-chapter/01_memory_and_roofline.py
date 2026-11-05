"""Memory budget and roofline arithmetic for LLM serving (standard library only).

Illustrative hardware numbers (check vendor datasheets before relying on them):
  H100 SXM 80 GB: 3.35 TB/s HBM, about 989 TFLOPS dense BF16.
Model shapes are Llama-style grouped-query attention configurations used for
illustration: 8B (32 layers, 8 KV heads, head dim 128) and
70B (80 layers, 8 KV heads, head dim 128).
"""

GB = 1e9
GIB = 2**30


def weights_bytes(params, bytes_per_weight):
    return params * bytes_per_weight


def kv_bytes_per_token(layers, kv_heads, head_dim, bytes_per_elem=2):
    # 2 tensors (K and V) per layer
    return 2 * layers * kv_heads * head_dim * bytes_per_elem


def max_concurrent_sequences(hbm_bytes, weights, overhead_frac, kv_per_token, ctx):
    usable = hbm_bytes * (1 - overhead_frac)
    free = usable - weights
    if free <= 0:
        return 0, free
    return int(free // (kv_per_token * ctx)), free


def decode_tokens_per_s_bound(bandwidth, weights, batch):
    # each decode step streams all weights once, regardless of batch size
    return batch * bandwidth / weights


def main():
    print("== Weight memory ==")
    for name, p in (("8B", 8e9), ("70B", 70e9)):
        for fmt, b in (("BF16", 2), ("FP8", 1), ("4-bit", 0.5)):
            print(f"{name:>4} {fmt:>5}: {weights_bytes(p, b) / GB:7.1f} GB")

    print("\n== KV cache per token ==")
    kv8 = kv_bytes_per_token(32, 8, 128)
    kv70 = kv_bytes_per_token(80, 8, 128)
    print(f"8B : {kv8} bytes = {kv8 / 1024:.0f} KiB per token")
    print(f"70B: {kv70} bytes = {kv70 / 1024:.0f} KiB per token")

    print("\n== Concurrent sequences on one 80 GB GPU (10% overhead reserve) ==")
    hbm = 80 * GB
    for ctx in (4096, 8192, 32768):
        n, free = max_concurrent_sequences(hbm, weights_bytes(8e9, 2), 0.10, kv8, ctx)
        print(f"8B BF16, ctx {ctx:>6}: free {free / GB:5.1f} GB -> {n} sequences")
    n, free = max_concurrent_sequences(hbm, weights_bytes(70e9, 1), 0.10, kv70, 8192)
    print(f"70B FP8,  ctx   8192: free {free / GB:5.1f} GB -> {n} sequences")
    n, free = max_concurrent_sequences(hbm, weights_bytes(70e9, 2), 0.10, kv70, 8192)
    print(f"70B BF16 on one GPU: free {free / GB:5.1f} GB -> {n} sequences (does not fit)")

    print("\n== Roofline for decode on H100 ==")
    bw = 3.35e12
    flops = 989e12
    ridge = flops / bw
    print(f"Ridge point: {ridge:.0f} FLOP per byte")
    w = weights_bytes(8e9, 2)
    for batch in (1, 8, 32, 128, 256, 512):
        mem_bound = decode_tokens_per_s_bound(bw, w, batch)
        compute_bound = flops / (2 * 8e9)
        achieved = min(mem_bound, compute_bound)
        regime = "memory-bound" if mem_bound < compute_bound else "compute-bound"
        print(f"batch {batch:>3}: {achieved:9.0f} tokens/s upper bound ({regime})")
    print(f"Arithmetic intensity at batch B in BF16 is about B FLOP/byte, "
          f"so the crossover is near batch {ridge:.0f}")
    print(f"70B FP8 single stream bound: "
          f"{decode_tokens_per_s_bound(bw, weights_bytes(70e9, 1), 1):.1f} tokens/s")


if __name__ == "__main__":
    main()
