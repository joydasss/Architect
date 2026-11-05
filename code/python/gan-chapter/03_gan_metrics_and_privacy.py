"""Evaluation metrics and a memorization test for generative models (CH11).
Standard library only.

Four toy "generators" are scored against a real 2-D mixture of four Gaussians:
  good      fresh samples from the true distribution
  collapsed samples from only two of the four modes (mode dropping)
  gaussian  one Gaussian with the same mean and covariance as the real data
  memorizer copies of training points plus tiny noise

Metrics: FID in 2-D (closed form), k-nearest-neighbour precision and recall
(Kynkaanniemi et al., 2019 style), mode histogram with effective number of modes,
a distance-based membership-inference AUC computed from the generated set, and the
median distance to the closest training record (DCR) against a held-out baseline.
"""
import math
import random

rng = random.Random(7)
CENTERS = [(1.5, 1.5), (1.5, -1.5), (-1.5, 1.5), (-1.5, -1.5)]
STD = 0.2
N = 500
K = 3


def real(n):
    return [(rng.gauss(cx, STD), rng.gauss(cy, STD))
            for cx, cy in (CENTERS[rng.randrange(4)] for _ in range(n))]


def mean_cov(pts):
    n = len(pts)
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    sxx = sum((p[0] - mx) ** 2 for p in pts) / (n - 1)
    syy = sum((p[1] - my) ** 2 for p in pts) / (n - 1)
    sxy = sum((p[0] - mx) * (p[1] - my) for p in pts) / (n - 1)
    return (mx, my), [[sxx, sxy], [sxy, syy]]


def fid(a, b):
    (m1, c1), (m2, c2) = mean_cov(a), mean_cov(b)
    prod = [[sum(c1[i][k] * c2[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    tr = prod[0][0] + prod[1][1]
    det = prod[0][0] * prod[1][1] - prod[0][1] * prod[1][0]
    tr_sqrt = math.sqrt(max(tr + 2 * math.sqrt(max(det, 0.0)), 0.0))
    mean_term = (m1[0] - m2[0]) ** 2 + (m1[1] - m2[1]) ** 2
    return mean_term + c1[0][0] + c1[1][1] + c2[0][0] + c2[1][1] - 2 * tr_sqrt


def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def knn_radius(pts, k):
    radii = []
    for i, p in enumerate(pts):
        ds = sorted(dist(p, q) for j, q in enumerate(pts) if j != i)
        radii.append(ds[k - 1])
    return radii


def coverage_fraction(queries, support, radii):
    hit = 0
    for q in queries:
        if any(dist(q, s) <= r for s, r in zip(support, radii)):
            hit += 1
    return hit / len(queries)


def mode_hist(pts):
    counts = [0] * 4
    off = 0
    for p in pts:
        for k, c in enumerate(CENTERS):
            if dist(p, c) < 3 * STD:
                counts[k] += 1
                break
        else:
            off += 1
    return counts, off


def auc_member_score(members, nonmembers, generated):
    """Score = distance to nearest generated sample. Smaller means 'member'."""
    sm = [min(dist(p, g) for g in generated) for p in members]
    sn = [min(dist(p, g) for g in generated) for p in nonmembers]
    wins = 0.0
    for a in sm:
        for b in sn:
            wins += 1.0 if a < b else 0.5 if a == b else 0.0
    return wins / (len(sm) * len(sn))


train = real(N)
test = real(N)
(mu, cov) = mean_cov(train)
l11 = math.sqrt(cov[0][0])
l21 = cov[0][1] / l11
l22 = math.sqrt(cov[1][1] - l21 * l21)
generators = {
    "good": real(N),
    "collapsed": [(rng.gauss(cx, STD), rng.gauss(cy, STD))
                  for cx, cy in (CENTERS[rng.randrange(2)] for _ in range(N))],
    "gaussian": [(mu[0] + l11 * a, mu[1] + l21 * a + l22 * b)
                 for a, b in ((rng.gauss(0, 1), rng.gauss(0, 1)) for _ in range(N))],
    "memorizer": [(p[0] + rng.gauss(0, 0.005), p[1] + rng.gauss(0, 0.005)) for p in train],
}

real_radii = knn_radius(test, K)
print("reference: test set vs train set FID = %.3f" % fid(train, test))
print("%-10s %7s %9s %7s %7s  %s" % ("generator", "FID", "precision", "recall", "AUC_MI", "mode counts, off-mode, effective modes"))
for name, gen in generators.items():
    gen_radii = knn_radius(gen, K)
    precision = coverage_fraction(gen, test, real_radii)
    recall = coverage_fraction(test, gen, gen_radii)
    counts, off = mode_hist(gen)
    auc = auc_member_score(train, test, gen)
    tot = sum(counts)
    ent = -sum(c / tot * math.log(c / tot) for c in counts if c > 0)
    print("%-10s %7.3f %9.2f %7.2f %7.2f  %s  off=%d  eff_modes=%.2f"
          % (name, fid(gen, test), precision, recall, auc, counts, off, math.exp(ent)))

# Distance to closest record (DCR): how near is each generated point to a training point?
# Compare with the same distance for held-out real points, which are not copies by construction.
def median(values):
    values = sorted(values)
    mid = len(values) // 2
    return values[mid] if len(values) % 2 else 0.5 * (values[mid - 1] + values[mid])


baseline = median([min(dist(p, t) for t in train) for p in test])
print("DCR baseline (held-out real to nearest training record): median %.4f" % baseline)
for name, gen in generators.items():
    med = median([min(dist(g, t) for t in train) for g in gen])
    print("DCR %-10s median %.4f  ratio to baseline %.2f" % (name, med, med / baseline))
