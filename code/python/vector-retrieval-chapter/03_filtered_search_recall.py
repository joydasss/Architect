"""Why low-selectivity filters hurt approximate search (standard library only).

Builds a small k-nearest-neighbour graph over clustered vectors and compares
four strategies for a filtered top-10 query, as the filter becomes more
selective:

* post-filter: search globally for top-m, then drop non-matching items
* post-filter with oversampling (m = 10 x k)
* traversal that ignores non-matching nodes (filter applied while walking)
* pre-filter (exact scan of the matching subset)

Recall is measured against an exact filtered scan. The graph is a plain
greedy-search proximity graph, a simplified stand-in for HNSW layer 0.

Run: python 03_filtered_search_recall.py
"""

import heapq
import math
import random
from operator import mul

SEED = 11
N, DIM, CLUSTERS, DEG, K = 3000, 16, 30, 12, 10
EF = 40


def normalize(v):
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


def dot(a, b):
    return sum(map(mul, a, b))


def build(rng):
    centers = [normalize([rng.gauss(0, 1) for _ in range(DIM)]) for _ in range(CLUSTERS)]
    pts, cluster_of = [], []
    for _ in range(N):
        ci = rng.randrange(CLUSTERS)
        pts.append(normalize([x + rng.gauss(0, 0.12) for x in centers[ci]]))
        cluster_of.append(ci)
    return pts, cluster_of


def build_graph(pts):
    graph = []
    for i, p in enumerate(pts):
        sims = sorted(((dot(p, q), j) for j, q in enumerate(pts) if j != i), reverse=True)[:DEG]
        graph.append([j for _, j in sims])
    # make links bidirectional so the graph is navigable
    for i, nbrs in enumerate(list(graph)):
        for j in nbrs:
            if i not in graph[j]:
                graph[j].append(i)
    # a few long-range links keep clusters connected (HNSW upper layers play this role)
    rng = random.Random(SEED + 1)
    for i in range(len(pts)):
        for _ in range(2):
            j = rng.randrange(len(pts))
            if j != i and j not in graph[i]:
                graph[i].append(j)
                graph[j].append(i)
    return graph


def pick_entry(pts, q, rng, allowed=None, samples=60):
    """Best of a random sample, a crude stand-in for descending the upper HNSW layers."""
    pool = list(allowed) if allowed is not None else range(len(pts))
    cand = rng.sample(pool, min(samples, len(pool)))
    return max(cand, key=lambda i: dot(q, pts[i]))


def graph_search(pts, graph, q, ef, entry, allowed=None):
    """Best-first search. If allowed is given, only allowed nodes enter results,
    but the walk still needs a route: non-allowed nodes may be traversed only
    when traverse_through is True (see main for the two variants)."""
    visited = {entry}
    cand = [(-dot(q, pts[entry]), entry)]
    results = []
    if allowed is None or entry in allowed:
        results = [(dot(q, pts[entry]), entry)]
    while cand:
        negs, node = heapq.heappop(cand)
        s = -negs
        if len(results) >= ef and s < min(results)[0]:
            break
        for nb in graph[node]:
            if nb in visited:
                continue
            visited.add(nb)
            sc = dot(q, pts[nb])
            if allowed is not None and nb not in allowed:
                continue  # filtered traversal: drop the node and do not expand it
            heapq.heappush(cand, (-sc, nb))
            results.append((sc, nb))
            results = heapq.nlargest(ef, results)
    return [i for _, i in heapq.nlargest(K, results)], len(visited)


def graph_search_unfiltered(pts, graph, q, ef, entry):
    ids, _ = graph_search(pts, graph, q, ef, entry, None)
    return ids


def graph_ranked(pts, graph, q, m, entry):
    visited = {entry}
    cand = [(-dot(q, pts[entry]), entry)]
    results = [(dot(q, pts[entry]), entry)]
    while cand:
        negs, node = heapq.heappop(cand)
        if len(results) >= m and -negs < min(results)[0]:
            break
        for nb in graph[node]:
            if nb in visited:
                continue
            visited.add(nb)
            sc = dot(q, pts[nb])
            heapq.heappush(cand, (-sc, nb))
            results.append((sc, nb))
            results = heapq.nlargest(m, results)
    return [i for _, i in sorted(results, reverse=True)]


def exact_filtered(pts, q, allowed):
    scored = sorted(((dot(q, pts[i]), i) for i in allowed), reverse=True)[:K]
    return [i for _, i in scored]


def main():
    rng = random.Random(SEED)
    pts, cluster_of = build(rng)
    graph = build_graph(pts)
    queries = [normalize([x + rng.gauss(0, 0.12) for x in pts[rng.randrange(N)]]) for _ in range(60)]

    print(f"N={N} dim={DIM} graph degree~{DEG} ef={EF} k={K}; filter = random tag set of given selectivity")
    print(f"{'selectivity':>11} {'matches':>8} {'post(m=ef)':>11} {'post(m=10k)':>12} {'filtered walk':>14} {'pre-filter':>11}")
    for sel in (0.5, 0.2, 0.05, 0.01, 0.003):
        allowed = set(rng.sample(range(N), max(K, int(N * sel))))
        totals = {"post": 0, "over": 0, "walk": 0, "pre": 0}
        for q in queries:
            truth = set(exact_filtered(pts, q, allowed))
            entry = pick_entry(pts, q, rng)
            r_post = [i for i in graph_ranked(pts, graph, q, EF, entry) if i in allowed][:K]
            r_over = [i for i in graph_ranked(pts, graph, q, 10 * K, entry) if i in allowed][:K]
            r_walk, _ = graph_search(pts, graph, q, EF, pick_entry(pts, q, rng, allowed), allowed)
            totals["post"] += len(set(r_post) & truth)
            totals["over"] += len(set(r_over) & truth)
            totals["walk"] += len(set(r_walk) & truth)
            totals["pre"] += len(set(exact_filtered(pts, q, allowed)) & truth)
        denom = len(queries) * min(K, len(allowed))
        print(f"{sel:>11.3f} {len(allowed):>8d} {totals['post'] / denom:>11.3f} {totals['over'] / denom:>12.3f} "
              f"{totals['walk'] / denom:>14.3f} {totals['pre'] / denom:>11.3f}")
    print("\nnote: 'filtered walk' drops non-matching nodes without expanding them, so the graph")
    print("fragments as selectivity falls. Production engines repair this with extra edges or")
    print("by switching to an exact scan of the matching subset.")


if __name__ == "__main__":
    main()
