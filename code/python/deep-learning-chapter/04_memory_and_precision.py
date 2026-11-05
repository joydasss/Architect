"""GPU memory accounting, compute estimate, roofline ridge points, and
reduced-precision pitfalls.

Standard library only. Prints the numbers used in the chapter:
  1. training-state memory for a 1-billion-parameter model (FP32 versus mixed
     precision with an AdamW optimizer),
  2. activation memory for a transformer layer stack under three policies,
  3. the 6*N*D training-FLOP estimate and wall-clock time,
  4. arithmetic-intensity ridge points for two example accelerators,
  5. FP16 underflow and loss scaling, BF16 rounding, and FP16 accumulation
     stall, using real half-precision rounding.
"""

import math
import struct

GIB = 2 ** 30


def to_fp16(x):
    try:
        return struct.unpack("<e", struct.pack("<e", x))[0]
    except OverflowError:
        return math.inf if x > 0 else -math.inf


def to_bf16(x):
    """Round a Python float to bfloat16 (round to nearest even on the top 16 bits of FP32)."""
    if x == 0 or not math.isfinite(x):
        return x
    bits = struct.unpack("<I", struct.pack("<f", x))[0]
    lsb = (bits >> 16) & 1
    bits = (bits + 0x7FFF + lsb) & 0xFFFF0000
    return struct.unpack("<f", struct.pack("<I", bits))[0]


def state_memory():
    n = 1_000_000_000
    print("== Training-state memory for N = 1e9 parameters ==")
    fp32 = {"weights FP32": 4 * n, "gradients FP32": 4 * n, "Adam m FP32": 4 * n, "Adam v FP32": 4 * n}
    mixed = {
        "weights BF16 (working copy)": 2 * n,
        "gradients BF16": 2 * n,
        "master weights FP32": 4 * n,
        "Adam m FP32": 4 * n,
        "Adam v FP32": 4 * n,
    }
    for title, d in (("Pure FP32 + AdamW", fp32), ("Mixed precision BF16 + FP32 master + AdamW", mixed)):
        print(title)
        for k, v in d.items():
            print(f"  {k:30s} {v / 1e9:6.2f} GB  ({v / GIB:6.2f} GiB)")
        tot = sum(d.values())
        print(f"  {'total':30s} {tot / 1e9:6.2f} GB  ({tot / GIB:6.2f} GiB)  = {tot / n:.0f} bytes/param")
    sgd_m = 4 * n * 3
    print(f"FP32 SGD with momentum: {sgd_m / 1e9:.1f} GB (12 bytes/param)")


def activation_memory():
    L, h, a, s, b = 20, 2048, 16, 2048, 4
    params = 12 * L * h * h
    print("\n== Activation memory, transformer stack L=%d h=%d heads=%d seq=%d batch=%d ==" % (L, h, a, s, b))
    print(f"non-embedding parameters 12*L*h^2 = {params / 1e9:.3f} B")
    per_layer_full = s * b * h * (34 + 5 * a * s / h)
    per_layer_sel = s * b * h * 34
    per_layer_ckpt = s * b * h * 2
    print(f"store everything (16-bit):       {per_layer_full / GIB:6.3f} GiB/layer -> {L * per_layer_full / GIB:7.2f} GiB total")
    print(f"drop attention score tensors:    {per_layer_sel / GIB:6.3f} GiB/layer -> {L * per_layer_sel / GIB:7.2f} GiB total")
    peak_full_ckpt = L * per_layer_ckpt + per_layer_full
    print(f"full checkpointing per layer:    {per_layer_ckpt / GIB:6.3f} GiB/layer input -> "
          f"{L * per_layer_ckpt / GIB:5.2f} GiB stored + {per_layer_full / GIB:5.2f} GiB for one layer recompute"
          f" = {peak_full_ckpt / GIB:5.2f} GiB peak")
    print(f"extra compute for full checkpointing: about 1 extra forward = 1/3 of fwd+bwd (4/3 total)")


def flops_and_time():
    n, d = 1e9, 20e9
    flops = 6 * n * d
    print("\n== Training compute, 6*N*D ==")
    print(f"N=1e9, D=20e9 tokens -> {flops:.2e} FLOPs")
    for name, peak in (("A100 bf16 dense 312 TFLOPS", 312e12), ("H100 SXM bf16 dense 989 TFLOPS", 989e12)):
        for mfu in (0.3, 0.4):
            sec = flops / (peak * mfu)
            print(f"  {name:32s} MFU {mfu:.0%}: {sec / 3600:7.1f} GPU-hours")


def ridge_points():
    print("\n== Roofline ridge points (FLOPs per byte of HBM traffic) ==")
    for name, peak, bw in (("A100 80GB", 312e12, 2.039e12), ("H100 SXM", 989e12, 3.35e12)):
        print(f"  {name:10s} peak {peak / 1e12:5.0f} TFLOPS / {bw / 1e12:.2f} TB/s = {peak / bw:6.1f} FLOP/byte")
    print("Arithmetic intensity of a bf16 matmul (M x K) @ (K x N), traffic = reads + write:")
    for m, k, nn in ((8, 4096, 4096), (128, 4096, 4096), (2048, 4096, 4096), (8192, 8192, 8192)):
        fl = 2 * m * k * nn
        by = 2 * (m * k + k * nn + m * nn)
        print(f"  M={m:5d} K={k:5d} N={nn:5d}: {fl / by:7.1f} FLOP/byte")
    print("Elementwise add of two bf16 tensors: 1 FLOP per 6 bytes = 0.17 FLOP/byte")


def precision_pitfalls():
    print("\n== Reduced-precision pitfalls ==")
    print(f"FP16 max {to_fp16(65504.0)}, smallest normal 2^-14 = {2 ** -14:.3e}, smallest subnormal 2^-24 = {2 ** -24:.3e}")
    g = 1e-8
    print(f"gradient {g:.0e} in FP16 -> {to_fp16(g)}")
    for scale in (1024, 65536):
        print(f"  loss scale {scale:6d}: scaled grad -> {to_fp16(g * scale):.4e}, unscaled back -> {to_fp16(g * scale) / scale:.3e}")
    big = 2.0 * 65536
    print(f"  but a gradient of 2.0 with scale 65536 = {big:.0f} -> FP16 {to_fp16(big)} (overflow, step must be skipped)")
    print(f"1 + 0.001: FP32 {1.001:.4f}, FP16 {to_fp16(1.001):.10f}, BF16 {to_bf16(1.001):.10f}")
    print(f"1 + 0.004 in BF16 -> {to_bf16(1.004)}  (BF16 spacing near 1 is 2^-7 = {2 ** -7})")
    print(f"1000.3 in FP16 {to_fp16(1000.3):.4f}, BF16 {to_bf16(1000.3):.4f}")
    print(f"1e-30 in FP16 {to_fp16(1e-30)}, BF16 {to_bf16(1e-30):.3e}; 1e5 in FP16 {to_fp16(1e5)}, BF16 {to_bf16(1e5):.1f}")
    # accumulation stall
    acc16 = 0.0
    acc32 = 0.0
    for _ in range(10000):
        acc16 = to_fp16(acc16 + to_fp16(1e-4))
        acc32 += 1e-4
    print(f"sum of 10000 x 1e-4: FP32-style accumulator {acc32:.4f}, FP16 accumulator {acc16:.4f}")


if __name__ == "__main__":
    state_memory()
    activation_memory()
    flops_and_time()
    ridge_points()
    precision_pitfalls()
