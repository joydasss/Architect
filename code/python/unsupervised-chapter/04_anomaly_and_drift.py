"""Anomaly scores and drift statistics (standard library only).

Prints: z-score versus MAD-based robust score on a contaminated sample, a small
isolation forest, Population Stability Index (PSI) on binned proportions, the
two-sample Kolmogorov-Smirnov (KS) statistic, a biased RBF Maximum Mean
Discrepancy (MMD), and a review-capacity threshold.
Run: python 04_anomaly_and_drift.py
"""
import math
import random


def robust_demo():
    xs = [10, 11, 9, 10, 12, 10, 11, 9, 10, 100]
    n = len(xs)
    mu = sum(xs) / n
    sd = math.sqrt(sum((x - mu) ** 2 for x in xs) / (n - 1))
    med = sorted(xs)[n // 2 - 1:n // 2 + 1]
    med = sum(med) / 2
    devs = sorted(abs(x - med) for x in xs)
    mad = (devs[n // 2 - 1] + devs[n // 2]) / 2
    print("mean=%.2f sd=%.2f z(100)=%.2f" % (mu, sd, (100 - mu) / sd))
    print("median=%.1f MAD=%.1f robust z(100)=0.6745*(100-median)/MAD=%.2f"
          % (med, mad, 0.6745 * (100 - med) / mad))


def c_factor(n):
    if n <= 1:
        return 0.0
    if n == 2:
        return 1.0
    h = math.log(n - 1) + 0.5772156649
    return 2 * h - 2 * (n - 1) / n


def build_tree(data, depth, limit, rng):
    if depth >= limit or len(data) <= 1:
        return ("leaf", len(data))
    dim = rng.randrange(len(data[0]))
    lo, hi = min(p[dim] for p in data), max(p[dim] for p in data)
    if lo == hi:
        return ("leaf", len(data))
    cut = rng.uniform(lo, hi)
    left = [p for p in data if p[dim] < cut]
    right = [p for p in data if p[dim] >= cut]
    return ("node", dim, cut, build_tree(left, depth + 1, limit, rng), build_tree(right, depth + 1, limit, rng))


def path_len(tree, p, depth=0):
    if tree[0] == "leaf":
        return depth + c_factor(tree[1])
    _, dim, cut, l, r = tree
    return path_len(l if p[dim] < cut else r, p, depth + 1)


def iforest_demo():
    rng = random.Random(5)
    data = [(rng.gauss(0, 1), rng.gauss(0, 1)) for _ in range(500)]
    psi, trees = 64, 100
    limit = math.ceil(math.log2(psi))
    forest = [build_tree(rng.sample(data, psi), 0, limit, rng) for _ in range(trees)]

    def score(p):
        e = sum(path_len(t, p) for t in forest) / trees
        return 2 ** (-e / c_factor(psi))

    for name, p in (("center (0,0)", (0.0, 0.0)), ("edge (2,2)", (2.0, 2.0)), ("outlier (6,6)", (6.0, 6.0))):
        print("score %-14s = %.3f" % (name, score(p)))
    print("c(64) = %.3f" % c_factor(64))


def psi(ref, cur):
    return sum((c - r) * math.log(c / r) for r, c in zip(ref, cur))


def ks_stat(a, b):
    a, b = sorted(a), sorted(b)
    i = j = 0
    d = 0.0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            i += 1
        else:
            j += 1
        d = max(d, abs(i / len(a) - j / len(b)))
    return d


def mmd2(a, b, gamma):
    def k(x, y):
        return math.exp(-gamma * (x - y) ** 2)
    kaa = sum(k(x, y) for x in a for y in a) / len(a) ** 2
    kbb = sum(k(x, y) for x in b for y in b) / len(b) ** 2
    kab = sum(k(x, y) for x in a for y in b) / (len(a) * len(b))
    return kaa + kbb - 2 * kab


def drift_demo():
    ref = [0.10, 0.20, 0.40, 0.20, 0.10]
    cur = [0.05, 0.15, 0.35, 0.25, 0.20]
    terms = ["%.4f" % ((c - r) * math.log(c / r)) for r, c in zip(ref, cur)]
    print("PSI terms:", terms, "PSI = %.4f" % psi(ref, cur))
    rng = random.Random(9)
    base = [rng.gauss(0, 1) for _ in range(500)]
    for shift in (0.0, 0.2, 0.5, 1.0):
        cur_s = [rng.gauss(shift, 1) for _ in range(500)]
        print("mean shift %.1f: KS = %.3f  MMD^2 = %.4f" % (shift, ks_stat(base, cur_s), mmd2(base[:200], cur_s[:200], 0.5)))
    print("KS critical value at alpha=0.05, n=m=500: %.3f" % (1.358 * math.sqrt(2 / 500)))


def capacity_demo():
    rng = random.Random(21)
    n = 100000
    scores = [rng.gauss(0, 1) for _ in range(n)]
    scores.sort(reverse=True)
    capacity = 200
    thr = scores[capacity - 1]
    print("score threshold for %d reviews per %d events: %.3f" % (capacity, n, thr))
    prevalence, recall = 0.001, 0.6
    tp = prevalence * n * recall
    print("if prevalence=0.1%% and the top %.1f%% captures %.0f%% of true cases: precision = %.2f"
          % (100 * capacity / n, 100 * recall, tp / capacity))


def lof_demo():
    pts, k = [0, 1, 2, 3, 10], 2

    def knn(i):
        ds = sorted((abs(pts[i] - pts[j]), j) for j in range(len(pts)) if j != i)
        return ds[:k]

    kd = [knn(i)[-1][0] for i in range(len(pts))]
    lrd = [k / sum(max(kd[j], abs(pts[i] - pts[j])) for _, j in knn(i)) for i in range(len(pts))]
    print("k-distance:", kd)
    print("lrd:", [round(x, 4) for x in lrd])
    for i in range(len(pts)):
        lof = sum(lrd[j] for _, j in knn(i)) / k / lrd[i]
        print("point %2d  LOF = %.3f" % (pts[i], lof))


def validation_demo():
    a, b = [1, 2], [8, 9, 10]
    ca, cb = sum(a) / 2, sum(b) / 3
    sa = sum(abs(x - ca) for x in a) / 2
    sb = sum(abs(x - cb) for x in b) / 3
    print("scatter A=%.3f B=%.3f centroid gap=%.1f  Davies-Bouldin = %.4f"
          % (sa, sb, abs(ca - cb), (sa + sb) / abs(ca - cb)))
    for x in (1, 2, 8, 9, 10):
        own, other = (a, b) if x in a else (b, a)
        ai = sum(abs(x - y) for y in own if y != x) / (len(own) - 1)
        bi = sum(abs(x - y) for y in other) / len(other)
        print("point %2d  a=%.3f b=%.3f s=%.3f" % (x, ai, bi, (bi - ai) / max(ai, bi)))


def single_complete_demo():
    pts = [0, 1, 3, 7, 9]
    for name, f in (("single", min), ("complete", max)):
        clusters = [[p] for p in pts]
        out = []
        while len(clusters) > 1:
            best = None
            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    d = f(abs(x - y) for x in clusters[i] for y in clusters[j])
                    if best is None or d < best[0]:
                        best = (d, i, j)
            d, i, j = best
            out.append("%s+%s@%g" % (clusters[i], clusters[j], d))
            clusters[i] = clusters[i] + clusters[j]
            del clusters[j]
        print(name + ":", "; ".join(out))


def main():
    print("== Local Outlier Factor, 1-D, k=2 ==")
    lof_demo()
    print("\n== Silhouette and Davies-Bouldin by hand ==")
    validation_demo()
    print("\n== Single versus complete linkage on 0,1,3,7,9 ==")
    single_complete_demo()
    print("\n== Contaminated sample ==")
    robust_demo()
    print("\n== Isolation forest (2-D Gaussian, 100 trees, subsample 64) ==")
    iforest_demo()
    print("\n== Drift statistics ==")
    drift_demo()
    print("\n== Review-capacity threshold ==")
    capacity_demo()


if __name__ == "__main__":
    main()
