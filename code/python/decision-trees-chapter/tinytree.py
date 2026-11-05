"""Minimal second-order regression tree used by scripts 02 and 03.

Standard library only. The tree is fitted on per-row gradients g and
Hessians h (XGBoost-style), which covers both cases in the chapter:

* Squared loss on target y with current prediction f: g = f - y, h = 1.
  With lam = 0 the leaf value is the mean residual.
* Plain regression tree (bagging, random forest): call with f = 0, so
  g = -y and h = 1, and the leaf value is the mean of y.

Leaf weight:  w = -G / (H + lam)
Split gain:   0.5 * (GL^2/(HL+lam) + GR^2/(HR+lam) - G^2/(H+lam)) - gamma
"""

import random


class Node:
    __slots__ = ("feat", "thr", "left", "right", "value")

    def __init__(self):
        self.feat = None
        self.thr = None
        self.left = None
        self.right = None
        self.value = 0.0


def _leaf_value(G, H, lam):
    return -G / (H + lam)


def build_tree(X, g, h, idx, depth, max_depth, lam=0.0, gamma=0.0,
               min_leaf=1, max_features=None, rng=None):
    node = Node()
    G = sum(g[i] for i in idx)
    H = sum(h[i] for i in idx)
    node.value = _leaf_value(G, H, lam)
    if depth >= max_depth or len(idx) < 2 * min_leaf:
        return node
    n_feat = len(X[0])
    feats = list(range(n_feat))
    if max_features is not None and max_features < n_feat:
        feats = rng.sample(feats, max_features)
    best = (0.0, None, None)  # gain, feature, threshold
    parent_score = G * G / (H + lam)
    for j in feats:
        order = sorted(idx, key=lambda i: X[i][j])
        GL = HL = 0.0
        for k in range(len(order) - 1):
            i = order[k]
            GL += g[i]
            HL += h[i]
            if X[i][j] == X[order[k + 1]][j]:
                continue
            if (k + 1) < min_leaf or (len(order) - k - 1) < min_leaf:
                continue
            GR, HR = G - GL, H - HL
            gain = 0.5 * (GL * GL / (HL + lam) + GR * GR / (HR + lam)
                          - parent_score) - gamma
            if gain > best[0] + 1e-12:
                best = (gain, j, 0.5 * (X[i][j] + X[order[k + 1]][j]))
    if best[1] is None:
        return node
    _, node.feat, node.thr = best
    left = [i for i in idx if X[i][node.feat] <= node.thr]
    right = [i for i in idx if X[i][node.feat] > node.thr]
    node.left = build_tree(X, g, h, left, depth + 1, max_depth, lam, gamma,
                           min_leaf, max_features, rng)
    node.right = build_tree(X, g, h, right, depth + 1, max_depth, lam, gamma,
                            min_leaf, max_features, rng)
    return node


def predict_one(node, x):
    while node.feat is not None:
        node = node.left if x[node.feat] <= node.thr else node.right
    return node.value


def fit_regression_tree(X, y, idx, max_depth, min_leaf=1, max_features=None,
                        rng=None):
    g = [-v for v in y]
    h = [1.0] * len(y)
    return build_tree(X, g, h, list(idx), 0, max_depth, 0.0, 0.0, min_leaf,
                      max_features, rng or random.Random(0))
