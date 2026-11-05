"""Hybrid retrieval fusion on a toy corpus (standard library only).

Compares lexical BM25, a toy "semantic" ranker (concept bags standing in for
embeddings), reciprocal rank fusion (RRF), and naive weighted score addition.
The point is mechanical: RRF uses ranks and ignores score scales, while a
weighted sum of raw scores is dominated by whichever scorer has the larger range.

Run: python 04_hybrid_fusion.py
"""

import math
from collections import Counter

DOCS = {
    "d1": "refund policy for annual plans within 30 days of purchase",
    "d2": "how to request your money back after cancelling a subscription",
    "d3": "error E-4021 means the payment token has expired",
    "d4": "reset your password using the account recovery page",
    "d5": "invoice and billing contact changes require an administrator",
    "d6": "returns and reimbursement rules for yearly subscriptions",
}

# Toy concept map: words that share a concept contribute to the same dimension.
CONCEPTS = {
    "refund": "money", "money": "money", "back": "money", "reimbursement": "money", "returns": "money",
    "cancelling": "cancel", "cancel": "cancel", "subscription": "plan", "subscriptions": "plan",
    "plans": "plan", "plan": "plan", "yearly": "plan", "annual": "plan",
    "password": "auth", "recovery": "auth", "reset": "auth", "account": "auth",
    "invoice": "billing", "billing": "billing", "payment": "billing", "token": "billing",
}


def tokens(text):
    return [t.strip(".,?").lower() for t in text.split()]


def bm25(query, k1=1.2, b=0.75):
    docs = {d: tokens(t) for d, t in DOCS.items()}
    avg = sum(len(v) for v in docs.values()) / len(docs)
    df = Counter(t for v in docs.values() for t in set(v))
    scores = {}
    for d, toks in docs.items():
        tf = Counter(toks)
        s = 0.0
        for q in tokens(query):
            if q in tf:
                idf = math.log(1 + (len(docs) - df[q] + 0.5) / (df[q] + 0.5))
                s += idf * tf[q] * (k1 + 1) / (tf[q] + k1 * (1 - b + b * len(toks) / avg))
        scores[d] = s
    return scores


def concept_vec(text):
    c = Counter(CONCEPTS[t] for t in tokens(text) if t in CONCEPTS)
    norm = math.sqrt(sum(v * v for v in c.values())) or 1.0
    return {k: v / norm for k, v in c.items()}


def semantic(query):
    q = concept_vec(query)
    out = {}
    for d, t in DOCS.items():
        v = concept_vec(t)
        out[d] = sum(q.get(k, 0.0) * v.get(k, 0.0) for k in q)
    return out


def ranked(scores):
    return [d for d, s in sorted(scores.items(), key=lambda x: (-x[1], x[0])) if s > 0]


def rrf(rank_lists, k=60):
    fused = Counter()
    for lst in rank_lists:
        for pos, d in enumerate(lst, start=1):
            fused[d] += 1.0 / (k + pos)
    return fused


def weighted(a, b, wa=0.5):
    return {d: wa * a[d] + (1 - wa) * b[d] for d in a}


def show(query):
    lex, sem = bm25(query), semantic(query)
    r_lex, r_sem = ranked(lex), ranked(sem)
    fused = rrf([r_lex, r_sem])
    wsum = weighted(lex, sem)
    print(f"query: {query!r}")
    print(f"  BM25 top3      : {r_lex[:3]}  scores {[round(lex[d], 2) for d in r_lex[:3]]}")
    print(f"  semantic top3  : {r_sem[:3]}  scores {[round(sem[d], 2) for d in r_sem[:3]]}")
    print(f"  RRF (k=60) top3: {ranked(fused)[:3]}  scores {[round(fused[d], 4) for d in ranked(fused)[:3]]}")
    print(f"  weighted 0.5/0.5 raw scores top3: {ranked(wsum)[:3]}")
    print()


if __name__ == "__main__":
    show("error E-4021")
    show("how do I get my money back for a yearly subscription")
    print("worked RRF: a document ranked 1st by one list and 4th by the other scores")
    print(f"  1/(60+1) + 1/(60+4) = {1 / 61 + 1 / 64:.5f}; ranked 2nd and 2nd scores {2 / 62:.5f}")
