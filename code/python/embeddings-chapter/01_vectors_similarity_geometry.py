"""Chapter 16 (Embeddings): distributional vectors and vector geometry.

Standard library plus NumPy only. Prints:
1. Dense vectors learned from co-occurrence counts (PPMI + SVD), the
   distributional hypothesis in miniature.
2. The cosine / dot / Euclidean equivalence for unit-norm vectors.
3. Anisotropy: a shared offset inflates every pairwise cosine.
4. Hubness: in high dimensions a few points appear in many neighbour lists.
"""
import numpy as np

# ---------------------------------------------------------------- 1. PPMI+SVD
corpus = [
    "the cat chased the mouse", "the dog chased the cat", "the cat ate fish",
    "the dog ate meat", "a mouse ate cheese", "the dog chased the mouse",
    "the bank approved the loan", "the bank raised the rate",
    "the lender approved the loan", "the lender raised the rate",
    "a loan needs a rate", "the bank denied the loan",
]
tokens = sorted({w for s in corpus for w in s.split()})
idx = {w: i for i, w in enumerate(tokens)}
V = len(tokens)
C = np.zeros((V, V))
window = 2
for s in corpus:
    ws = s.split()
    for i, w in enumerate(ws):
        for j in range(max(0, i - window), min(len(ws), i + window + 1)):
            if j != i:
                C[idx[w], idx[ws[j]]] += 1
total = C.sum()
pw = C.sum(1, keepdims=True) / total
pc = C.sum(0, keepdims=True) / total
with np.errstate(divide="ignore"):
    pmi = np.log((C / total) / (pw @ pc))
ppmi = np.where(np.isfinite(pmi) & (pmi > 0), pmi, 0.0)
U, S, _ = np.linalg.svd(ppmi)
d = 4
E = U[:, :d] * np.sqrt(S[:d])
En = E / np.linalg.norm(E, axis=1, keepdims=True)


def cos(a, b):
    return float(En[idx[a]] @ En[idx[b]])


print("== 1. PPMI + SVD vectors (V=%d, d=%d) ==" % (V, d))
for a, b in [("cat", "dog"), ("bank", "lender"), ("cat", "bank"), ("dog", "loan")]:
    print("cos(%s, %s) = %.3f" % (a, b, cos(a, b)))

# ------------------------------------------------- 2. metric equivalences
rng = np.random.default_rng(0)
A = rng.normal(size=(5, 8))
q = rng.normal(size=8)
An = A / np.linalg.norm(A, axis=1, keepdims=True)
qn = q / np.linalg.norm(q)
dot = An @ qn
l2sq = ((An - qn) ** 2).sum(1)
print("\n== 2. Unit-norm equivalence ==")
print("dot            :", np.round(dot, 3))
print("2 - 2*dot      :", np.round(2 - 2 * dot, 3))
print("squared L2     :", np.round(l2sq, 3))
print("same ranking   :", bool((np.argsort(-dot) == np.argsort(l2sq)).all()))
# without normalization the dot product ranking is dominated by norm
scale = np.array([1.0, 1.0, 10.0, 1.0, 1.0])  # item 2 has a large norm but a mediocre angle
raw = (A * scale[:, None]) @ q
cosr = ((A * scale[:, None]) @ q) / (np.linalg.norm(A * scale[:, None], axis=1) * np.linalg.norm(q))
print("raw dot top-1  :", int(np.argmax(raw)), " cosine top-1:", int(np.argmax(cosr)))

# ---------------------------------------------------------- 3. anisotropy
n, dim = 2000, 256
X = rng.normal(size=(n, dim))
offset = rng.normal(size=dim)
offset = offset / np.linalg.norm(offset) * 12.0  # shared direction, norm 12
Xo = X + offset


def mean_pairwise_cos(M, m=400):
    M = M[:m]
    M = M / np.linalg.norm(M, axis=1, keepdims=True)
    G = M @ M.T
    return float((G.sum() - m) / (m * (m - 1)))


print("\n== 3. Anisotropy ==")
print("mean cosine, centred random vectors : %.3f" % mean_pairwise_cos(X))
print("mean cosine, with shared offset     : %.3f" % mean_pairwise_cos(Xo))
Xc = Xo - Xo.mean(0)
print("mean cosine after mean-centring     : %.3f" % mean_pairwise_cos(Xc))

# ------------------------------------------------------------ 4. hubness
def skewness(x):
    x = np.asarray(x, float)
    return float(((x - x.mean()) ** 3).mean() / x.std() ** 3)


def hubness(dim, n=1500, k=10, seed=1):
    r = np.random.default_rng(seed)
    P = r.normal(size=(n, dim)) + r.normal(size=(1, dim)) * 0.3
    P = P / np.linalg.norm(P, axis=1, keepdims=True)
    G = P @ P.T
    np.fill_diagonal(G, -np.inf)
    nn = np.argpartition(-G, k, axis=1)[:, :k]
    counts = np.bincount(nn.ravel(), minlength=n)
    return counts.max(), skewness(counts), int((counts == 0).sum())


print("\n== 4. Hubness (k=10, n=1500) ==")
for dm in (3, 32, 512):
    mx, sk, zero = hubness(dm)
    print("dim=%3d  max k-occurrence=%3d  skew=%.2f  never-a-neighbour=%d" % (dm, mx, sk, zero))
