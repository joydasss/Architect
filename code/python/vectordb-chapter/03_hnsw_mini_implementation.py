"""CH21 Vector Databases: a small, from-scratch HNSW-style ANN index
(Section 4.3).

This is a deliberately simplified, two-layer (base layer + one sparse upper
layer) implementation of the Hierarchical Navigable Small World idea: nodes
are inserted with a bounded neighbor list built via greedy nearest-neighbor
search, a small fraction of nodes also get long-range edges in a sparse
upper layer, and search greedily descends from the upper layer into the
dense base layer -- the same shape as the Section 4.3 diagrams, at a scale
small enough to run and inspect directly rather than only via a library.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field

import numpy as np


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(
        (a @ b) / ((np.linalg.norm(a) + 1e-12) * (np.linalg.norm(b) + 1e-12))
    )


@dataclass
class MiniHNSW:
    """A minimal two-layer HNSW-style graph index."""

    max_neighbors: int = 8
    upper_layer_probability: float = 0.1
    vectors: dict[int, np.ndarray] = field(default_factory=dict)
    base_edges: dict[int, set[int]] = field(default_factory=dict)
    upper_edges: dict[int, set[int]] = field(default_factory=dict)
    upper_layer_nodes: set[int] = field(default_factory=set)
    entry_point: int | None = None
    _rng: np.random.Generator = field(default_factory=lambda: np.random.default_rng(7))

    def insert(self, node_id: int, vector: np.ndarray) -> None:
        self.vectors[node_id] = vector
        self.base_edges.setdefault(node_id, set())

        if self.entry_point is None:
            self.entry_point = node_id
            self.upper_layer_nodes.add(node_id)
            self.upper_edges.setdefault(node_id, set())
            return

        # Greedily find nearby existing nodes in the base layer (Section 4.3
        # step 2: greedy graph descent, applied here at insert time too).
        candidates = self._greedy_search(vector, self.entry_point, self.base_edges, top_k=self.max_neighbors)
        for neighbor_id in candidates:
            self._connect(node_id, neighbor_id, self.base_edges)

        # Probabilistically promote this node into the sparse upper layer
        # (Section 4.3 step 1: layer assignment).
        if self._rng.random() < self.upper_layer_probability:
            self.upper_layer_nodes.add(node_id)
            self.upper_edges.setdefault(node_id, set())
            for other in self.upper_layer_nodes:
                if other != node_id:
                    self._connect(node_id, other, self.upper_edges, cap=self.max_neighbors // 2)

    def _connect(self, a: int, b: int, edges: dict[int, set[int]], cap: int | None = None) -> None:
        limit = cap if cap is not None else self.max_neighbors
        edges.setdefault(a, set()).add(b)
        edges.setdefault(b, set()).add(a)
        for node in (a, b):
            if len(edges[node]) > limit:
                # Prune to the `limit` closest neighbors (bounded degree,
                # Section 4.3 step 3).
                ranked = sorted(
                    edges[node],
                    key=lambda n: -cosine_similarity(self.vectors[node], self.vectors[n]),
                )
                edges[node] = set(ranked[:limit])

    def _greedy_search(self, query: np.ndarray, start: int, edges: dict[int, set[int]], top_k: int) -> list[int]:
        visited = {start}
        best = [(-cosine_similarity(query, self.vectors[start]), start)]
        heapq.heapify(best)
        frontier = [start]

        improved = True
        while improved:
            improved = False
            for node in list(frontier):
                for neighbor in edges.get(node, ()):
                    if neighbor in visited:
                        continue
                    visited.add(neighbor)
                    score = -cosine_similarity(query, self.vectors[neighbor])
                    heapq.heappush(best, (score, neighbor))
                    frontier.append(neighbor)
                    improved = True

        ranked = sorted(best)[:top_k]
        return [node_id for _, node_id in ranked]

    def search(self, query: np.ndarray, k: int, ef_search: int = 10) -> list[int]:
        """Coarse-to-fine search: descend from the upper layer, then refine
        in the base layer with a beam of `ef_search` candidates (Section
        4.3 step 4)."""
        assert self.entry_point is not None, "Index is empty"

        current_best = self.entry_point
        if len(self.upper_layer_nodes) > 1:
            upper_candidates = self._greedy_search(query, self.entry_point, self.upper_edges, top_k=1)
            if upper_candidates:
                current_best = upper_candidates[0]

        beam = self._greedy_search(query, current_best, self.base_edges, top_k=max(ef_search, k))
        beam.sort(key=lambda n: -cosine_similarity(query, self.vectors[n]))
        return beam[:k]


def brute_force_top_k(query: np.ndarray, vectors: dict[int, np.ndarray], k: int) -> list[int]:
    scored = sorted(vectors, key=lambda n: -cosine_similarity(query, vectors[n]))
    return scored[:k]


def demo() -> None:
    rng = np.random.default_rng(3)
    n_points, dims = 500, 32
    all_vectors = {i: rng.normal(size=dims).astype(np.float32) for i in range(n_points)}

    index = MiniHNSW(max_neighbors=8, upper_layer_probability=0.1)
    for node_id, vector in all_vectors.items():
        index.insert(node_id, vector)

    query = rng.normal(size=dims).astype(np.float32)
    k = 5

    exact = brute_force_top_k(query, all_vectors, k)
    approx_low_beam = index.search(query, k=k, ef_search=3)
    approx_high_beam = index.search(query, k=k, ef_search=30)

    def recall(approx: list[int]) -> float:
        return len(set(approx) & set(exact)) / k

    print(f"True top-{k} (brute force):        {exact}")
    print(f"Approx top-{k} (ef_search=3):       {approx_low_beam}  recall={recall(approx_low_beam):.2f}")
    print(f"Approx top-{k} (ef_search=30):      {approx_high_beam}  recall={recall(approx_high_beam):.2f}")
    print("\nHigher ef_search trades more graph traversal for better recall,")
    print("exactly the tunable knob described in Section 4.3.")


if __name__ == "__main__":
    demo()
