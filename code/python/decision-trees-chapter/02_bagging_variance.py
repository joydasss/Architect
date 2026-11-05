"""Bagging, random forest, correlation, and out-of-bag error (stdlib only).

Requires tinytree.py in the same folder. Prints:

1. Variance of one deep tree versus bagged trees versus a random forest,
   measured at fixed test points over repeated training sets.
2. The measured pairwise correlation of tree predictions and a check of
   Var(average) = rho*sigma^2 + (1-rho)*sigma^2/B.
3. Out-of-bag (OOB) error versus held-out error.

Runtime is roughly one to two minutes in pure Python.
"""

import math
import random

from tinytree import fit_regression_tree, predict_one

N_FEAT = 6
N_TRAIN = 300
N_TEST = 60
DEPTH = 8


def truth(x):
    return (3 * math.sin(2 * x[0]) + 2 * x[1] * x[2] + x[3]
            + (2.0 if x[4] > 0 else -2.0))


def make(n, rng, noise=1.0):
    X = [[rng.uniform(-2, 2) for _ in range(N_FEAT)] for _ in range(n)]
    y = [truth(x) + rng.gauss(0, noise) for x in X]
    return X, y


def fit_forest(X, y, n_trees, max_features, rng, bootstrap=True):
    n = len(y)
    trees, oob_sets = [], []
    for _ in range(n_trees):
        if bootstrap:
            idx = [rng.randrange(n) for _ in range(n)]
        else:
            idx = list(range(n))
        t = fit_regression_tree(X, y, idx, DEPTH, 1, max_features, rng)
        trees.append(t)
        oob_sets.append(set(range(n)) - set(idx))
    return trees, oob_sets


def forest_predict(trees, x):
    return sum(predict_one(t, x) for t in trees) / len(trees)


def mean(v):
    return sum(v) / len(v)


def var(v):
    m = mean(v)
    return sum((a - m) ** 2 for a in v) / (len(v) - 1)


if __name__ == "__main__":
    rng = random.Random(7)
    Xte, _ = make(N_TEST, random.Random(99))
    yte_true = [truth(x) for x in Xte]

    configs = [("single deep tree", 1, None, False),
               ("bagging B=25 (all features)", 25, None, True),
               ("random forest B=25 (m=2 of 6)", 25, 2, True)]
    R = 30
    preds = {c[0]: [] for c in configs}
    tree_preds_example = []
    for r in range(R):
        X, y = make(N_TRAIN, rng)
        for name, B, m, boot in configs:
            trees, _ = fit_forest(X, y, B, m, rng, boot)
            preds[name].append([forest_predict(trees, x) for x in Xte])
            if name.startswith("random forest") and r == 0:
                tree_preds_example = [[predict_one(t, x) for x in Xte]
                                      for t in trees]

    print("== Variance and squared bias at the test points ==")
    print(f"({R} training sets of {N_TRAIN} rows, noise sd 1.0)")
    print(f"{'model':<32}{'avg variance':>13}{'avg bias^2':>12}{'sum':>8}")
    for name, *_ in configs:
        P = preds[name]
        v = mean([var([P[r][j] for r in range(R)]) for j in range(N_TEST)])
        b2 = mean([(mean([P[r][j] for r in range(R)]) - yte_true[j]) ** 2
                   for j in range(N_TEST)])
        print(f"{name:<32}{v:>13.3f}{b2:>12.3f}{v + b2:>8.3f}")

    print("\n== Correlation between two trees (over training sets) ==")
    print("rho = Cov(tree A, tree B) / Var(tree) across fresh training sets;")
    print("A and B share a training set but use independent randomisation.")
    RR = 100
    B = 25
    for label, m in (("bagging", None), ("random forest m=2", 2)):
        rng2 = random.Random(21)
        covs, vars_, fvars_cols = [], [], []
        A_all, B_all, F_all = [], [], []
        for _ in range(RR):
            X, y = make(N_TRAIN, rng2)
            ta, _ = fit_forest(X, y, 1, m, rng2, True)
            tb, _ = fit_forest(X, y, 1, m, rng2, True)
            fo, _ = fit_forest(X, y, B, m, rng2, True)
            A_all.append([predict_one(ta[0], x) for x in Xte])
            B_all.append([predict_one(tb[0], x) for x in Xte])
            F_all.append([forest_predict(fo, x) for x in Xte])
        cov = mean([
            sum((A_all[r][j] - mean([A_all[k][j] for k in range(RR)]))
                * (B_all[r][j] - mean([B_all[k][j] for k in range(RR)]))
                for r in range(RR)) / (RR - 1) for j in range(N_TEST)])
        sig2 = mean([(var([A_all[r][j] for r in range(RR)])
                      + var([B_all[r][j] for r in range(RR)])) / 2
                     for j in range(N_TEST)])
        rho = cov / sig2
        pred = rho * sig2 + (1 - rho) * sig2 / B
        meas = mean([var([F_all[r][j] for r in range(RR)])
                     for j in range(N_TEST)])
        print(f"{label:<18} sigma^2={sig2:.3f} rho={rho:.3f}"
              f"  formula Var(B={B})={pred:.3f}  measured={meas:.3f}")
    print("\n== Out-of-bag error versus held-out error ==")
    X, y = make(300, random.Random(5))
    Xh, yh = make(600, random.Random(6))
    trees, oob = fit_forest(X, y, 60, 2, random.Random(3), True)
    se, cnt = 0.0, 0
    for i in range(len(y)):
        ts = [t for t, s in zip(trees, oob) if i in s]
        if ts:
            se += (mean([predict_one(t, X[i]) for t in ts]) - y[i]) ** 2
            cnt += 1
    held = mean([(forest_predict(trees, x) - t) ** 2 for x, t in zip(Xh, yh)])
    train = mean([(forest_predict(trees, x) - t) ** 2 for x, t in zip(X, y)])
    frac = mean([len(s) / len(y) for s in oob])
    print(f"rows with at least one OOB tree: {cnt}/{len(y)}")
    print(f"average OOB fraction per tree: {frac:.3f}"
          f" (theory (1-1/n)^n = {(1 - 1 / 300) ** 300:.3f}, limit 0.368)")
    print(f"training MSE (in-bag) = {train:.3f}")
    print(f"OOB MSE               = {se / cnt:.3f}")
    print(f"held-out MSE          = {held:.3f}")
    print("noise variance        = 1.000")
