"""Quantization error, speculative-decoding acceptance, floating-point order, perplexity.

Standard library only. Run: python 04_quantization_speculative_logprobs.py

Everything is synthetic and seeded. The point is to make mechanisms visible,
not to predict the quality of a real model.
"""

import math
import random
import struct


def to_fp16(x):
    """Round a Python float to the nearest IEEE half-precision value."""
    return struct.unpack("e", struct.pack("e", x))[0]


def quantize_row(row, bits, group):
    """Symmetric quantization with one scale per group of `group` weights."""
    qmax = 2 ** (bits - 1) - 1
    out = []
    for i in range(0, len(row), group):
        blk = row[i:i + group]
        scale = max(abs(v) for v in blk) / qmax
        out.extend(max(-qmax - 1, min(qmax, round(v / scale))) * scale for v in blk)
    return out


def matvec(w, x):
    return [sum(a * b for a, b in zip(row, x)) for row in w]


def quantization_demo():
    rng = random.Random(0)
    rows, cols = 64, 512
    w = [[rng.gauss(0, 0.02) for _ in range(cols)] for _ in range(rows)]
    for _ in range(10):  # a few outlier weights
        w[rng.randrange(rows)][rng.randrange(cols)] = 0.5
    x = [rng.gauss(0, 1) for _ in range(cols)]
    ref = matvec(w, x)
    ref_norm = math.sqrt(sum(v * v for v in ref))
    print("== Quantization error on a synthetic layer with 10 outlier weights ==")
    for bits in (8, 4):
        for name, group in (("per-row", cols), ("group-64", 64)):
            wq = [quantize_row(r, bits, group) for r in w]
            mse = sum((a - b) ** 2 for r, rq in zip(w, wq) for a, b in zip(r, rq)) / (rows * cols)
            out = matvec(wq, x)
            err = math.sqrt(sum((a - b) ** 2 for a, b in zip(ref, out))) / ref_norm
            print(f"INT{bits} {name:<9} weight MSE {mse:.2e} | relative output error {err:.4f}")


def speculative_demo():
    print("\n== Speculative decoding: expected tokens per target-model pass ==")
    for a in (0.6, 0.8, 0.9):
        row = []
        for k in (2, 4, 8):
            expected = (1 - a ** (k + 1)) / (1 - a)  # includes the bonus token
            row.append(f"k={k}: {expected:.2f}")
        print(f"acceptance {a:.1f}: " + "  ".join(row))
    rng = random.Random(0)
    a, k, trials, total = 0.8, 4, 100_000, 0
    for _ in range(trials):
        n = 0
        while n < k and rng.random() < a:
            n += 1
        total += n + 1
    print(f"Monte Carlo a=0.8 k=4: {total / trials:.2f} (formula {(1 - a ** 5) / (1 - a):.2f})")
    e = (1 - a ** 5) / (1 - a)
    for c in (0.05, 0.2):
        print(f"draft cost {c:.2f} of target: speedup ~ {e / (1 + 4 * c):.2f}x")


def fp_order_demo():
    print("\n== Floating-point addition is not associative ==")
    print("(0.1 + 0.2) + 0.3 =", repr((0.1 + 0.2) + 0.3), "| 0.1 + (0.2 + 0.3) =", repr(0.1 + (0.2 + 0.3)))
    rng = random.Random(1)
    vals = [to_fp16(rng.gauss(0, 1)) for _ in range(20_000)]
    fwd = 0.0
    for v in vals:
        fwd = to_fp16(fwd + v)
    bwd = 0.0
    for v in reversed(vals):
        bwd = to_fp16(bwd + v)
    print("float16 running sum, forward :", fwd)
    print("float16 running sum, backward:", bwd)
    print("float64 reference            :", round(math.fsum(vals), 4))
    z1, z2 = 10.0000, 10.0004
    print(f"near-tie logits {z1} vs {z2}: a 1e-3 perturbation on the first flips greedy choice:",
          z1 + 1e-3 > z2)


def perplexity_demo():
    print("\n== Cross-entropy and perplexity ==")
    probs = [0.5, 0.25, 0.8, 0.1]
    ce = -sum(math.log(p) for p in probs) / len(probs)
    print(f"token probabilities {probs}")
    print(f"cross-entropy {ce:.4f} nats = {ce / math.log(2):.4f} bits; perplexity {math.exp(ce):.4f}")
    vocab = 50_000
    print(f"uniform guess over {vocab}: cross-entropy {math.log(vocab):.3f} nats, perplexity {vocab}")


if __name__ == "__main__":
    quantization_demo()
    speculative_demo()
    fp_order_demo()
    perplexity_demo()
