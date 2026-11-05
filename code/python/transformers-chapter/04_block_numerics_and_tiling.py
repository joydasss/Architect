"""A tiny pre-LN decoder block, online-softmax tiling, and numerical stability.

Standard library only. Demonstrates:
1. Softmax overflow and the max-subtraction fix.
2. float16 limits: logits overflow, and stalled accumulation.
3. Online (tiled) softmax attention equals standard attention (the FlashAttention idea).
4. Residual-stream growth with depth in a pre-LN stack.
5. A full pre-LN decoder block with causal masking: future tokens cannot change the past.

Run: python 04_block_numerics_and_tiling.py
"""

import math
import random
import struct


def to_fp16(x):
    """Round a Python float to the nearest IEEE half-precision value (inf on overflow)."""
    try:
        return struct.unpack("<e", struct.pack("<e", x))[0]
    except OverflowError:
        return math.copysign(float("inf"), x)


def softmax_naive(row):
    e = [math.exp(v) for v in row]
    s = sum(e)
    return [v / s for v in e]


def softmax_stable(row):
    m = max(row)
    e = [math.exp(v - m) for v in row]
    s = sum(e)
    return [v / s for v in e]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def attention_standard(q, ks, vs):
    d = len(q)
    w = softmax_stable([dot(q, k) / math.sqrt(d) for k in ks])
    return [sum(w[j] * vs[j][c] for j in range(len(vs))) for c in range(len(vs[0]))]


def attention_tiled(q, ks, vs, tile):
    """Process keys in tiles with a running max m, running denominator l, running output o."""
    d = len(q)
    m = float("-inf")
    l = 0.0
    o = [0.0] * len(vs[0])
    for start in range(0, len(ks), tile):
        s = [dot(q, k) / math.sqrt(d) for k in ks[start:start + tile]]
        m_new = max(m, max(s))
        scale = math.exp(m - m_new) if m != float("-inf") else 0.0
        p = [math.exp(v - m_new) for v in s]
        l = l * scale + sum(p)
        o = [oc * scale for oc in o]
        for pj, vj in zip(p, vs[start:start + tile]):
            for c in range(len(o)):
                o[c] += pj * vj[c]
        m = m_new
    return [oc / l for oc in o]


def layer_norm(x, eps=1e-5):
    mu = sum(x) / len(x)
    var = sum((v - mu) ** 2 for v in x) / len(x)
    return [(v - mu) / math.sqrt(var + eps) for v in x]


def rms_norm(x, eps=1e-5):
    rms = math.sqrt(sum(v * v for v in x) / len(x) + eps)
    return [v / rms for v in x]


def matvec(w, x):
    return [dot(row, x) for row in w]


def rand_matrix(rng, rows, cols, std):
    return [[rng.gauss(0, std) for _ in range(cols)] for _ in range(rows)]


def silu(v):
    return v / (1.0 + math.exp(-v))


class Block:
    """Pre-LN decoder block: x + MHA(norm(x)), then x + SwiGLU(norm(x))."""

    def __init__(self, rng, d, heads, d_ff):
        self.d, self.h, self.dh = d, heads, d // heads
        std = 1.0 / math.sqrt(d)
        self.wq, self.wk = rand_matrix(rng, d, d, std), rand_matrix(rng, d, d, std)
        self.wv, self.wo = rand_matrix(rng, d, d, std), rand_matrix(rng, d, d, std)
        self.wg = rand_matrix(rng, d_ff, d, std)
        self.wu = rand_matrix(rng, d_ff, d, std)
        self.wd = rand_matrix(rng, d, d_ff, 1.0 / math.sqrt(d_ff))

    def forward(self, xs, causal=True):
        n = len(xs)
        hs = [rms_norm(x) for x in xs]
        q = [matvec(self.wq, h) for h in hs]
        k = [matvec(self.wk, h) for h in hs]
        v = [matvec(self.wv, h) for h in hs]
        att = []
        for i in range(n):
            concat = []
            for head in range(self.h):
                sl = slice(head * self.dh, (head + 1) * self.dh)
                limit = i + 1 if causal else n
                ks = [k[j][sl] for j in range(limit)]
                vs = [v[j][sl] for j in range(limit)]
                concat.extend(attention_standard(q[i][sl], ks, vs))
            att.append(matvec(self.wo, concat))
        xs = [[a + b for a, b in zip(x, y)] for x, y in zip(xs, att)]
        out = []
        for x in xs:
            h = rms_norm(x)
            gate = [silu(g) for g in matvec(self.wg, h)]
            up = matvec(self.wu, h)
            ffn = matvec(self.wd, [g * u for g, u in zip(gate, up)])
            out.append([a + b for a, b in zip(x, ffn)])
        return out


