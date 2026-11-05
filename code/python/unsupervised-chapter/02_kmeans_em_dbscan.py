"""k-means (Lloyd + k-means++), silhouette, 1-D Gaussian mixture EM, and DBSCAN.

Standard library only. Prints: a hand-checkable k-means run on 7 points,
inertia/silhouette versus k on 3 blobs, one EM step with responsibilities,
and k-means versus DBSCAN on two concentric rings.
Run: python 02_kmeans_em_dbscan.py
"""
import math
import random


def d2(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def mean(points):
    n = len(points)
    return tuple(sum(p[i] for p in points) / n for i in range(len(points[0])))


def lloyd(points, centroids, max_iter=100, verbose=False):
    centroids = list(centroids)
    labels = None
    for it in range(1, max_iter + 1):
        new = [min(range(len(centroids)), key=lambda j: d2(p, centroids[j])) for p in points]
        if new == labels:
            break
        labels = new
        for j in range(len(centroids)):
            members = [p for p, l in zip(points, labels) if l == j]
            if members:
                centroids[j] = mean(members)
        if verbose:
            sse = sum(d2(p, centroids[l]) for p, l in zip(points, labels))
            print("iter %d labels=%s SSE=%.3f" % (it, labels, sse))
            print("   centroids=%s" % [tuple(round(c, 3) for c in m) for m in centroids])
    sse = sum(d2(p, centroids[l]) for p, l in zip(points, labels))
    return labels, centroids, sse


def kmeanspp(points, k, rng):
    cents = [rng.choice(points)]
    while len(cents) < k:
        w = [min(d2(p, c) for c in cents) for p in points]
        r, acc = rng.random() * sum(w), 0.0
        for p, wi in zip(points, w):
            acc += wi
            if acc >= r:
                cents.append(p)
                break
    return cents


def best_of(points, k, rng, restarts=10):
    best = None
    for _ in range(restarts):
        res = lloyd(points, kmeanspp(points, k, rng))
        if best is None or res[2] < best[2]:
            best = res
    return best


def silhouette(points, labels):
    scores = []
    ks = sorted(set(labels))
    for i, p in enumerate(points):
        per = {}
        for q, l in zip(points, labels):
            per.setdefault(l, []).append(math.sqrt(d2(p, q)))
        own = per[labels[i]]
        if len(own) == 1:
            scores.append(0.0)
            continue
        a = sum(own) / (len(own) - 1)
        b = min(sum(v) / len(v) for l, v in per.items() if l != labels[i])
        scores.append((b - a) / max(a, b))
    return sum(scores) / len(scores)


def norm_pdf(x, mu, s):
    return math.exp(-0.5 * ((x - mu) / s) ** 2) / (s * math.sqrt(2 * math.pi))


def em_1d(xs, mus, sigmas, pis, iters, verbose_first=False):
    for t in range(iters):
        resp = []
        for x in xs:
            w = [pi * norm_pdf(x, m, s) for pi, m, s in zip(pis, mus, sigmas)]
            z = sum(w)
            resp.append([wi / z for wi in w])
        if verbose_first and t == 0:
            for x, r in zip(xs, resp):
                print("   x=%.1f  r=(%.4f, %.4f)" % (x, r[0], r[1]))
        for k in range(len(mus)):
            nk = sum(r[k] for r in resp)
            mus[k] = sum(r[k] * x for r, x in zip(resp, xs)) / nk
            sigmas[k] = math.sqrt(sum(r[k] * (x - mus[k]) ** 2 for r, x in zip(resp, xs)) / nk)
            pis[k] = nk / len(xs)
    ll = sum(math.log(sum(pi * norm_pdf(x, m, s) for pi, m, s in zip(pis, mus, sigmas))) for x in xs)
    return mus, sigmas, pis, ll


def dbscan(points, eps, min_pts):
    n = len(points)
    nbrs = [[j for j in range(n) if d2(points[i], points[j]) <= eps * eps] for i in range(n)]
    labels = [None] * n
    cid = 0
    for i in range(n):
        if labels[i] is not None:
            continue
        if len(nbrs[i]) < min_pts:
            labels[i] = -1
            continue
        labels[i] = cid
        stack = list(nbrs[i])
        while stack:
            j = stack.pop()
            if labels[j] == -1:
                labels[j] = cid
            if labels[j] is not None:
                continue
            labels[j] = cid
            if len(nbrs[j]) >= min_pts:
                stack.extend(nbrs[j])
        cid += 1
    return labels


def purity(labels, truth):
    tot = 0
    for c in set(labels):
        members = [t for l, t in zip(labels, truth) if l == c]
        tot += max(members.count(t) for t in set(members))
    return tot / len(labels)


def main():
    print("== Lloyd on 7 points, init at A and D ==")
    pts = [(1, 1), (1.5, 2), (3, 4), (5, 7), (3.5, 5), (4.5, 5), (3.5, 4.5)]
    lloyd(pts, [pts[0], pts[3]], verbose=True)

    print("\n== k selection on 3 blobs (150 points, 10 k-means++ restarts) ==")
    rng = random.Random(3)
    centers = [(0, 0), (6, 0), (3, 5)]
    blobs = [(rng.gauss(cx, 1), rng.gauss(cy, 1)) for cx, cy in centers for _ in range(50)]
    print("k  inertia   silhouette")
    for k in range(1, 7):
        labels, _, sse = best_of(blobs, k, rng)
        sil = silhouette(blobs, labels) if k > 1 else float("nan")
        print("%d  %8.1f  %.3f" % (k, sse, sil))

    print("\n== EM for a 2-component 1-D mixture ==")
    xs = [1.0, 1.2, 0.8, 4.0, 4.3, 3.7, 2.5]
    print("first E-step with mu=(0,5), sigma=(1,1), pi=(0.5,0.5):")
    m, s, p, ll = em_1d(xs, [0.0, 5.0], [1.0, 1.0], [0.5, 0.5], 1, verbose_first=True)
    print("after 1 iter: mu=(%.3f, %.3f) sigma=(%.3f, %.3f) pi=(%.3f, %.3f) loglik=%.3f" % (m[0], m[1], s[0], s[1], p[0], p[1], ll))
    m, s, p, ll = em_1d(xs, [0.0, 5.0], [1.0, 1.0], [0.5, 0.5], 50)
    print("after 50 iter: mu=(%.3f, %.3f) sigma=(%.3f, %.3f) pi=(%.3f, %.3f) loglik=%.3f" % (m[0], m[1], s[0], s[1], p[0], p[1], ll))

    print("\n== Two concentric rings: k-means versus DBSCAN ==")
    rng = random.Random(11)
    ring, truth = [], []
    for r, t in ((1.0, 0), (3.0, 1)):
        for _ in range(100):
            a = rng.random() * 2 * math.pi
            ring.append((r * math.cos(a) + rng.gauss(0, 0.08), r * math.sin(a) + rng.gauss(0, 0.08)))
            truth.append(t)
    km, _, _ = best_of(ring, 2, rng)
    print("k-means k=2 purity = %.3f" % purity(km, truth))
    for eps in (0.5, 1.0):
        db = dbscan(ring, eps, 5)
        print("DBSCAN eps=%.1f min_pts=5 clusters=%d noise=%d purity=%.3f"
              % (eps, len(set(db) - {-1}), db.count(-1), purity(db, truth)))


if __name__ == "__main__":
    main()
