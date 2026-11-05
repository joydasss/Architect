"""CART by hand on a ten-row loan table (standard library only).

Prints parent impurity, every candidate split for the income feature,
a categorical split ordered by class mean, the best depth-2 tree, the
cost-complexity pruning table, and a missing-value default-direction
example. The numbers are quoted in the chapter (Sections 3 to 7).
"""

import math
from math import log2

# id, income (thousand), debt-to-income ratio, region, default (1 = yes)
ROWS = [
    (1, 25, 0.45, "A", 1),
    (2, 32, 0.40, "B", 1),
    (3, 38, 0.41, "A", 0),
    (4, 41, 0.50, "C", 1),
    (5, 48, 0.30, "B", 0),
    (6, 55, 0.37, "A", 1),
    (7, 60, 0.25, "C", 0),
    (8, 72, 0.20, "B", 0),
    (9, 80, 0.38, "A", 0),
    (10, 95, 0.15, "C", 0),
]


def gini(ys):
    n = len(ys)
    if n == 0:
        return 0.0
    p = sum(ys) / n
    return 1.0 - p * p - (1 - p) * (1 - p)


def entropy(ys):
    n = len(ys)
    p = sum(ys) / n
    return -sum(q * log2(q) for q in (p, 1 - p) if q > 0)


def weighted(imp, left, right):
    n = len(left) + len(right)
    return len(left) / n * imp(left) + len(right) / n * imp(right)


def best_numeric(rows, col):
    rows = sorted(rows, key=lambda r: r[col])
    ys = [r[4] for r in rows]
    out = []
    for k in range(1, len(rows)):
        if rows[k - 1][col] == rows[k][col]:
            continue
        thr = (rows[k - 1][col] + rows[k][col]) / 2
        L, R = ys[:k], ys[k:]
        out.append((thr, len(L), sum(L), len(R), sum(R), gini(L), gini(R),
                    weighted(gini, L, R)))
    return out


def build(rows, depth, max_depth, path="root"):
    """Greedy CART on Gini; returns nested dict and prints the choices."""
    ys = [r[4] for r in rows]
    node = {"n": len(ys), "pos": sum(ys), "gini": gini(ys)}
    if depth == max_depth or gini(ys) == 0 or len(rows) < 2:
        return node
    best = None
    for col, name in ((1, "income"), (2, "dti")):
        for c in best_numeric(rows, col):
            if best is None or c[-1] < best[0] - 1e-12:
                best = (c[-1], name, col, round(c[0], 3))
    if best is None:
        return node
    w, name, col, thr = best
    print(f"{'  ' * depth}{path}: n={len(ys)} pos={sum(ys)} gini={gini(ys):.4f}"
          f" -> split {name} <= {thr} (weighted child gini {w:.4f})")
    node.update(feat=name, thr=thr)
    node["left"] = build([r for r in rows if r[col] <= thr], depth + 1,
                         max_depth, "L")
    node["right"] = build([r for r in rows if r[col] > thr], depth + 1,
                          max_depth, "R")
    return node


def leaves(node):
    if "left" not in node:
        return [node]
    return leaves(node["left"]) + leaves(node["right"])


def misclass(node):
    return sum(min(l["pos"], l["n"] - l["pos"]) for l in leaves(node))


