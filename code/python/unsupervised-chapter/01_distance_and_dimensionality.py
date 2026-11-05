"""Distance measures and the curse of dimensionality (standard library only).

Prints: (1) metric disagreements on tiny examples, (2) distance concentration
for random points as dimension grows, (3) cube/ball volume ratios.
Run: python 01_distance_and_dimensionality.py
"""
import math
import random


def euclid(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def cosine_sim(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def mahalanobis_2d(x, mu, cov):
    (a, b), (c, d) = cov
    det = a * d - b * c
    inv = ((d / det, -b / det), (-c / det, a / det))
    v = (x[0] - mu[0], x[1] - mu[1])
    q = v[0] * (inv[0][0] * v[0] + inv[0][1] * v[1]) + v[1] * (inv[1][0] * v[0] + inv[1][1] * v[1])
    return math.sqrt(q)


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b)


def edit_distance(s, t):
    prev = list(range(len(t) + 1))
    for i, cs in enumerate(s, 1):
        cur = [i]
        for j, ct in enumerate(t, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (cs != ct)))
        prev = cur
    return prev[-1]


def main():
    print("== Metric examples ==")
    x, y = (1.0, 2.0), (2.0, 4.0)
    print("euclid((1,2),(2,4)) = %.3f, cosine = %.3f" % (euclid(x, y), cosine_sim(x, y)))
    cov = ((1.0, 0.9), (0.9, 1.0))
    for p in [(1.0, 1.0), (1.0, -1.0)]:
        print("point %s: euclid from origin = %.3f, mahalanobis = %.3f"
              % (p, euclid(p, (0, 0)), mahalanobis_2d(p, (0, 0), cov)))
    a, b = {"milk", "bread", "eggs"}, {"bread", "eggs", "jam", "tea"}
    print("jaccard = %.3f (|inter|=%d, |union|=%d)" % (jaccard(a, b), len(a & b), len(a | b)))
    print("edit_distance(kitten, sitting) =", edit_distance("kitten", "sitting"))

    print("\n== Distance concentration (500 uniform points, 1 query, 20 trials avg) ==")
    print("dim  (dmax-dmin)/dmin")
    rng = random.Random(7)
    for d in (2, 10, 100, 1000):
        ratios = []
        for _ in range(20):
            q = [rng.random() for _ in range(d)]
            ds = [euclid(q, [rng.random() for _ in range(d)]) for _ in range(500)]
            ratios.append((max(ds) - min(ds)) / min(ds))
        print("%4d  %.3f" % (d, sum(ratios) / len(ratios)))

    print("\n== Volume facts ==")
    print("dim  ball(r=0.5)/cube  outer 5%-shell share of unit cube")
    for d in (2, 3, 10, 20, 50):
        ball = math.pi ** (d / 2) / math.gamma(d / 2 + 1) * 0.5 ** d
        shell = 1 - 0.9 ** d  # points within 0.05 of any face
        print("%3d  %.2e          %.3f" % (d, ball, shell))


if __name__ == "__main__":
    main()
