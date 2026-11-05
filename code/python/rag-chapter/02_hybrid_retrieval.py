"""Hybrid retrieval with reciprocal rank fusion (standard library only).

Sparse side: BM25. Dense side: hand-assigned similarity fixtures that mimic an
embedding model (no downloads needed); a character-trigram TF-IDF cosine is
also printed as a surface-similarity proxy. The point is the fusion mechanics:
scores from the two lists are on different scales, so reciprocal rank fusion
(RRF) combines ranks only.
"""
import math
from collections import Counter

DOCS = {
    "d1": "Employees must submit expense claims within 30 days of return.",
    "d2": "Policy ER-4471 covers reimbursement of meals up to 60 USD per day.",
    "d3": "Business class flights require manager approval for trips over 6 hours.",
    "d4": "Staff can be repaid for food costs while travelling, capped daily.",
    "d5": "The cafeteria menu changes weekly and lists allergens.",
}


def tok(s):
    return [w.strip(".,").lower() for w in s.split()]


def bm25_scores(query, docs, k1=1.2, b=0.75):
    toks = {d: tok(t) for d, t in docs.items()}
    avg = sum(len(t) for t in toks.values()) / len(toks)
    n = len(toks)
    df = Counter(w for t in toks.values() for w in set(t))
    out = {}
    for d, t in toks.items():
        tf = Counter(t)
        s = 0.0
        for q in tok(query):
            if q not in tf:
                continue
            idf = math.log(1 + (n - df[q] + 0.5) / (df[q] + 0.5))
            s += idf * tf[q] * (k1 + 1) / (tf[q] + k1 * (1 - b + b * len(t) / avg))
        out[d] = s
    return out


def trigrams(s):
    s = " " + s.lower() + " "
    return Counter(s[i:i + 3] for i in range(len(s) - 2))


def trigram_scores(query, docs):
    vecs = {d: trigrams(t) for d, t in docs.items()}
    n = len(vecs)
    df = Counter(g for v in vecs.values() for g in v)
    idf = {g: math.log((1 + n) / (1 + c)) + 1 for g, c in df.items()}

    def w(v):
        return {g: c * idf.get(g, 1.0) for g, c in v.items()}

    q = w(trigrams(query))
    qn = math.sqrt(sum(x * x for x in q.values()))
    out = {}
    for d, v in vecs.items():
        dv = w(v)
        dot = sum(q[g] * dv.get(g, 0) for g in q)
        dn = math.sqrt(sum(x * x for x in dv.values()))
        out[d] = dot / (qn * dn)
    return out


def ranked(scores):
    return [d for d, _ in sorted(scores.items(), key=lambda x: -x[1])]


def rrf(lists, k=60):
    fused = Counter()
    for lst in lists:
        for rank, d in enumerate(lst, start=1):
            fused[d] += 1.0 / (k + rank)
    return fused


# Hand-assigned cosine similarities that mimic a real embedding model: it
# blurs the exact identifier in query 1 but matches the paraphrase in query 2.
# These are fixtures for the demo, not measured model output.
FIXTURE_DENSE = {
    "ER-4471": {"d1": 0.41, "d2": 0.44, "d3": 0.38, "d4": 0.47, "d5": 0.30},
    "money back for food while travelling": {
        "d1": 0.52, "d2": 0.58, "d3": 0.40, "d4": 0.83, "d5": 0.35},
}

if __name__ == "__main__":
    for query in ["ER-4471", "money back for food while travelling"]:
        sp = ranked(bm25_scores(query, DOCS))
        de = ranked(FIXTURE_DENSE[query])
        tg = ranked(trigram_scores(query, DOCS))
        print("  trigram TF-IDF proxy:", tg[:3])
        fu = rrf([sp, de])
        print(f"query: {query!r}")
        print("  sparse (BM25):   ", sp[:3])
        print("  dense proxy:     ", de[:3])
        print("  RRF fused:       ", [d for d, _ in fu.most_common(3)])
        print("  top fused score: ", round(fu.most_common(1)[0][1], 5))
    # Worked RRF arithmetic: a document ranked 1st in one list and 3rd in the
    # other, with k=60.
    print("RRF(rank1, rank3) =", round(1 / 61 + 1 / 63, 5))
    print("RRF(rank2, rank2) =", round(2 / 62, 5))
