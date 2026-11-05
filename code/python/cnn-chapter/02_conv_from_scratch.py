"""Convolution from scratch on small grids.

Standard library only. Run: python 02_conv_from_scratch.py

Shows cross-correlation versus true convolution, an edge-detecting kernel,
translation equivariance, max pooling (and its limited invariance), a
transposed convolution, and the batch-normalization arithmetic used in the
chapter.
"""

import math


def cross_correlate(img, ker, stride=1, pad=0):
    h, w = len(img), len(img[0])
    k = len(ker)
    padded = [[0.0] * (w + 2 * pad) for _ in range(h + 2 * pad)]
    for i in range(h):
        for j in range(w):
            padded[i + pad][j + pad] = img[i][j]
    ho = (h + 2 * pad - k) // stride + 1
    wo = (w + 2 * pad - k) // stride + 1
    out = []
    for i in range(ho):
        row = []
        for j in range(wo):
            s = 0.0
            for a in range(k):
                for b in range(k):
                    s += padded[i * stride + a][j * stride + b] * ker[a][b]
            row.append(s)
        out.append(row)
    return out


def flip(ker):
    return [row[::-1] for row in ker[::-1]]


def max_pool(img, k=2, stride=2):
    ho = (len(img) - k) // stride + 1
    wo = (len(img[0]) - k) // stride + 1
    return [[max(img[i * stride + a][j * stride + b]
                 for a in range(k) for b in range(k))
             for j in range(wo)] for i in range(ho)]


def shift_right(img, n):
    return [[0.0] * n + row[:len(row) - n] for row in img]


def transposed_conv(inp, ker, stride=2):
    h, w, k = len(inp), len(inp[0]), len(ker)
    ho, wo = (h - 1) * stride + k, (w - 1) * stride + k
    out = [[0.0] * wo for _ in range(ho)]
    for i in range(h):
        for j in range(w):
            for a in range(k):
                for b in range(k):
                    out[i * stride + a][j * stride + b] += inp[i][j] * ker[a][b]
    return out


def show(name, grid):
    print(name)
    for row in grid:
        print("  " + " ".join(f"{v:5.1f}" for v in row))


def main():
    img = [[1, 2, 0, 1, 3],
           [0, 1, 3, 1, 2],
           [2, 1, 0, 0, 1],
           [1, 3, 2, 1, 0],
           [0, 1, 1, 2, 2]]
    img = [[float(v) for v in row] for row in img]
    ker = [[1.0, 0.0, -1.0],
           [2.0, 0.0, -2.0],
           [1.0, 0.0, -1.0]]

    print("=== Cross-correlation versus convolution (3x3 kernel, 5x5 image) ===")
    cc = cross_correlate(img, ker)
    cv = cross_correlate(img, flip(ker))
    show("cross-correlation (what deep-learning libraries compute)", cc)
    show("true convolution (kernel flipped)", cv)
    print("convolution equals negated cross-correlation here:",
          all(abs(cc[i][j] + cv[i][j]) < 1e-12 for i in range(3) for j in range(3)))

    print("\n=== Vertical step edge on an 8x8 image, Sobel-x kernel ===")
    edge = [[0.0] * 4 + [1.0] * 4 for _ in range(8)]
    resp = cross_correlate(edge, ker)
    print("one output row (6 values):", resp[0])

    print("\n=== Translation equivariance ===")
    blob = [[0.0] * 10 for _ in range(10)]
    for i in (3, 4, 5):
        for j in (2, 3, 4):
            blob[i][j] = 1.0
    shifted = shift_right(blob, 2)
    a = cross_correlate(blob, ker, pad=1)
    b = cross_correlate(shifted, ker, pad=1)
    a_shift = shift_right(a, 2)
    print("conv(shift(x)) == shift(conv(x)) away from borders:",
          all(abs(a_shift[i][j] - b[i][j]) < 1e-12
              for i in range(10) for j in range(2, 10)))

    print("\n=== Max pooling: 2x2 stride 2 ===")
    feat = [[1, 3, 2, 0], [4, 2, 1, 1], [0, 1, 5, 2], [2, 2, 3, 4]]
    feat = [[float(v) for v in row] for row in feat]
    show("pooled", max_pool(feat))
    one_px = [[0.0] * 4 for _ in range(4)]
    one_px[1][1] = 9.0
    moved = [[0.0] * 4 for _ in range(4)]
    moved[0][0] = 9.0
    moved2 = [[0.0] * 4 for _ in range(4)]
    moved2[1][2] = 9.0
    print("pooled(peak at (1,1)):", max_pool(one_px))
    print("pooled(peak at (0,0)) same cell, invariant:", max_pool(moved))
    print("pooled(peak at (1,2)) different cell, not invariant:", max_pool(moved2))

    print("\n=== Transposed convolution: 2x2 input, 3x3 kernel, stride 2 ===")
    tin = [[1.0, 2.0], [3.0, 4.0]]
    tk = [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    show("output 5x5 (overlap cells receive sums)", transposed_conv(tin, tk))

    print("\n=== Batch normalization on one channel ===")
    values = [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]
    mu = sum(values) / len(values)
    var = sum((v - mu) ** 2 for v in values) / len(values)
    eps = 1e-5
    norm = [(v - mu) / math.sqrt(var + eps) for v in values]
    print("mean:", mu, " variance:", var)
    print("normalized:", [round(v, 3) for v in norm])
    gamma, beta = 1.5, 0.5
    print("after gamma=1.5, beta=0.5:", [round(gamma * v + beta, 3) for v in norm])
    n_pix = 32 * 56 * 56
    print("values averaged per channel for batch 32 at 56x56:", n_pix)

    print("\n=== Folding batch norm into the preceding convolution ===")
    w, bias = 0.8, 0.1
    run_mu, run_var, g, bt = 0.5, 4.0, 1.5, 0.5
    scale = g / math.sqrt(run_var + eps)
    w_fold = w * scale
    b_fold = (bias - run_mu) * scale + bt
    x = 3.0
    unfolded = g * ((w * x + bias) - run_mu) / math.sqrt(run_var + eps) + bt
    folded = w_fold * x + b_fold
    print("unfolded:", round(unfolded, 6), " folded:", round(folded, 6))


if __name__ == "__main__":
    main()
