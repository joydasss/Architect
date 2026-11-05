"""Chapter 16 (Embeddings): a toy contrastive (InfoNCE) bi-encoder in NumPy.

The encoder is a single linear map over bag-of-words counts followed by L2
normalisation. Gradients are derived by hand (see the chapter). Pairs are
(query, document) samples that share a hidden topic. We compare temperatures
and show the effect of hard negatives. NumPy only; runs in a few seconds.
"""
import numpy as np

T, POOL, NOISE = 30, 100, 60  # topics, shared topic-word pool, noise words
V = POOL + NOISE
D_OUT = 16
# Each topic owns 8 words drawn from a pool of 100, so topics overlap in vocabulary.
_topic_words = np.random.default_rng(99).integers(0, POOL, size=(T, 8))


def sample_pairs(rng, n, topics=None):
    t = rng.integers(0, T, size=n) if topics is None else topics
    Xq = np.zeros((n, V))
    Xd = np.zeros((n, V))
    for i, tp in enumerate(t):
        for X, k in ((Xq, 3), (Xd, 5)):
            for w in rng.choice(_topic_words[tp], size=k):
                X[i, w] += 1
            for w in rng.integers(POOL, V, size=4):  # shared noise words
                X[i, w] += 1
    return Xq, Xd, t


def normalise(H):
    n = np.linalg.norm(H, axis=1, keepdims=True)
    return H / n, n


def backprop_norm(Z, n, dZ):
    return (dZ - Z * (Z * dZ).sum(1, keepdims=True)) / n


def train(tau, steps=150, batch=64, lr=0.5, hard=False, seed=0):
    rng = np.random.default_rng(seed)
    W = rng.normal(scale=0.1, size=(V, D_OUT))
    for _ in range(steps):
        Xq, Xd, t = sample_pairs(rng, batch)
        if hard:
            # every query gets a same-neighbourhood "hard" negative: a document from the adjacent topic
            Xn = sample_pairs(rng, batch, topics=(t + 1) % T)[1]
            Xd_all = np.vstack([Xd, Xn])
        else:
            Xd_all = Xd
        Q, nq = normalise(Xq @ W)
        Dm, nd = normalise(Xd_all @ W)
        S = Q @ Dm.T / tau
        S -= S.max(1, keepdims=True)
        P = np.exp(S)
        P /= P.sum(1, keepdims=True)
        Y = np.zeros_like(P)
        Y[np.arange(batch), np.arange(batch)] = 1
        G = (P - Y) / (batch * tau)  # dLoss/d(cosine) = (softmax - onehot) / (B * tau)
        dQ = G @ Dm
        dD = G.T @ Q
        dW = Xq.T @ backprop_norm(Q, nq, dQ) + Xd_all.T @ backprop_norm(Dm, nd, dD)
        W -= lr * dW
    return W


def evaluate(W, seed=123, n=512):
    rng = np.random.default_rng(seed)
    Xq, Xd, t = sample_pairs(rng, n)
    Q, _ = normalise(Xq @ W)
    Dm, _ = normalise(Xd @ W)
    S = Q @ Dm.T
    same = t[:, None] == t[None, :]
    pos_cos = S[np.arange(n), np.arange(n)].mean()
    neg_cos = S[~same].mean()
    # success: top-1 retrieved document comes from the right topic
    top1 = S.argmax(1)
    acc = (t[top1] == t).mean()
    return pos_cos, neg_cos, acc


rng0 = np.random.default_rng(0)
W0 = rng0.normal(scale=0.1, size=(V, D_OUT))
p, n_, a = evaluate(W0)
print("untrained        pos_cos=%.3f  neg_cos=%.3f  topic-top1=%.3f" % (p, n_, a))
for tau in (0.02, 0.1, 0.5, 2.0):
    W = train(tau)
    p, n_, a = evaluate(W)
    print("tau=%-5s        pos_cos=%.3f  neg_cos=%.3f  topic-top1=%.3f" % (tau, p, n_, a))
W = train(0.1, hard=True)
p, n_, a = evaluate(W)
print("tau=0.1 + hard   pos_cos=%.3f  neg_cos=%.3f  topic-top1=%.3f" % (p, n_, a))
