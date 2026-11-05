"""Parameter counts, FLOPs, training compute and key-value (KV) cache sizes.

Standard library only. Every number the chapter's worked examples quote is
printed here. Configurations are the published architecture shapes of the
named models; hardware figures are published peak specifications and are
labelled as such. Verify them against vendor documentation before planning.

Run: python 02_params_flops_kv_cache.py
"""

import math

GIB = 1024 ** 3


def decoder_params(d, layers, heads, kv_heads, d_head, d_ff, vocab,
                   gated_ffn=True, tied=False, bias=False, pos_len=0, norm_params_per=1):
    """Count parameters of a decoder-only transformer.

    gated_ffn=True  -> SwiGLU style: three d x d_ff matrices (gate, up, down).
    gated_ffn=False -> classic two-matrix FFN.
    norm_params_per -> parameters per normalization (d for RMSNorm, 2d for LayerNorm with bias).
    """
    q = d * heads * d_head
    k = d * kv_heads * d_head
    v = d * kv_heads * d_head
    o = heads * d_head * d
    attn = q + k + v + o
    ffn = (3 if gated_ffn else 2) * d * d_ff
    norms = 2 * d * norm_params_per
    biases = 0
    if bias:
        biases = (heads * d_head + 2 * kv_heads * d_head + d) + (d_ff + d)
    per_layer = attn + ffn + norms + biases
    embed = vocab * d
    out_head = 0 if tied else vocab * d
    total = layers * per_layer + embed + out_head + d * norm_params_per + pos_len * d
    return {"per_layer": per_layer, "attn": attn, "ffn": ffn, "embed": embed + out_head, "total": total}


def moe_params(d, layers, heads, kv_heads, d_head, d_ff, vocab, experts, top_k):
    q = d * heads * d_head
    kv = 2 * d * kv_heads * d_head
    o = heads * d_head * d
    attn = q + kv + o
    expert = 3 * d * d_ff
    router = d * experts
    norms = 2 * d
    total = layers * (attn + experts * expert + router + norms) + 2 * vocab * d + d
    active = layers * (attn + top_k * expert + router + norms) + 2 * vocab * d + d
    return total, active


def kv_bytes_per_token(layers, kv_heads, d_head, bytes_per=2):
    return 2 * layers * kv_heads * d_head * bytes_per