def main():
    rng = random.Random(3)

    print("=== 1. Softmax overflow ===")
    logits = [1000.0, 999.0, 998.0]
    try:
        softmax_naive(logits)
    except OverflowError as err:
        print(f"naive softmax on {logits}: OverflowError ({err})")
    print(f"stable softmax: {[round(p, 4) for p in softmax_stable(logits)]}")
    print(f"stable softmax is shift-invariant: "
          f"{[round(p, 4) for p in softmax_stable([0.0, -1.0, -2.0])]}")

    print("\n=== 2. float16 limits ===")
    print(f"largest finite float16 = {to_fp16(65504.0)}; 65520 rounds to {to_fp16(65520.0)}")
    d_k = 128
    q = [23.0] * d_k
    k = [23.0] * d_k
    raw = dot(q, k)
    print(f"q.k with all entries 23.0 and d_k=128: {raw:.0f} -> as float16: {to_fp16(raw)}")
    print(f"scaling first (divide by sqrt(d_k)={math.sqrt(d_k):.2f}): {to_fp16(raw / math.sqrt(d_k)):.2f}")
    acc = 0.0
    for _ in range(4096):
        acc = to_fp16(acc + 1.0)
    print(f"summing 4096 ones with float16 accumulation: {acc:.0f} (true 4096)")
    acc32 = 0.0
    for _ in range(4096):
        acc32 += 1.0
    print(f"same sum with a wider accumulator: {acc32:.0f}")
    print(f"float16 has 11 significant bits: above 2048 the spacing is 2, so "
          f"2049 rounds to {to_fp16(2049.0):.0f}")

    print("\n=== 3. Online-softmax tiling equals standard attention ===")
    n, dh = 37, 8
    q = [rng.gauss(0, 1) for _ in range(dh)]
    ks = [[rng.gauss(0, 1) for _ in range(dh)] for _ in range(n)]
    vs = [[rng.gauss(0, 1) for _ in range(dh)] for _ in range(n)]
    ref = attention_standard(q, ks, vs)
    for tile in (1, 4, 16, 37):
        out = attention_tiled(q, ks, vs, tile)
        print(f"tile={tile:>2}: max abs difference = {max(abs(a - b) for a, b in zip(ref, out)):.2e}")

    print("\n=== 4. Residual stream growth: pre-LN stack of random sublayers ===")
    d = 64
    x = [rng.gauss(0, 1) for _ in range(d)]
    stds = {}
    for layer in range(1, 129):
        h = layer_norm(x)
        w = rand_matrix(rng, d, d, 1.0 / math.sqrt(d))
        update = matvec(w, h)
        x = [a + b for a, b in zip(x, update)]
        if layer in (1, 8, 32, 128):
            stds[layer] = math.sqrt(sum(v * v for v in x) / d)
    for layer, s in stds.items():
        print(f"after {layer:>3} sublayers: residual RMS = {s:5.2f}   "
              f"(sqrt(layers+1) = {math.sqrt(layer + 1):5.2f})")

    print("\n=== 5. Causality of a full pre-LN decoder block ===")
    block = Block(rng, d=16, heads=4, d_ff=32)
    xs = [[rng.gauss(0, 1) for _ in range(16)] for _ in range(6)]
    base = block.forward(xs, causal=True)
    xs2 = [row[:] for row in xs]
    xs2[5] = [rng.gauss(0, 1) for _ in range(16)]
    changed = block.forward(xs2, causal=True)
    diffs = [max(abs(a - b) for a, b in zip(r1, r2)) for r1, r2 in zip(base, changed)]
    print("max change per position after editing token 5 (causal):",
          [f"{v:.1e}" for v in diffs])
    assert all(v == 0.0 for v in diffs[:5])
    bi = block.forward(xs, causal=False)
    bi2 = block.forward(xs2, causal=False)
    diffs_bi = [max(abs(a - b) for a, b in zip(r1, r2)) for r1, r2 in zip(bi, bi2)]
    print("max change per position after editing token 5 (bidirectional):",
          [f"{v:.1e}" for v in diffs_bi])
    print("PASS: causal block does not leak future tokens.")


if __name__ == "__main__":
    main()
