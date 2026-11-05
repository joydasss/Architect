"""Gradient boosting from scratch (standard library only).

Requires tinytree.py in the same folder. Prints:

1. One boosting round of logistic loss on six rows, with gradients,
   Hessians, split gains, and leaf weights for lambda = 0 and lambda = 1.
2. Shrinkage: validation and test error versus learning rate with early
   stopping on a validation set.
3. Row subsampling (stochastic gradient boosting) at a fixed learning rate.
4. Extrapolation: boosted trees versus a straight line outside the
   training range.
"""

import math
import random

from tinytree import build_tree, predict_one


def boost_squared(X, y, rounds, lr, depth, rng, subsample=1.0, lam=0.0,
                  Xv=None, yv=None):
    """Squared-loss boosting. Returns trees, base value, validation curve."""
    n = len(y)
    base = sum(y) / n
    f = [base] * n
    trees, curve = [], []
    fv = [base] * len(Xv) if Xv else None
    for _ in range(rounds):
        g = [f[i] - y[i] for i in range(n)]
        h = [1.0] * n
        idx = list(range(n))
        if subsample < 1.0:
            idx = rng.sample(idx, int(subsample * n))
        t = build_tree(X, g, h, idx, 0, depth, lam, 0.0, 5, None, rng)
        trees.append(t)
        for i in range(n):
            f[i] += lr * predict_one(t, X[i])
        if Xv:
            for i in range(len(Xv)):
                fv[i] += lr * predict_one(t, Xv[i])
            curve.append(sum((fv[i] - yv[i]) ** 2
                             for i in range(len(yv))) / len(yv))
    return trees, base, curve


def predict(trees, base, lr, x):
    return base + lr * sum(predict_one(t, x) for t in trees)


def make(n, rng, noise=0.5):
    X = [[rng.uniform(-3, 3) for _ in range(3)] for _ in range(n)]
    y = [2 * math.sin(x[0]) + 0.5 * x[1] ** 2 + rng.gauss(0, noise)
         for x in X]
    return X, y


def logistic_round_demo():
    xs = [[1.0], [2.0], [3.0], [4.0], [5.0], [6.0]]
    ys = [0, 0, 1, 0, 1, 1]
    n = len(ys)
    p0 = sum(ys) / n
    f0 = math.log(p0 / (1 - p0))
    p = [1 / (1 + math.exp(-f0))] * n
    g = [p[i] - ys[i] for i in range(n)]
    h = [p[i] * (1 - p[i]) for i in range(n)]
    print(f"initial p={p0:.3f} f0={f0:.3f}")
    print("g =", [round(v, 3) for v in g], " h =", [round(v, 3) for v in h])
    G, H = sum(g), sum(h)
    for lam in (0.0, 1.0):
        print(f"-- lambda = {lam} --")
        best = None
        GL = HL = 0.0
        for k in range(n - 1):
            GL += g[k]
            HL += h[k]
            GR, HR = G - GL, H - HL
            gain = 0.5 * (GL * GL / (HL + lam) + GR * GR / (HR + lam)
                          - G * G / (H + lam))
            wl, wr = -GL / (HL + lam), -GR / (HR + lam)
            print(f"split after x={xs[k][0]:.0f}: GL={GL:+.3f} HL={HL:.3f}"
                  f" gain={gain:.4f} wL={wl:+.4f} wR={wr:+.4f}")
            if best is None or gain > best[0] + 1e-12:
                best = (gain, k, wl, wr)
        gain, k, wl, wr = best
        print(f"chosen: split after x={xs[k][0]:.0f}, gain={gain:.4f},"
              f" wL={wl:+.4f}, wR={wr:+.4f}")
        eta = 0.3
        newf = [f0 + eta * (wl if i <= k else wr) for i in range(n)]
        newp = [1 / (1 + math.exp(-v)) for v in newf]
        print(f"after eta={eta}: p =", [round(v, 3) for v in newp])


if __name__ == "__main__":
    print("== One logistic boosting round on six rows ==")
    logistic_round_demo()

    rng = random.Random(1)
    Xtr, ytr = make(300, rng)
    Xva, yva = make(150, rng)
    Xte, yte = make(600, rng)

    print("\n== Shrinkage and early stopping (depth 3, up to 400 rounds) ==")
    print("lr     best_round  val_MSE  test_MSE_at_best  test_MSE_at_400")
    for lr in (1.0, 0.3, 0.1, 0.03):
        trees, base, curve = boost_squared(Xtr, ytr, 400, lr, 3,
                                           random.Random(2), 1.0, 0.0,
                                           Xva, yva)
        b = min(range(len(curve)), key=curve.__getitem__)

        def test_mse(k):
            return sum((predict(trees[:k + 1], base, lr, x) - t) ** 2
                       for x, t in zip(Xte, yte)) / len(yte)
        print(f"{lr:<6} {b + 1:<11} {curve[b]:.3f}    {test_mse(b):.3f}"
              f"            {test_mse(399):.3f}")
    print("noise variance = 0.250")

    print("\n== Row subsampling at lr = 0.1 ==")
    for ss in (1.0, 0.5):
        trees, base, curve = boost_squared(Xtr, ytr, 400, 0.1, 3,
                                           random.Random(3), ss, 0.0,
                                           Xva, yva)
        b = min(range(len(curve)), key=curve.__getitem__)
        tm = sum((predict(trees[:b + 1], base, 0.1, x) - t) ** 2
                 for x, t in zip(Xte, yte)) / len(yte)
        print(f"subsample={ss}: best_round={b + 1} val_MSE={curve[b]:.3f}"
              f" test_MSE={tm:.3f}")

    print("\n== Extrapolation: y = 2x + 1 plus noise, train on x in [0, 10] ==")
    r = random.Random(4)
    xs = [[r.uniform(0, 10)] for _ in range(200)]
    ys = [2 * x[0] + 1 + r.gauss(0, 0.5) for x in xs]
    trees, base, _ = boost_squared(xs, ys, 300, 0.1, 3, random.Random(5))
    mx = sum(x[0] for x in xs) / len(xs)
    my = sum(ys) / len(ys)
    slope = (sum((x[0] - mx) * (y - my) for x, y in zip(xs, ys))
             / sum((x[0] - mx) ** 2 for x in xs))
    icpt = my - slope * mx
    print("x      truth   boosted  linear")
    for x in (2, 5, 9, 10, 12, 15, 20):
        print(f"{x:<6} {2 * x + 1:<7} {predict(trees, base, 0.1, [x]):<8.2f}"
              f" {slope * x + icpt:.2f}")