def main():
    print("=== 1. Parameter counts ===")
    models = {
        "GPT-2 small (LayerNorm, GELU, learned pos, tied)": dict(
            d=768, layers=12, heads=12, kv_heads=12, d_head=64, d_ff=3072, vocab=50257,
            gated_ffn=False, tied=True, bias=True, pos_len=1024, norm_params_per=2),
        "Llama-2 7B shape": dict(d=4096, layers=32, heads=32, kv_heads=32, d_head=128,
                                 d_ff=11008, vocab=32000),
        "Llama-2 70B shape": dict(d=8192, layers=80, heads=64, kv_heads=8, d_head=128,
                                  d_ff=28672, vocab=32000),
        "Llama-3 8B shape": dict(d=4096, layers=32, heads=32, kv_heads=8, d_head=128,
                                 d_ff=14336, vocab=128256),
    }
    counted = {}
    for name, cfg in models.items():
        r = decoder_params(**cfg)
        counted[name] = (cfg, r)
        print(f"{name}: total={r['total']:,}  per_layer={r['per_layer']:,}  "
              f"attn/layer={r['attn']:,}  ffn/layer={r['ffn']:,}  embed+head={r['embed']:,}")
    total, active = moe_params(4096, 32, 32, 8, 128, 14336, 32000, experts=8, top_k=2)
    print(f"Mixtral-8x7B shape (8 experts, top-2): total={total:,}  active per token={active:,}")

    print("\n=== 2. Rule of thumb check: params ~ 12 * L * d^2 ===")
    for name in ("GPT-2 small (LayerNorm, GELU, learned pos, tied)", "Llama-2 7B shape"):
        cfg, r = counted[name]
        approx = 12 * cfg["layers"] * cfg["d"] ** 2
        print(f"{name}: 12*L*d^2={approx:,}  non-embedding exact={r['total'] - r['embed']:,}")

    print("\n=== 3. FLOPs per token ===")
    cfg, r = counted["Llama-2 7B shape"]
    n_total = r["total"]
    n_noemb = n_total - cfg["vocab"] * cfg["d"]  # drop the input embedding lookup (no matmul)
    print(f"matmul parameters (all but input embedding): {n_noemb:,}")
    print(f"forward FLOPs/token  ~ 2N = {2 * n_noemb:.3e}")
    print(f"training FLOPs/token ~ 6N = {6 * n_noemb:.3e}")
    for n_ctx in (2048, 4096, 32768, 131072):
        attn_fwd = 2 * cfg["layers"] * n_ctx * cfg["heads"] * cfg["d_head"]  # causal average
        share = attn_fwd / (2 * n_noemb + attn_fwd)
        print(f"  context {n_ctx:>6}: attention FLOPs/token (fwd, causal avg) = {attn_fwd:.3e}  "
              f"share of forward = {share:5.1%}")

    print("\n=== 4. Training compute (6ND) and compute-optimal sizing ===")
    for name, n, dtok in (("Chinchilla 70B x 1.4T tokens", 70e9, 1.4e12),
                          ("Gopher 280B x 300B tokens", 280e9, 300e9),
                          ("7B x 2T tokens (illustrative)", 7e9, 2e12)):
        c = 6 * n * dtok
        print(f"{name}: C = 6ND = {c:.3e} FLOPs  tokens/param = {dtok / n:.1f}")
    c_budget = 1e24
    n_opt = math.sqrt(c_budget / (6 * 20))
    print(f"Budget 1e24 FLOPs, D=20N: N = sqrt(C/120) = {n_opt:.3e} params, D = {20 * n_opt:.3e} tokens")
    peak = 989e12  # H100 SXM dense bf16 peak, published spec at time of writing
    for mfu in (0.30, 0.40, 0.50):
        gpu_s = 5.88e23 / (peak * mfu)
        print(f"  5.88e23 FLOPs at MFU {mfu:.0%}: {gpu_s / 3600:,.0f} GPU-hours "
              f"({gpu_s / 3600 / 2048 / 24:.1f} days on 2048 GPUs)")
    print(f"  at an illustrative $2.00 per GPU-hour and MFU 40%: ${5.88e23 / (peak * 0.40) / 3600 * 2:,.0f}")

    print("\n=== 5. KV cache ===")
    shapes = {
        "Llama-2 7B (MHA, 32 KV heads)": (32, 32, 128),
        "Llama-3 8B (GQA, 8 KV heads)": (32, 8, 128),
        "Llama-2 70B (GQA, 8 KV heads)": (80, 8, 128),
    }
    for name, (layers, kvh, dh) in shapes.items():
        b = kv_bytes_per_token(layers, kvh, dh, 2)
        row = [f"{b / 1024:.0f} KiB/token (fp16)"]
        for n_ctx in (4096, 32768, 131072):
            row.append(f"{n_ctx}: {b * n_ctx / GIB:.2f} GiB")
        print(f"{name}: " + "; ".join(row))
    # Llama-2 70B with full multi-head (hypothetical) for the GQA saving.
    b_mha = kv_bytes_per_token(80, 64, 128, 2)
    b_gqa = kv_bytes_per_token(80, 8, 128, 2)
    print(f"Llama-2 70B if every head had its own K,V: {b_mha / 1024:.0f} KiB/token; "
          f"GQA saving = {b_mha / b_gqa:.0f}x")
    # How many 32k-token sequences fit next to the weights on one 80 GB (decimal) accelerator?
    hbm = 80e9
    weights = 2 * counted["Llama-3 8B shape"][1]["total"]
    free = hbm * 0.9 - weights
    per_seq = kv_bytes_per_token(32, 8, 128, 2) * 32768
    print(f"80 GB accelerator, Llama-3 8B shape, fp16 weights {weights / 1e9:.1f} GB, 90% usable: "
          f"free {free / 1e9:.1f} GB -> {int(free // per_seq)} sequences of 32768 tokens "
          f"({per_seq / 1e9:.2f} GB each)")

    print("\n=== 6. Attention-score matrix memory if materialized ===")
    for n_ctx in (2048, 8192, 32768, 131072):
        per_head = n_ctx * n_ctx * 2  # fp16 bytes
        print(f"n={n_ctx:>6}: one head = {per_head / GIB:9.3f} GiB, 32 heads in one layer = "
              f"{32 * per_head / GIB:10.1f} GiB per sequence")

    print("\n=== 7. Memory-bound decoding (batch 1) ===")
    bw = 3.35e12  # H100 SXM HBM3 bandwidth, published spec at time of writing
    weights_bytes = 2 * counted["Llama-2 7B shape"][1]["total"]
    t = weights_bytes / bw
    print(f"read all fp16 weights once: {weights_bytes / 1e9:.2f} GB / 3.35 TB/s = {t * 1e3:.2f} ms/token "
          f"-> <= {1 / t:.0f} tokens/s per sequence")
    flops_per_byte = (2 * n_noemb) / weights_bytes
    print(f"arithmetic intensity at batch 1 ~ {flops_per_byte:.2f} FLOP/byte; "
          f"accelerator ridge point ~ {peak / bw:.0f} FLOP/byte")
    print(f"batch needed to reach the ridge point ~ {peak / bw / flops_per_byte:.0f} sequences "
          f"(ignores KV reads and overheads)")

    print("\n=== 8. Training memory per parameter (mixed precision, Adam) ===")
    per_param = 2 + 2 + 4 + 4 + 4  # bf16 weights, bf16 grads, fp32 master, Adam m, Adam v
    print(f"{per_param} bytes/param -> 7B model = {per_param * 6.74e9 / GIB:.0f} GiB before activations")


