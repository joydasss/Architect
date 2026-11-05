"""Backpropagation through time (BPTT) and the product of Jacobians.

Standard library only (no NumPy). Run: python 01_bptt_gradient_decay.py

Parts:
  A. Scalar arithmetic behind vanishing and exploding gradients.
  B. Spectral norm of the Jacobian product dh_T/dh_{T-k} for a tanh RNN whose
     recurrent matrix is rho times an orthogonal matrix.
  C. A finite-difference check of a hand-written BPTT gradient.
  D. Global-norm gradient clipping on a toy gradient.
  E. The LSTM cell-state path: the product of forget gates.
"""

import math
import random


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))]
            for i in range(len(a))]


def matvec(a, v):
    return [sum(a[i][k] * v[k] for k in range(len(v))) for i in range(len(a))]


def transpose(a):
    return [list(r) for r in zip(*a)]


def random_orthogonal(n, rng):
    """Gram-Schmidt on random vectors gives an orthogonal matrix."""
    rows = []
    while len(rows) < n:
        v = [rng.gauss(0, 1) for _ in range(n)]
        for r in rows:
            d = sum(x * y for x, y in zip(v, r))
            v = [x - d * y for x, y in zip(v, r)]
        norm = math.sqrt(sum(x * x for x in v))
        if norm > 1e-6:
            rows.append([x / norm for x in v])
    return rows


def spectral_norm(a, iters=200):
    """Largest singular value by power iteration on A^T A."""
    n = len(a[0])
    v = [1.0 / math.sqrt(n)] * n
    ata = matmul(transpose(a), a)
    lam = 0.0
    for _ in range(iters):
        w = matvec(ata, v)
        lam = math.sqrt(sum(x * x for x in w))
        if lam == 0:
            return 0.0
        v = [x / lam for x in w]
    return math.sqrt(lam)


def part_a():
    print("== A. Scalar factors rho^k ==")
    for rho in (0.9, 1.0, 1.2):
        print("rho=%.1f  k=10: %.4g  k=50: %.4g  k=100: %.4g"
              % (rho, rho ** 10, rho ** 50, rho ** 100))


def part_b():
    print("\n== B. Spectral norm of dh_T/dh_(T-k), tanh RNN, n=8, T=100 ==")
    n, T = 8, 100
    rng = random.Random(0)
    q = random_orthogonal(n, rng)
    u = [[rng.gauss(0, 0.5) for _ in range(n)] for _ in range(n)]
    xs = [[rng.gauss(0, 1) for _ in range(n)] for _ in range(T)]
    ks = (1, 10, 25, 50, 100)
    print("%6s" % "rho" + "".join("%12s" % ("k=%d" % k) for k in ks))
    for rho in (0.5, 0.9, 1.0, 1.5, 3.0):
        w = [[rho * x for x in row] for row in q]
        h = [0.0] * n
        jacs = []
        for t in range(T):
            pre = [a + b for a, b in zip(matvec(w, h), matvec(u, xs[t]))]
            h = [math.tanh(p) for p in pre]
            d = [1 - x * x for x in h]
            jacs.append([[d[i] * w[i][j] for j in range(n)] for i in range(n)])
        row = "%6.1f" % rho
        prod = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
        out = {}
        for k in range(1, T + 1):
            # dh_T/dh_(T-k) = J_T J_(T-1) ... J_(T-k+1)
            prod = matmul(prod, jacs[T - k])
            if k in ks:
                out[k] = spectral_norm(prod)
        row += "".join("%12.3e" % out[k] for k in ks)
        print(row)


def bptt_loss_and_grads(w, u, b, xs, target):
    """Tanh RNN, loss = 0.5*||h_T - target||^2, returns loss, dW, dU, db."""
    n = len(w)
    hs = [[0.0] * n]
    for x in xs:
        pre = [p + q + r for p, q, r in zip(matvec(w, hs[-1]), matvec(u, x), b)]
        hs.append([math.tanh(p) for p in pre])
    loss = 0.5 * sum((a - c) ** 2 for a, c in zip(hs[-1], target))
    dw = [[0.0] * n for _ in range(n)]
    du = [[0.0] * len(xs[0]) for _ in range(n)]
    db = [0.0] * n
    dh = [a - c for a, c in zip(hs[-1], target)]
    for t in range(len(xs), 0, -1):
        dpre = [dh[i] * (1 - hs[t][i] ** 2) for i in range(n)]
        for i in range(n):
            db[i] += dpre[i]
            for j in range(n):
                dw[i][j] += dpre[i] * hs[t - 1][j]
            for j in range(len(xs[0])):
                du[i][j] += dpre[i] * xs[t - 1][j]
        dh = [sum(w[i][j] * dpre[i] for i in range(n)) for j in range(n)]
    return loss, dw, du, db


def part_c():
    print("\n== C. Finite-difference check of BPTT ==")
    rng = random.Random(1)
    n, m, T = 3, 2, 6
    w = [[rng.gauss(0, 0.6) for _ in range(n)] for _ in range(n)]
    u = [[rng.gauss(0, 0.6) for _ in range(m)] for _ in range(n)]
    b = [0.1, -0.1, 0.05]
    xs = [[rng.gauss(0, 1) for _ in range(m)] for _ in range(T)]
    target = [0.3, -0.2, 0.1]
    loss, dw, _, _ = bptt_loss_and_grads(w, u, b, xs, target)
    eps, worst = 1e-6, 0.0
    for i in range(n):
        for j in range(n):
            w[i][j] += eps
            lp = bptt_loss_and_grads(w, u, b, xs, target)[0]
            w[i][j] -= 2 * eps
            lm = bptt_loss_and_grads(w, u, b, xs, target)[0]
            w[i][j] += eps
            num = (lp - lm) / (2 * eps)
            rel = abs(num - dw[i][j]) / max(1e-12, abs(num) + abs(dw[i][j]))
            worst = max(worst, rel)
    print("loss=%.6f  max relative error over dW entries=%.2e" % (loss, worst))


def part_d():
    print("\n== D. Global-norm clipping ==")
    g = [30.0, -40.0, 0.0]
    norm = math.sqrt(sum(x * x for x in g))
    c = 5.0
    scale = min(1.0, c / norm)
    clipped = [x * scale for x in g]
    print("norm=%.1f  threshold=%.1f  scale=%.2f  clipped=%s  new norm=%.1f"
          % (norm, c, scale, clipped, math.sqrt(sum(x * x for x in clipped))))


def part_e():
    print("\n== E. LSTM cell path: product of forget gates over k steps ==")
    print("%10s %8s %12s %12s" % ("bias", "f", "f^50", "f^200"))
    for bias in (-2.0, 0.0, 1.0, 2.0, 5.0):
        f = 1 / (1 + math.exp(-bias))
        print("%10.1f %8.4f %12.3e %12.3e" % (bias, f, f ** 50, f ** 200))


if __name__ == "__main__":
    part_a()
    part_b()
    part_c()
    part_d()
    part_e()
