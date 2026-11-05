"""Positional information: sinusoidal, rotary (RoPE) and ALiBi, standard library only.

Checks the properties the chapter relies on:
1. Attention without positions is permutation-equivariant.
2. Sinusoidal encodings: the dot product PE(p).PE(p+k) depends only on k.
3. RoPE: the query-key score depends only on the offset n-m.
4. ALiBi: head slopes and the bias matrix.
5. Position interpolation: why scaling positions keeps rotation angles in range.

Run: python 03_positional_encodings.py
"""

import math
import random


def softmax(row):
    m = max(row)
    e = [math.exp(v - m) for v in row]
    s = sum(e)
    return [v / s for v in e]


def self_attention(x):
    d = len(x[0])
    out = []
    for qi in x:
        scores = [sum(a * b for a, b in zip(qi, kj)) / math.sqrt(d) for kj in x]
        w = softmax(scores)
        out.append([sum(w[j] * x[j][c] for j in range(len(x))) for c in range(d)])
    return out


def sinusoid(pos, d_model, base=10000.0):
    pe = []
    for i in range(d_model // 2):
        angle = pos / (base ** (2 * i / d_model))
        pe.extend([math.sin(angle), math.cos(angle)])
    return pe


def rope(vec, pos, base=10000.0):
    """Rotate consecutive coordinate pairs of vec by pos * theta_i."""
    out = []
    d = len(vec)
    for i in range(d // 2):
        theta = pos * base ** (-2 * i / d)
        c, s = math.cos(theta), math.sin(theta)
        a, b = vec[2 * i], vec[2 * i + 1]
        out.extend([a * c - b * s, a * s + b * c])
    return out


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def main():
    rng = random.Random(7)

    print("=== 1. Permutation equivariance without positions ===")
    x = [[rng.gauss(0, 1) for _ in range(4)] for _ in range(4)]
    perm = [2, 0, 3, 1]
    y = self_attention(x)
    y_perm = self_attention([x[i] for i in perm])
    gap = max(abs(a - b) for r1, r2 in zip([y[i] for i in perm], y_perm) for a, b in zip(r1, r2))
    print(f"max |f(permuted x) - permuted f(x)| = {gap:.1e}  (zero means order is invisible)")

    print("\n=== 2. Sinusoidal: PE(p).PE(p+k) depends only on k (d_model=64) ===")
    for k in (1, 5, 20):
        vals = [dot(sinusoid(p, 64), sinusoid(p + k, 64)) for p in (0, 10, 100, 1000)]
        print(f"offset k={k:>2}: " + ", ".join(f"{v:.6f}" for v in vals))
    print("wavelengths (positions per full cycle) for d_model=64:",
          [round(2 * math.pi * 10000 ** (2 * i / 64), 1) for i in (0, 8, 16, 31)])

    print("\n=== 3. RoPE: q_m . k_n depends only on n-m (d=16) ===")
    q = [rng.gauss(0, 1) for _ in range(16)]
    k = [rng.gauss(0, 1) for _ in range(16)]
    for m, n in ((3, 7), (10, 14), (100, 104), (5000, 5004)):
        print(f"m={m:>5}, n={n:>5}, offset={n - m}: score = {dot(rope(q, m), rope(k, n)):.6f}")
    for m, n in ((3, 9), (50, 56)):
        print(f"m={m:>5}, n={n:>5}, offset={n - m}: score = {dot(rope(q, m), rope(k, n)):.6f}")
    print(f"norm of q before/after rotation: {math.sqrt(dot(q, q)):.6f} / "
          f"{math.sqrt(dot(rope(q, 123), rope(q, 123))):.6f}")

    print("\n=== 4. ALiBi: slopes and bias for 8 heads, 5 tokens ===")
    n_heads = 8
    slopes = [2 ** (-8 * (h + 1) / n_heads) for h in range(n_heads)]
    print("slopes:", [f"1/{round(1 / s)}" for s in slopes])
    s0 = slopes[0]
    for i in range(5):
        row = [(-s0 * (i - j) if j <= i else float("-inf")) for j in range(5)]
        print("  " + " ".join(f"{v:6.2f}" if v != float("-inf") else "  -inf" for v in row))
    print(f"penalty at distance 1000 for head 0: {-s0 * 1000:.1f}; for last head: "
          f"{-slopes[-1] * 1000:.2f}")

    print("\n=== 5. Position interpolation: RoPE angle of the slowest pair ===")
    d = 128
    slowest = 10000 ** (-2 * (d // 2 - 1) / d)
    for pos, label in ((4096, "trained length 4096"), (16384, "extended to 16384, no scaling"),
                       (16384 / 4, "16384 scaled by 1/4")):
        print(f"{label:34s}: slowest angle = {pos * slowest:.4f} rad "
              f"({pos * slowest / (2 * math.pi):.4f} turns)")
    print(f"fastest pair (theta=1): offset 1 -> {1.0:.2f} rad; after /4 interpolation -> "
          f"{1.0 / 4:.2f} rad (neighbours are harder to tell apart)")


if __name__ == "__main__":
    main()