def chinchilla_loss(n, d, e=1.69, a=406.4, b=410.7, alpha=0.34, beta=0.28):
    """Parametric loss L(N, D) = E + A/N^alpha + B/D^beta with the constants reported by
    Hoffmann et al. (2022). A replication (Besiroglu et al., 2024) found these constants
    do not fit the reconstructed data exactly, so treat the output as illustrative."""
    return e + a / n ** alpha + b / d ** beta


def scaling_and_case_study():
    print("\n=== 9. Parametric scaling-law illustration (constants as reported, illustrative) ===")
    for name, n, d in (("Gopher-like 280B x 300B", 280e9, 300e9),
                       ("Chinchilla-like 70B x 1.4T", 70e9, 1.4e12),
                       ("8B x 15T tokens (heavily over-trained)", 8e9, 15e12),
                       ("8B x 160B tokens (20 tok/param)", 8e9, 160e9)):
        print(f"{name}: C = {6 * n * d:.2e}  predicted loss = {chinchilla_loss(n, d):.3f}")
    c = 5.88e23
    best = None
    n = 1e9
    while n < 1e13:
        d = c / (6 * n)
        loss = chinchilla_loss(n, d)
        if best is None or loss < best[0]:
            best = (loss, n, d)
        n *= 1.01
    print(f"best split of C=5.88e23 under the formula: N = {best[1]:.2e}, D = {best[2]:.2e}, "
          f"tokens/param = {best[2] / best[1]:.1f}, loss = {best[0]:.3f}")

    print("\n=== 10. Case study arithmetic: 32k-token requests on a Llama-3 8B shape ===")
    layers, d_model = 32, 4096
    total = 8_030_261_248
    n_mat = total - 128256 * 4096
    n_ctx = 32768
    proj = 2 * n_mat * n_ctx
    attn = 2 * layers * d_model * n_ctx ** 2  # causal, averaged
    peak, mfu, bw = 989e12, 0.40, 3.35e12
    pre_flops = proj + attn
    pre_s = pre_flops / (peak * mfu)
    print(f"prefill FLOPs: projections {proj:.3e} + attention {attn:.3e} = {pre_flops:.3e}; "
          f"attention share {attn / pre_flops:.1%}; time at 40% MFU = {pre_s:.2f} s")
    w = 2 * total
    kv = kv_bytes_per_token(32, 8, 128, 2) * n_ctx
    out_tokens = 500
    for batch in (1, 13):
        step_bytes = w + batch * kv
        step_s = step_bytes / bw
        print(f"batch {batch:>2}: bytes/step = {step_bytes / 1e9:.1f} GB -> {step_s * 1e3:.1f} ms/step, "
              f"{batch / step_s:.0f} tokens/s total, {1 / step_s:.0f} tokens/s per sequence")
    step13 = (w + 13 * kv) / bw
    decode_share = out_tokens * step13 / 13
    gpu_s = pre_s + decode_share
    print(f"per request at batch 13: prefill {pre_s:.2f} s + decode share {decode_share:.2f} s = "
          f"{gpu_s:.2f} accelerator-seconds; at an illustrative $2.00/hour = ${gpu_s / 3600 * 2:.5f}")
    print(f"weights bytes {w / 1e9:.2f} GB; KV per 32k sequence {kv / 1e9:.2f} GB")

    n_long = 131072
    proj_l = 2 * n_mat * n_long
    attn_l = 2 * layers * d_model * n_long ** 2
    tot_l = proj_l + attn_l
    print(f"prefill at {n_long} tokens: projections {proj_l:.3e} + attention {attn_l:.3e} = {tot_l:.3e}; "
          f"attention share {attn_l / tot_l:.1%}; time at 40% MFU = {tot_l / (peak * mfu):.1f} s; "
          f"ratio to 32k prefill = {tot_l / pre_flops:.1f}x")
    print(f"crossover n where attention FLOPs equal the rest: 12*d = {12 * d_model}")
    window = 4096
    kv_tok = kv_bytes_per_token(32, 8, 128, 2)
    print(f"sliding window {window}: cache = {kv_tok * window / GIB:.3f} GiB; hybrid 1/4 dense at 131072 = "
          f"{(kv_tok * n_long / 4 + 0.75 * kv_tok * window) / GIB:.3f} GiB")