if __name__ == "__main__":
    ys = [r[4] for r in ROWS]
    print("== Parent impurity ==")
    print(f"positives={sum(ys)} of {len(ys)}  gini={gini(ys):.4f}"
          f"  entropy={entropy(ys):.4f} bits")

    print("\n== Candidate thresholds on income (Gini) ==")
    print("thr   nL posL nR posR giniL  giniR  weighted  gain")
    for t, nl, pl, nr, pr, gl, gr, w in best_numeric(ROWS, 1):
        print(f"{t:<5} {nl:<3} {pl:<4} {nr:<3} {pr:<4} {gl:.4f} {gr:.4f}"
              f" {w:.4f}    {gini(ys) - w:.4f}")

    print("\n== Same thresholds scored by entropy (information gain) ==")
    srt = sorted(ROWS, key=lambda r: r[1])
    sy = [r[4] for r in srt]
    for k in range(1, len(srt)):
        L, R = sy[:k], sy[k:]
        ig = entropy(sy) - weighted(entropy, L, R)
        print(f"thr {(srt[k-1][1] + srt[k][1]) / 2:<5} IG={ig:.4f}")

    print("\n== Categorical split on region (order by default rate) ==")
    rate = {}
    for reg in "ABC":
        v = [r[4] for r in ROWS if r[3] == reg]
        rate[reg] = sum(v) / len(v)
        print(f"region {reg}: n={len(v)} pos={sum(v)} rate={rate[reg]:.4f}")
    order = sorted(rate, key=rate.get)
    for k in range(1, len(order)):
        Lset = set(order[:k])
        L = [r[4] for r in ROWS if r[3] in Lset]
        R = [r[4] for r in ROWS if r[3] not in Lset]
        print(f"left={sorted(Lset)} weighted gini={weighted(gini, L, R):.4f}")

    print("\n== Greedy CART, max depth 2 ==")
    tree = build(ROWS, 0, 2)
    print("leaves:", [(l["n"], l["pos"]) for l in leaves(tree)])

    print("\n== Cost-complexity pruning (weakest link) ==")
    print("-- growing the full tree --")
    full = build(ROWS, 0, 10)
    n = len(ROWS)

    def err(nd):  # misclassified count if nd were a leaf
        return min(nd["pos"], nd["n"] - nd["pos"])

    def subtree_err(nd):
        return sum(err(l) for l in leaves(nd))

    def internal(nd):
        return [] if "left" not in nd else (
            [nd] + internal(nd["left"]) + internal(nd["right"]))

    step = 0
    while "left" in full:
        print(f"step {step}: leaves={len(leaves(full))}"
              f" resubstitution error={subtree_err(full)}/{n}")
        cands = []
        for nd in internal(full):
            T = len(leaves(nd))
            a = (err(nd) - subtree_err(nd)) / n / (T - 1)
            cands.append((a, nd))
        a_min = min(c[0] for c in cands)
        print(f"   alpha_min = {a_min:.4f}; collapse")
        for a, nd in cands:
            if abs(a - a_min) < 1e-12:
                for key in ("left", "right", "feat", "thr"):
                    nd.pop(key, None)
        step += 1
    print(f"step {step}: leaves=1 resubstitution error={subtree_err(full)}/{n}")

    print("\n== AdaBoost with stumps on ten points ==")
    xs = list(range(1, 11))
    lab = [1, 1, 1, -1, -1, -1, 1, 1, 1, -1]
    w = [1 / 10] * 10
    F = [0.0] * 10
    for rnd in range(1, 4):
        best = None
        for t in [k + 0.5 for k in range(0, 10)]:
            for sgn in (1, -1):
                pred = [sgn if x > t else -sgn for x in xs]
                e = sum(wi for wi, p, y in zip(w, pred, lab) if p != y)
                if best is None or e < best[0] - 1e-12:
                    best = (e, t, sgn, pred)
        e, t, sgn, pred = best
        a = 0.5 * math.log((1 - e) / e)
        w = [wi * math.exp(-a * y * p)
             for wi, y, p in zip(w, lab, pred)]
        z = sum(w)
        w = [wi / z for wi in w]
        F = [f + a * p for f, p in zip(F, pred)]
        wrong = [x for x, p, y in zip(xs, pred, lab) if p != y]
        print(f"round {rnd}: stump x>{t} sign={sgn:+d} eps={e:.4f}"
              f" alpha={a:.4f} Z={z:.4f} wrong at x={wrong}")
        print("   new weights:", [round(v, 4) for v in w])
        errs = sum(1 for f, y in zip(F, lab) if (1 if f > 0 else -1) != y)
        print(f"   ensemble training errors after round {rnd}: {errs}/10")

    print("\n== Instability: flip the label of id 6 ==")
    flipped = [r if r[0] != 6 else (6, 55, 0.37, "A", 0) for r in ROWS]
    for label, data in (("original", ROWS), ("id 6 flipped", flipped)):
        cands = []
        for col, name in ((1, "income"), (2, "dti")):
            for c in best_numeric(data, col):
                cands.append((round(c[-1], 4), name, round(c[0], 3)))
        cands.sort()
        print(f"{label}: best root splits (weighted Gini, feature, thr):",
              cands[:3])

    print("\n== Surrogate agreement with income <= 57.5 ==")
    prim = {r[0]: r[1] <= 57.5 for r in ROWS}
    sur = {r[0]: r[2] <= 0.335 for r in ROWS}
    agree = sum(prim[i] == sur[i] for i in prim) / len(prim)
    print(f"dti <= 0.335 same direction: {agree:.2f}; flipped: {1 - agree:.2f};"
          f" majority baseline: {max(sum(prim.values()), 10 - sum(prim.values())) / 10:.2f}")

    print("\n== Missing-value default direction ==")
    # income <= 57.5 split; income of row 6 (pos) and row 9 (neg) missing
    known = [r for r in ROWS if r[0] not in (6, 9)]
    miss = [r for r in ROWS if r[0] in (6, 9)]
    base_L = [r[4] for r in known if r[1] <= 57.5]
    base_R = [r[4] for r in known if r[1] > 57.5]
    for side in ("left", "right"):
        L = base_L + ([r[4] for r in miss] if side == "left" else [])
        R = base_R + ([r[4] for r in miss] if side == "right" else [])
        print(f"missing -> {side}: weighted gini="
              f"{weighted(gini, L, R):.4f}  left={len(L)} right={len(R)}")
