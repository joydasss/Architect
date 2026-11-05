"""One LSTM step, one GRU step, parameter counts, and one attention step.

Standard library only. Run: python 02_lstm_gru_attention_step.py

The numbers printed here are the ones the chapter walks through by hand.
"""

import math


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def affine(w, u, b, x, h):
    return [sum(w[i][k] * x[k] for k in range(len(x)))
            + sum(u[i][k] * h[k] for k in range(len(h))) + b[i]
            for i in range(len(b))]


def fmt(v):
    return "[" + ", ".join("%.4f" % a for a in v) + "]"


def lstm_step():
    print("== LSTM step (input size 1, hidden size 2) ==")
    x, h, c = [1.0], [0.5, -0.5], [2.0, -1.0]
    Wf, Uf, bf = [[0.4], [0.2]], [[0.2, 0.0], [0.0, 0.2]], [1.0, 1.0]
    Wi, Ui, bi = [[0.3], [-0.3]], [[0.1, 0.1], [0.1, 0.1]], [0.0, 0.0]
    Wg, Ug, bg = [[1.0], [-1.0]], [[0.5, 0.0], [0.0, 0.5]], [0.0, 0.0]
    Wo, Uo, bo = [[0.2], [0.2]], [[0.1, 0.0], [0.0, 0.1]], [0.0, 0.0]
    zf = affine(Wf, Uf, bf, x, h)
    zi = affine(Wi, Ui, bi, x, h)
    zg = affine(Wg, Ug, bg, x, h)
    zo = affine(Wo, Uo, bo, x, h)
    f = [sigmoid(a) for a in zf]
    i = [sigmoid(a) for a in zi]
    g = [math.tanh(a) for a in zg]
    o = [sigmoid(a) for a in zo]
    c_new = [f[k] * c[k] + i[k] * g[k] for k in range(2)]
    h_new = [o[k] * math.tanh(c_new[k]) for k in range(2)]
    print("pre-activations  zf", fmt(zf), "zi", fmt(zi))
    print("                 zg", fmt(zg), "zo", fmt(zo))
    print("f", fmt(f), " i", fmt(i), " g", fmt(g), " o", fmt(o))
    print("keep  f*c_prev   ", fmt([f[k] * c[k] for k in range(2)]))
    print("write i*g        ", fmt([i[k] * g[k] for k in range(2)]))
    print("c_new            ", fmt(c_new))
    print("tanh(c_new)      ", fmt([math.tanh(a) for a in c_new]))
    print("h_new            ", fmt(h_new))
    print("dc_new/dc_prev (diagonal) = f =", fmt(f))


def gru_step():
    print("\n== GRU step (same sizes, same weights reused where sensible) ==")
    x, h = [1.0], [0.5, -0.5]
    Wz, Uz, bz = [[0.4], [0.2]], [[0.2, 0.0], [0.0, 0.2]], [1.0, 1.0]
    Wr, Ur, br = [[0.3], [-0.3]], [[0.1, 0.1], [0.1, 0.1]], [0.0, 0.0]
    Wn, Un, bn = [[1.0], [-1.0]], [[0.5, 0.0], [0.0, 0.5]], [0.0, 0.0]
    z = [sigmoid(a) for a in affine(Wz, Uz, bz, x, h)]
    r = [sigmoid(a) for a in affine(Wr, Ur, br, x, h)]
    rh = [r[k] * h[k] for k in range(2)]
    n = [math.tanh(a) for a in affine(Wn, Un, bn, x, rh)]
    h_new = [(1 - z[k]) * h[k] + z[k] * n[k] for k in range(2)]
    print("update z", fmt(z), " reset r", fmt(r))
    print("candidate n", fmt(n))
    print("h_new = (1-z)*h + z*n", fmt(h_new))


def param_counts():
    print("\n== Parameter counts (input d=128, hidden h=256, one layer) ==")
    d, h = 128, 256
    vanilla = h * (d + h) + h
    lstm = 4 * (h * (d + h) + h)
    gru = 3 * (h * (d + h) + h)
    print("vanilla RNN:", vanilla)
    print("GRU        :", gru, " ratio to vanilla %.1f" % (gru / vanilla))
    print("LSTM       :", lstm, " ratio to vanilla %.1f" % (lstm / vanilla))
    print("LSTM with two bias vectors (PyTorch layout): 4*h*(d+h) + 8*h =",
          4 * h * (d + h) + 8 * h)
    print("LSTM with projection-free 3 stacked layers (d=h=256):",
          4 * (256 * 512 + 256) * 3)


def softmax(v):
    m = max(v)
    e = [math.exp(a - m) for a in v]
    s = sum(e)
    return [a / s for a in e]


def attention_step():
    print("\n== One attention step over 3 encoder states ==")
    enc = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    s = [1.0, 0.0]
    # Luong dot-product score
    dot = [sum(a * b for a, b in zip(s, h)) for h in enc]
    a_dot = softmax(dot)
    ctx = [sum(a_dot[j] * enc[j][k] for j in range(3)) for k in range(2)]
    print("Luong dot scores", fmt(dot), "weights", fmt(a_dot), "context", fmt(ctx))
    # Bahdanau additive score: v^T tanh(Wa s + Ua h_j)
    Wa = [[0.5, 0.0], [0.0, 0.5]]
    Ua = [[0.5, 0.0], [0.0, 0.5]]
    v = [1.0, -1.0]
    scores = []
    for h in enc:
        t = [math.tanh(sum(Wa[i][k] * s[k] for k in range(2))
                       + sum(Ua[i][k] * h[k] for k in range(2))) for i in range(2)]
        scores.append(sum(v[i] * t[i] for i in range(2)))
    a_add = softmax(scores)
    ctx2 = [sum(a_add[j] * enc[j][k] for j in range(3)) for k in range(2)]
    print("Bahdanau scores", fmt(scores), "weights", fmt(a_add), "context", fmt(ctx2))
    print("sum of weights:", "%.4f" % sum(a_add))


if __name__ == "__main__":
    lstm_step()
    gru_step()
    param_counts()
    attention_step()
