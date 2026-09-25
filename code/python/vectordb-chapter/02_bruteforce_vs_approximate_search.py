"""CH21 Vector Databases: brute-force exact k-NN vs. a simplified IVF-style
approximate search (Sections 4.2, 4.4).

Demonstrates the recall-vs-latency crossover from Section 4.2: brute-force
search is exact (100% recall) but scales linearly with collection size,
while a cluster-based approximate search only examines the closest clusters
(the same idea as an Inverted File index's nlist/nprobe from Section 4.4),
trading a small amount of recall for a large latency reduction as the
collection grows.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np


def cosine_similarity_matrix(query: np.ndarray, vectors: np.ndarray) -> np.ndarray:
    """Cosine similarity between one query vector and many stored vectors."""
    query_norm = query / (np.linalg.norm(query) + 1e-12)
    vectors_norm = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-12)
    return vectors_norm @ query_norm


def brute_force_search(query: np.ndarray, vectors: np.ndarray, k: int) -> np.ndarray:
    """Exact k-NN: score every vector, return the true top-k indices."""
    scores = cosine_similarity_matrix(query, vectors)
    return np.argsort(-scores)[:k]


@dataclass
class SimpleIVFIndex:
    """A minimal Inverted-File-style ANN index (Section 4.4).

    Real IVF implementations use k-means to learn centroids; this uses a
    fixed random sample of vectors as centroids to keep the example small
    and dependency-free, while preserving the same nlist/nprobe mechanics.
    """

    vectors: np.ndarray
    n_lists: int
    centroid_indices: np.ndarray
    assignments: np.ndarray

    @classmethod
    def build(cls, vectors: np.ndarray, n_lists: int, seed: int = 0) -> "SimpleIVFIndex":
        rng = np.random.default_rng(seed)
        centroid_indices = rng.choice(len(vectors), size=n_lists, replace=False)
        centroids = vectors[centroid_indices]
        # Assign every vector to its nearest centroid (Section 4.4 step 1).
        sims_to_centroids = vectors @ centroids.T
        assignments = np.argmax(sims_to_centroids, axis=1)
        return cls(vectors=vectors, n_lists=n_lists,
                    centroid_indices=centroid_indices, assignments=assignments)

    def search(self, query: np.ndarray, k: int, n_probe: int) -> np.ndarray:
        centroids = self.vectors[self.centroid_indices]
        centroid_scores = cosine_similarity_matrix(query, centroids)
        probed_clusters = np.argsort(-centroid_scores)[:n_probe]

        candidate_mask = np.isin(self.assignments, probed_clusters)
        candidate_indices = np.where(candidate_mask)[0]
        if len(candidate_indices) == 0:
            return np.array([], dtype=int)

        candidate_scores = cosine_similarity_matrix(query, self.vectors[candidate_indices])
        top_within_candidates = np.argsort(-candidate_scores)[:k]
        return candidate_indices[top_within_candidates]


def recall_at_k(approx_indices: np.ndarray, exact_indices: np.ndarray) -> float:
    if len(exact_indices) == 0:
        return 1.0
    return len(set(approx_indices) & set(exact_indices)) / len(exact_indices)


def run_comparison(n_vectors: int, dims: int, k: int, n_lists: int, n_probe: int) -> None:
    rng = np.random.default_rng(42)
    vectors = rng.normal(size=(n_vectors, dims)).astype(np.float32)
    query = rng.normal(size=(dims,)).astype(np.float32)

    start = time.perf_counter()
    exact = brute_force_search(query, vectors, k)
    brute_force_seconds = time.perf_counter() - start

    index = SimpleIVFIndex.build(vectors, n_lists=n_lists)
    start = time.perf_counter()
    approx = index.search(query, k=k, n_probe=n_probe)
    approx_seconds = time.perf_counter() - start

    print(f"n_vectors={n_vectors:>8} dims={dims:>4} "
          f"brute_force={brute_force_seconds * 1000:8.3f}ms "
          f"approx={approx_seconds * 1000:8.3f}ms "
          f"recall@{k}={recall_at_k(approx, exact):.2f}")


if __name__ == "__main__":
    print("Brute-force (exact) vs. IVF-style approximate search (Sections 4.2, 4.4)")
    print("As n_vectors grows, brute-force cost grows linearly while the")
    print("approximate search stays roughly flat, at a small recall cost.\n")
    for n_vectors in (1_000, 10_000, 100_000):
        run_comparison(n_vectors=n_vectors, dims=256, k=10, n_lists=64, n_probe=8)
