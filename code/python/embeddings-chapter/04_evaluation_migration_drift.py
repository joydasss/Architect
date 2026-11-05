"""Chapter 16 (Embeddings): evaluation metrics, migration cost, drift checks.

NumPy only. Prints:
1. Recall@k, MRR and nDCG@k on a small labelled example.
2. Re-embedding cost and time for a corpus migration.
3. Why vectors from two models are not comparable (random rotation) and how
   an orthogonal Procrustes map recovers neighbours only when both spaces
   are related by a rotation.
4. A drift statistic: centroid shift and mean nearest-neighbour similarity.
"""
import math
import numpy as np

# ------------------------------------------------------------- 1. metrics
rankings = {  # query -> ranked doc ids returned
    "q1": ["a", "b", "c", "d", "e"],
    "q2": ["x", "y", "z", "w", "v"],
    "q3": ["m", "n", "o", "p", "q"],
}
relevant = {"q1": {"b"}, "q2": {"w", "y"}, "q3": {"zz"}}


def recall_at(k, r, rel):
    return len(set(r[:k]) & rel) / len(rel)


def rr(r, rel):
    for i, d in enumerate(r, 1):
        if d in rel:
            return 1.0 / i
    return 0.0


def ndcg(k, r, rel):
    dcg = sum(1.0 / math.log2(i + 1) for i, d in enumerate(r[:k], 1) if d in rel)
    ideal = sum(1.0 / math.log2(i + 1) for i in range(1, min(k, len(rel)) + 1))
    return dcg / ideal


print("== 1. Metrics ==")
for q in rankings:
    print("%s recall@3=%.2f  RR=%.3f  nDCG@5=%.3f" % (
        q, recall_at(3, rankings[q], relevant[q]), rr(rankings[q], relevant[q]),
        ndcg(5, rankings[q], relevant[q])))
print("mean recall@3 = %.3f  MRR = %.3f  mean nDCG@5 = %.3f" % (
    np.mean([recall_at(3, rankings[q], relevant[q]) for q in rankings]),
    np.mean([rr(rankings[q], relevant[q]) for q in rankings]),
    np.mean([ndcg(5, rankings[q], relevant[q]) for q in rankings])))

# ------------------------------------------------------ 2. migration cost
print("\n== 2. Re-embedding cost ==")
chunks, tok_per_chunk = 40_000_000, 300
tokens = chunks * tok_per_chunk
price_per_million = 0.10  # illustrative USD per 1M tokens, NOT a quote
print("tokens to re-embed: %.1f billion" % (tokens / 1e9))
print("API cost at $%.2f/1M tokens: $%s" % (price_per_million, format(tokens / 1e6 * price_per_million, ",.0f")))
tps = 400_000  # illustrative aggregate tokens per second for a self-hosted GPU pool
print("self-hosted at %s tokens/s: %.1f hours" % (format(tps, ","), tokens / tps / 3600))
dim = 1024
print("new index (fp32, %d-d): %.0f GB; dual-write holds old + new = %.0f GB" % (
    dim, chunks * dim * 4 / 1e9, 2 * chunks * dim * 4 / 1e9))

# --------------------------------------------- 3. incomparable spaces
rng = np.random.default_rng(3)
n, d = 3000, 64
A = rng.normal(size=(n, d))
A /= np.linalg.norm(A, axis=1, keepdims=True)
R, _ = np.linalg.qr(rng.normal(size=(d, d)))  # random rotation = "another model"
B = A @ R
queries = A[:200] + rng.normal(size=(200, d)) * 0.05
queries /= np.linalg.norm(queries, axis=1, keepdims=True)
truth = np.argmax(queries @ A.T, axis=1)
cross = np.argmax(queries @ B.T, axis=1)  # query from space A vs corpus in space B
print("\n== 3. Cross-space comparison ==")
print("same-space top-1 matches truth : %.3f" % (truth == truth).mean())
print("query in A, corpus in B top-1  : %.3f" % (cross == truth).mean())
U, _, Vt = np.linalg.svd(A[1000:2000].T @ B[1000:2000])  # fit map on 1000 anchor pairs
Rhat = U @ Vt
mapped = queries @ Rhat
print("after Procrustes map (rotation only): %.3f" % (np.argmax(mapped @ B.T, axis=1) == truth).mean())
# a genuinely different model: nonlinear distortion breaks the rotation assumption
B2 = np.tanh(3 * (A @ R + 0.3 * rng.normal(size=(n, d)))) 
B2 /= np.linalg.norm(B2, axis=1, keepdims=True)
U, _, Vt = np.linalg.svd(A[1000:2000].T @ B2[1000:2000])
mapped = queries @ (U @ Vt)
print("Procrustes against nonlinear/noisy model: %.3f" % (np.argmax(mapped @ B2.T, axis=1) == truth).mean())

# ---------------------------------------------------------- 4. drift
print("\n== 4. Drift statistics ==")
base = rng.normal(size=(2000, 32)) + rng.normal(size=(1, 32)) * 0.5
base /= np.linalg.norm(base, axis=1, keepdims=True)
ref = base[:1000]


def drift(batch, ref):
    c_shift = float(np.linalg.norm(batch.mean(0) - ref.mean(0)))
    nn = float((batch @ ref.T).max(1).mean())
    return c_shift, nn


same = base[1000:1500]
print("same distribution : centroid shift %.3f  mean NN-sim %.3f" % drift(same, ref))
shifted = rng.normal(size=(500, 32)) + rng.normal(size=(1, 32)) * 1.5
shifted /= np.linalg.norm(shifted, axis=1, keepdims=True)
print("new topic mix     : centroid shift %.3f  mean NN-sim %.3f" % drift(shifted, ref))
