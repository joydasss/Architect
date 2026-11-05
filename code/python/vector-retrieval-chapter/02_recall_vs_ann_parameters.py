"""Exact baseline versus an IVF-style approximate index (standard library only).

Measures recall@10 against brute force while sweeping nprobe, and reports a
machine-independent cost (distance computations per query) next to wall-clock
p50/p95 latency. It also shows a benchmark pitfall: queries copied from the
indexed set look easier than held-out queries.

Run: python 02_recall_vs_ann_parameters.py
"""

import math
import random
import statistics
import time
from operator import mul

SEED = 7
N, DIM, CLUSTERS, LISTS, K = 8000, 24, 40, 64, 10
NUM_QUERIES = 100


def normalize(v):
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


def dot(a, b):
    return sum(map(mul, a, b))


def make_data(rng):
    centers = [normalize([rng.gauss(0, 1) for _ in range(DIM)]) for _ in range(CLUSTERS)]

    def sample():
        c = rng.choice(centers)
        return normalize([x + rng.gauss(0, 0.35 / math.sqrt(DIM) * 2) for x in c])

    corpus = [sample() for _ in range(N)]
    held_out = [sample() for _ in range(NUM_QUERIES)]
    return corpus, held_out


def kmeans(points, k, rng, iters=8):
    cents = [list(p) for p in rng.sample(points, k)]
    for _ in range(iters):
        buckets = [[] for _ in range(k)]
        for p in points:
            best = max(range(k), key=lambda i: dot(p, cents[i]))
            buckets[best].append(p)
        for i, b in enumerate(buckets):
            if b:
                cents[i] = normalize([sum(col) / len(b) for col in zip(*b)])
    return cents


def build_ivf(corpus, rng):
    train = rng.sample(corpus, 2000)
    cents = kmeans(train, LISTS, rng)
    lists = [[] for _ in range(LISTS)]
    for idx, p in enumerate(corpus):
        best = max(range(LISTS), key=lambda i: dot(p, cents[i]))
        lists[best].append(idx)
    return cents, lists


def exact_topk(corpus, q, k=K):
    scored = sorted(((dot(q, p), i) for i, p in enumerate(corpus)), reverse=True)[:k]
    return [i for _, i in scored]


def ivf_topk(corpus, cents, lists, q, nprobe, k=K):
    order = sorted(range(LISTS), key=lambda i: dot(q, cents[i]), reverse=True)[:nprobe]
    cand = [i for li in order for i in lists[li]]
    scored = sorted(((dot(q, corpus[i]), i) for i in cand), reverse=True)[:k]
    return [i for _, i in scored], LISTS + len(cand)


def pct(values, p):
    s = sorted(values)
    return s[min(len(s) - 1, int(math.ceil(p / 100 * len(s))) - 1)]


def evaluate(corpus, cents, lists, queries, truth, nprobe):
    hits, lat, cost = 0, [], []
    for q, t in zip(queries, truth):
        t0 = time.perf_counter()
        got, c = ivf_topk(corpus, cents, lists, q, nprobe)
        lat.append((time.perf_counter() - t0) * 1000)
        cost.append(c)
        hits += len(set(got) & set(t))
    recall = hits / (len(queries) * K)
    return recall, statistics.mean(cost), pct(lat, 50), pct(lat, 95)


def main():
    rng = random.Random(SEED)
    corpus, held_out = make_data(rng)
    cents, lists = build_ivf(corpus, rng)
    sizes = [len(x) for x in lists]
    print(f"corpus={N} dim={DIM} lists={LISTS} list size min/mean/max={min(sizes)}/{N // LISTS}/{max(sizes)}")

    truth_held = [exact_topk(corpus, q) for q in held_out]
    t0 = time.perf_counter()
    for q in held_out[:20]:
        exact_topk(corpus, q)
    flat_ms = (time.perf_counter() - t0) / 20 * 1000
    print(f"exact (flat) scan: {N} distance computations per query, ~{flat_ms:.1f} ms per query\n")

    print("held-out queries: recall@10 versus nprobe")
    print(f"{'nprobe':>6} {'recall@10':>10} {'dist/query':>11} {'p50 ms':>8} {'p95 ms':>8}")
    for nprobe in (1, 2, 4, 8, 16, 32):
        r, c, p50, p95 = evaluate(corpus, cents, lists, held_out, truth_held, nprobe)
        print(f"{nprobe:>6} {r:>10.3f} {c:>11.0f} {p50:>8.2f} {p95:>8.2f}")

    # Pitfall: queries that are exact copies of indexed vectors.
    copies = [corpus[i] for i in rng.sample(range(N), NUM_QUERIES)]
    truth_copy = [exact_topk(corpus, q) for q in copies]
    print("\npitfall: queries copied from the corpus (self-match always found)")
    for nprobe in (1, 4):
        r, *_ = evaluate(corpus, cents, lists, copies, truth_copy, nprobe)
        rh, *_ = evaluate(corpus, cents, lists, held_out, truth_held, nprobe)
        print(f"  nprobe={nprobe}: copied-query recall@10={r:.3f}  held-out recall@10={rh:.3f}")


if __name__ == "__main__":
    main()
