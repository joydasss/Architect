"""Windowing, padding masks, carried state, and forecasting baselines.

Standard library only. Run: python 04_windowing_state_forecasting.py

Parts:
  A. Padding and masking: masked mean loss versus naive mean over padding.
  B. Streaming: carrying hidden state across chunks equals one full pass;
     resetting state at each chunk does not (the chunked-serving bug).
  C. Baselines on a synthetic seasonal series: naive, seasonal naive,
     simple exponential smoothing, and least-squares lag features.
  D. Train/serve skew: scaling with statistics from the full series (leaky)
     versus statistics from the training window only.
"""

import math
import random


def part_a():
    print("== A. Masked loss ==")
    # Three sequences of lengths 4, 2, 1 padded to length 4. Per-step losses.
    losses = [[1.0, 2.0, 3.0, 2.0], [4.0, 2.0, 0.0, 0.0], [3.0, 0.0, 0.0, 0.0]]
    lengths = [4, 2, 1]
    total = sum(sum(row[:n]) for row, n in zip(losses, lengths))
    real = sum(lengths)
    naive = sum(sum(row) for row in losses) / (len(losses) * 4)
    print("masked mean = %.0f / %d = %.4f" % (total, real, total / real))
    print("naive mean over padded grid = %.4f" % naive)


def rnn_step(h, x, w=0.8, u=0.5, b=0.1):
    return math.tanh(w * h + u * x + b)


def part_b():
    print("\n== B. Carried state across chunks ==")
    rng = random.Random(3)
    xs = [rng.gauss(0, 1) for _ in range(12)]
    h = 0.0
    for x in xs:
        h = rnn_step(h, x)
    full = h
    h = 0.0
    for chunk in (xs[:4], xs[4:8], xs[8:]):
        for x in chunk:
            h = rnn_step(h, x)
    carried = h
    h = 0.0
    for chunk in (xs[:4], xs[4:8], xs[8:]):
        h = 0.0  # state reset at every chunk
        for x in chunk:
            h = rnn_step(h, x)
    reset = h
    print("full pass h_T      = %.6f" % full)
    print("carried across 3   = %.6f  (diff %.1e)" % (carried, abs(full - carried)))
    print("reset each chunk   = %.6f  (diff %.3f)" % (reset, abs(full - reset)))


def series(n, rng):
    return [50 + 0.05 * t + 10 * math.sin(2 * math.pi * t / 7) + rng.gauss(0, 1)
            for t in range(n)]


def mae(a, b):
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


def solve(a, b):
    """Gaussian elimination with partial pivoting for small systems."""
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(m[r][c]))
        m[c], m[p] = m[p], m[c]
        for r in range(c + 1, n):
            f = m[r][c] / m[c][c]
            for k in range(c, n + 1):
                m[r][k] -= f * m[c][k]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (m[i][n] - sum(m[i][j] * x[j] for j in range(i + 1, n))) / m[i][i]
    return x


def part_c():
    print("\n== C. One-step-ahead baselines, season 7 ==")
    rng = random.Random(7)
    y = series(240, rng)
    split = 180
    test = list(range(split, len(y)))
    actual = [y[t] for t in test]
    naive = [y[t - 1] for t in test]
    snaive = [y[t - 7] for t in test]
    alpha, level, ses = 0.5, y[0], {}
    for t in range(1, len(y)):
        ses[t] = level  # forecast for t uses data up to t-1
        level = alpha * y[t] + (1 - alpha) * level
    ses_f = [ses[t] for t in test]
    lags = 8
    rows = [[1.0] + [y[t - k] for k in range(1, lags + 1)] for t in range(lags, split)]
    targ = [y[t] for t in range(lags, split)]
    p = lags + 1
    ata = [[sum(r[i] * r[j] for r in rows) for j in range(p)] for i in range(p)]
    for i in range(p):
        ata[i][i] += 1e-6
    atb = [sum(r[i] * v for r, v in zip(rows, targ)) for i in range(p)]
    coef = solve(ata, atb)
    lag_f = [coef[0] + sum(coef[k] * y[t - k] for k in range(1, lags + 1)) for t in test]
    for name, f in (("naive (y[t-1])", naive), ("seasonal naive (y[t-7])", snaive),
                    ("exp. smoothing a=0.5", ses_f), ("8 lag features, least squares", lag_f)):
        print("%-32s MAE = %.3f" % (name, mae(actual, f)))


def part_d():
    print("\n== D. Scaling leakage ==")
    rng = random.Random(11)
    y = [100 + 0.3 * t + rng.gauss(0, 2) for t in range(100)]
    train = y[:80]
    mu_tr = sum(train) / len(train)
    sd_tr = math.sqrt(sum((v - mu_tr) ** 2 for v in train) / len(train))
    mu_all = sum(y) / len(y)
    sd_all = math.sqrt(sum((v - mu_all) ** 2 for v in y) / len(y))
    print("train-only mean %.2f sd %.2f; full-series mean %.2f sd %.2f"
          % (mu_tr, sd_tr, mu_all, sd_all))
    last = y[-1]
    print("last value z-score: train stats %.2f, leaky stats %.2f"
          % ((last - mu_tr) / sd_tr, (last - mu_all) / sd_all))


if __name__ == "__main__":
    part_a()
    part_b()
    part_c()
    part_d()
