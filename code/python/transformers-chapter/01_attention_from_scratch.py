"""Scaled dot-product attention from scratch (standard library only, no NumPy).

Prints three things that the chapter quotes:
1. A hand-checkable 3-token attention computation, with and without a causal mask.
2. A numeric check of the 1/sqrt(d_k) variance argument.
3. A mask test: with a causal mask, changing a future token must not change
   earlier outputs.

Run: python 01_attention_from_scratch.py
"""

import math
import random


def matmul(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def transpose(a):
    return [list(r) for r in zip(*a)]


def softmax(row):
    m = max(row)
    exps = [math.exp(v - m) for v in row]
    s = sum(exps)
    return [e / s for e in exps]


def attention(q, k, v, causal=False):
    d_k = len(k[0])
    scores = matmul(q, transpose(k))
    scores = [[s / math.sqrt(d_k) for s in row] for row in scores]
    if causal:
        for i, row in enumerate(scores):
            for j in range(len(row)):
                if j > i:
                    row[j] = float("-inf")
    weights = [softmax(row) for row in scores]
    return scores, weights, matmul(weights, v)


def fmt(m, nd=3):
    return "\n".join("  [" + ", ".join(f"{x:7.{nd}f}" for x in row) + "]" for row in m)


def worked_example():
    print("=== 1. Worked 3-token example (d_model=4, d_k=d_v=2) ===")
    # Three tokens: "the", "cat", "sat". Embeddings are chosen so the arithmetic is easy.
    x = [
        [1.0, 0.0, 0.0, 0.0],  # the
        [0.0, 1.0, 0.0, 0.0],  # cat
        [0.0, 0.0, 1.0, 1.0],  # sat
    ]
    wq = [[1, 0], [0, 1], [1, 0], [0, 1]]
    wk = [[1, 0], [0, 1], [0, 1], [1, 0]]
    wv = [[2, 0], [0, 2], [1, 0], [0, 1]]
    q = matmul(x, wq)
    k = matmul(x, wk)
    v = matmul(x, wv)
    print("Q =\n" + fmt(q, 1))
    print("K =\n" + fmt(k, 1))
    print("V =\n" + fmt(v, 1))
    raw = matmul(q, transpose(k))
    print("Raw scores QK^T =\n" + fmt(raw, 1))
    scores, weights, out = attention(q, k, v)
    print("Scaled scores (divide by sqrt(2)=%.4f) =\n" % math.sqrt(2) + fmt(scores, 3))
    print("Attention weights (rows sum to 1) =\n" + fmt(weights, 3))
    print("Output = weights @ V =\n" + fmt(out, 3))
    _, cw, cout = attention(q, k, v, causal=True)
    print("Causal attention weights =\n" + fmt(cw, 3))
    print("Causal output =\n" + fmt(cout, 3))


def variance_check():
    print("\n=== 2. Variance of q.k for unit-variance components ===")
    rng = random.Random(0)
    trials = 3000
    print(f"{'d_k':>6} {'var(q.k)':>10} {'var scaled':>11} {'mean max-weight raw':>20} {'scaled':>8}")
    for d_k in (4, 16, 64, 256, 1024):
        dots = []
        for _ in range(trials):
            q = [rng.gauss(0, 1) for _ in range(d_k)]
            k = [rng.gauss(0, 1) for _ in range(d_k)]
            dots.append(sum(a * b for a, b in zip(q, k)))
        mean = sum(dots) / trials
        var = sum((d - mean) ** 2 for d in dots) / trials
        # Saturation: one query against 16 keys, average of the largest softmax weight.
        raw_max = 0.0
        sc_max = 0.0
        n_soft = 100
        for _ in range(n_soft):
            q = [rng.gauss(0, 1) for _ in range(d_k)]
            row = []
            for _ in range(16):
                k = [rng.gauss(0, 1) for _ in range(d_k)]
                row.append(sum(a * b for a, b in zip(q, k)))
            raw_max += max(softmax(row))
            sc_max += max(softmax([r / math.sqrt(d_k) for r in row]))
        print(f"{d_k:>6} {var:>10.2f} {var / d_k:>11.2f} {raw_max / n_soft:>20.3f} {sc_max / n_soft:>8.3f}")


def mask_test():
    print("\n=== 3. Causal mask leak test ===")
    rng = random.Random(1)
    n, d = 5, 4
    x = [[rng.gauss(0, 1) for _ in range(d)] for _ in range(n)]
    _, _, base = attention(x, x, x, causal=True)
    x2 = [row[:] for row in x]
    x2[4] = [rng.gauss(0, 1) for _ in range(d)]  # change only the last (future) token
    _, _, changed = attention(x2, x2, x2, causal=True)
    diffs = [max(abs(a - b) for a, b in zip(r1, r2)) for r1, r2 in zip(base, changed)]
    print("max abs change per position after editing token 4 (causal):",
          ["%.1e" % d_ for d_ in diffs])
    _, _, base_u = attention(x, x, x, causal=False)
    _, _, changed_u = attention(x2, x2, x2, causal=False)
    diffs_u = [max(abs(a - b) for a, b in zip(r1, r2)) for r1, r2 in zip(base_u, changed_u)]
    print("max abs change per position after editing token 4 (no mask):",
          ["%.1e" % d_ for d_ in diffs_u])
    assert all(dv == 0.0 for dv in diffs[:4]), "causal mask leaks future information"
    print("PASS: positions 0-3 are unchanged under the causal mask.")


if __name__ == "__main__":
    worked_example()
    variance_check()
    mask_test()
