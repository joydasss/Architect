"""Chapter 16 (Embeddings): fusion, truncation, quantization, storage arithmetic.

NumPy only. Prints:
1. Reciprocal rank fusion (RRF) worked example.
2. Truncation of a vector whose variance is front-loaded (Matryoshka-like).
3. Scalar (int8), binary and product quantization: storage and recall@10.
4. Storage and latency arithmetic for bi-encoder vs late interaction.
"""
import numpy as np

# ------------------------------------------------------------------ 1. RRF
bm25 = ["d3", "d1", "d7", "d2", "d9"]
dense = ["d2", "d3", "d5", "d1", "d8"]
K = 60
scores = {}
for ranking in (bm25, dense):
    for r, doc in enumerate(ranking, start=1):
        scores[doc] = scores.get(doc, 0.0) + 1.0 / (K + r)
print("== 1. RRF (k=60) ==")
for doc, s in sorted(scores.items(), key=lambda kv: -kv[1]):
    print("%s  %.5f" % (doc, s))

# ----------------------------------------------------------- shared corpus
rng = np.random.default_rng(7)
N, D, NQ = 20000, 256, 1000
# Front-loaded variance: later dimensions carry less signal, as in Matryoshka training.
scale = 1.0 / np.sqrt(1 + np.arange(D) / 8.0)
X = rng.normal(size=(N, D)) * scale
src = rng.integers(0, N, NQ)  # each query is a noisy copy of one 'relevant' item
Q = X[src] + rng.normal(size=(NQ, D)) * scale * 2.0


def unit(M):
    return M / np.linalg.norm(M, axis=1, keepdims=True)


Xn, Qn = unit(X), unit(Q)


def recall_at_10(Xs, Qs):
    """Fraction of queries whose source item appears in the top 10."""
    approx = np.argsort(-(Qs @ Xs.T), axis=1)[:, :10]
    return float(np.mean([s in a for a, s in zip(approx, src)]))


# ---------------------------------------------------------- 2. truncation
print("\n== 2. Truncate then renormalise (success@10: source item in top 10) ==")
for d in (256, 128, 64, 32, 16):
    print("d=%3d  success@10 = %.3f   bytes/vector (fp32) = %d" % (
        d, recall_at_10(unit(Xn[:, :d]), unit(Qn[:, :d])), d * 4))

# --------------------------------------------------------- 3. quantization
print("\n== 3. Quantization (D=256) ==")
lo, hi = Xn.min(0), Xn.max(0)
step = (hi - lo) / 255.0
Xi = np.round((Xn - lo) / step)
Xdeq = Xi * step + lo
print("float32     : %4d bytes/vec  recall@10 = %.3f" % (D * 4, recall_at_10(Xn, Qn)))
print("int8 scalar : %4d bytes/vec  recall@10 = %.3f" % (D, recall_at_10(Xdeq, Qn)))
Xb = np.sign(Xn - 0.0)
Qb = np.sign(Qn)
print("binary 1-bit: %4d bytes/vec  recall@10 = %.3f (Hamming-equivalent dot)" % (D // 8, recall_at_10(Xb, Qb)))
# binary retrieve top-100, rescore with float32
cand = np.argsort(-(Qb @ Xb.T), axis=1)[:, :100]
hit = []
for i in range(NQ):
    sc = Xn[cand[i]] @ Qn[i]
    top = cand[i][np.argsort(-sc)[:10]]
    hit.append(float(src[i] in top))
print("binary + fp32 rescore of top-100: recall@10 = %.3f" % np.mean(hit))

# product quantization: M subspaces, 256 centroids each (1 byte per subspace)
def kmeans(P, k, iters=8, seed=0):
    r = np.random.default_rng(seed)
    C = P[r.choice(len(P), k, replace=False)].copy()
    for _ in range(iters):
        d2 = (P ** 2).sum(1, keepdims=True) - 2 * P @ C.T + (C ** 2).sum(1)
        a = d2.argmin(1)
        for j in range(k):
            m = a == j
            if m.any():
                C[j] = P[m].mean(0)
    return C, a


for M in (32, 16):
    sub = D // M
    recon = np.zeros_like(Xn)
    for m in range(M):
        sl = slice(m * sub, (m + 1) * sub)
        C, a = kmeans(Xn[:, sl], 256)
        recon[:, sl] = C[a]
    print("PQ M=%2d     : %4d bytes/vec  recall@10 = %.3f" % (M, M, recall_at_10(recon, Qn)))

# ----------------------------------------- 4. storage / latency arithmetic
print("\n== 4. Storage arithmetic ==")
docs, tokens_per_doc, dim_tok = 10_000_000, 200, 128
single = docs * 1024 * 4
multi = docs * tokens_per_doc * dim_tok * 2  # fp16
print("single-vector 1024-d fp32 : %.1f GB" % (single / 1e9))
print("late-interaction 128-d fp16 x 200 tokens: %.1f GB" % (multi / 1e9))
print("ratio: %.0fx" % (multi / single))
print("cross-encoder at 1,000 pairs/s: 100 candidates = %.2f s, whole corpus = %.1f h" % (
    100 / 1000, docs / 1000 / 3600))