def extras():
    print("\n=== 11. Mixture-of-experts routing, scaling factors, tokens, contributions ===")
    logits = [2.0, 1.0, 0.1, -1.0]
    top = sorted(range(4), key=lambda i: -logits[i])[:2]
    exps = [math.exp(logits[i]) for i in top]
    gates = [e / sum(exps) for e in exps]
    print(f"router logits {logits}: top-2 experts {top}, exp = {[round(e, 3) for e in exps]}, "
          f"gates = {[round(g, 3) for g in gates]}")
    for b in (1, 4, 8, 16):
        print(f"  batch {b:>2}: expected distinct experts of 8 (top-2, uniform) = "
              f"{8 * (1 - (1 - 2 / 8) ** b):.2f}")
    total, active = moe_params(4096, 32, 32, 8, 128, 14336, 32000, experts=8, top_k=2)
    print(f"Mixtral shape: forward FLOPs/token active = {2 * active:.3e}, if dense at total size = "
          f"{2 * total:.3e}; bf16 weights = {2 * total / 1e9:.1f} GB")
    print(f"balanced aux-loss factor E*sum(f*P) with f=P=1/8 over 8 experts: "
          f"{8 * sum((1 / 8) * (1 / 8) for _ in range(8)):.3f}")

    print(f"Kaplan exponent: doubling N multiplies loss by {2 ** -0.076:.3f}; "
          f"10x multiplies by {10 ** -0.076:.3f}")
    n70, d70 = 70e9, 1.4e12
    n8, d8 = 8.03e9, 15e12
    demand = 1e13
    t70 = 6 * n70 * d70 + 2 * n70 * demand
    t8 = 6 * n8 * d8 + 2 * n8 * demand
    print(f"lifetime compute at {demand:.0e} served tokens: 70B = {t70:.3e}, 8B/15T = {t8:.3e}, "
          f"ratio = {t70 / t8:.2f}")
    t70s = 6 * n70 * d70 + 2 * n70 * 1e11
    t8s = 6 * n8 * d8 + 2 * n8 * 1e11
    print(f"at 1e11 served tokens: 70B = {t70s:.3e}, 8B/15T = {t8s:.3e}")

    print(f"ViT tokens: 224/16 -> {(224 // 16) ** 2 + 1}; 384/16 -> {(384 // 16) ** 2 + 1}; "
          f"score-entry ratio = {((384 // 16) ** 2 + 1) ** 2 / ((224 // 16) ** 2 + 1) ** 2:.2f}; "
          f"patch 8 at 224 -> {(224 // 8) ** 2} patches")
    print(f"image cache at 128 KiB/token for 576 tokens = {576 * 128 / 1024:.0f} MiB")
    state = 8192 * 16 * 2 * 48
    print(f"SSM state (8192x16, 48 layers, 16-bit) = {state / 2 ** 20:.0f} MiB; "
          f"KV at 32768 (Llama-3 8B shape) / state = {4 * 2 ** 30 / state:.0f}x")

    print("context-length cost table (Llama-3 8B shape, 40% MFU on 989 TFLOPs, 55.9 GB for cache):")
    n_mat = 8_030_261_248 - 128256 * 4096
    prev = None
    for n in (4096, 32768, 131072):
        flops = 2 * n_mat * n + 2 * 32 * 4096 * n ** 2
        secs = flops / (989e12 * 0.40)
        kvb = kv_bytes_per_token(32, 8, 128, 2) * n
        conc = int(55.9e9 // kvb)
        extra = "" if prev is None else f"  (x{secs / prev:.1f} vs previous row)"
        print(f"  n={n:>6}: prefill {secs:6.3f} s, cache {kvb / 1e9:6.2f} GB, concurrent {conc}{extra}")
        prev = secs

    print("case-study options (peak 989 TFLOPs, 40% MFU, 3.35 TB/s per accelerator, 80 GB each, 90% usable):")
    n6k = 6000
    f6k = 2 * n_mat * n6k + 2 * 32 * 4096 * n6k ** 2
    kv6k = kv_bytes_per_token(32, 8, 128, 2) * n6k
    print(f"  B (8B shape, 6000-token retrieved prompt): prefill {f6k / (989e12 * 0.4):.2f} s, "
          f"cache {kv6k / 1e9:.2f} GB, concurrent per accelerator {int(55.9e9 // kv6k)}")
    n30k = 30000
    f30k = 2 * n_mat * n30k + 2 * 32 * 4096 * n30k ** 2
    print(f"  A (8B shape, 30000-token contract): prefill {f30k / (989e12 * 0.4):.2f} s")
    w70 = 2 * 68_976_648_192
    n_mat70 = 68_976_648_192 - 32000 * 8192
    f70 = 2 * n_mat70 * 32768 + 2 * 80 * 8192 * 32768 ** 2
    kv70 = kv_bytes_per_token(80, 8, 128, 2) * 32768
    gpus = 4
    free70 = gpus * 80e9 * 0.9 - w70
    conc70 = int(free70 // kv70)
    pre70 = f70 / (gpus * 989e12 * 0.4)
    step70 = (w70 + conc70 * kv70) / (gpus * 3.35e12)
    gpu_s = gpus * (pre70 + 500 * step70 / conc70)
    print(f"  C (70B shape, 4 accelerators, 32768 tokens): weights {w70 / 1e9:.1f} GB, free {free70 / 1e9:.1f} GB, "
          f"cache/seq {kv70 / 1e9:.2f} GB, concurrent {conc70}, prefill {pre70:.2f} s, step {step70 * 1e3:.1f} ms, "
          f"accelerator-seconds/request {gpu_s:.1f}, cost at $2/h = ${gpu_s / 3600 * 2:.4f}")

    # Attention weight versus contribution in the 3-token example.
    w = 0.401
    print(f"contribution norms for 'the': self {w * math.hypot(2, 0):.3f}, "
          f"sat {w * math.hypot(1, 1):.3f}, cat {0.198 * math.hypot(0, 2):.3f}")


if __name__ == "__main__":
    main()
    scaling_and_case_study()
    extras()
