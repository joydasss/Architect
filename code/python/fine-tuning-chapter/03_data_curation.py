"""Data curation for supervised fine-tuning (standard library only).

Shows (1) loss masking on completion tokens, (2) packing efficiency,
(3) exact and near-duplicate detection with word shingles and Jaccard
similarity, and (4) n-gram decontamination against a held-out test set.

Run: python 03_data_curation.py
"""
import re

# ---- 1. Loss masking -------------------------------------------------
prompt = "<|user|> classify: refund not received <|assistant|>"
completion = " billing_issue <|end|>"
p_tok, c_tok = prompt.split(), completion.split()
tokens = p_tok + c_tok
labels = [-100] * len(p_tok) + c_tok          # -100 = ignored by the loss
print("tokens :", tokens)
print("labels :", labels)
print(f"loss-bearing tokens = {sum(l != -100 for l in labels)} of {len(tokens)}")

# ---- 2. Packing ------------------------------------------------------
lengths = [180, 420, 95, 700, 310, 150, 60, 520, 240, 90]
ctx = 1024


def padded_batches(lengths):
    # one example per sequence, padded to ctx
    return len(lengths), sum(lengths) / (len(lengths) * ctx)


def packed(lengths):
    bins = []
    for n in sorted(lengths, reverse=True):          # first-fit decreasing
        for b in bins:
            if sum(b) + n <= ctx:
                b.append(n)
                break
        else:
            bins.append([n])
    return len(bins), sum(lengths) / (len(bins) * ctx)


for name, fn in (("padded", padded_batches), ("packed", packed)):
    seqs, util = fn(lengths)
    print(f"{name}: {seqs} sequences of {ctx}, useful-token fraction = {util:.2f}")

# ---- 3. Deduplication ------------------------------------------------
docs = {
    "a": "Please reset my password, I am locked out of my account.",
    "b": "please reset my password,  I am locked out of my account!",
    "c": "Please reset my password; I'm locked out of my account today.",
    "d": "The invoice total does not match the purchase order.",
}


def norm(t):
    return re.sub(r"[^a-z0-9 ]", "", t.lower()).split()


def shingles(t, k=3):
    w = norm(t)
    return {tuple(w[i:i + k]) for i in range(len(w) - k + 1)}


def jaccard(a, b):
    return len(a & b) / len(a | b)


keys = list(docs)
print("\nPairwise Jaccard on 3-word shingles:")
for i in range(len(keys)):
    for j in range(i + 1, len(keys)):
        a, b = keys[i], keys[j]
        exact = docs[a] == docs[b]
        print(f"  {a}-{b}: exact={exact!s:5}  jaccard={jaccard(shingles(docs[a]), shingles(docs[b])):.2f}")

# ---- 4. Decontamination ----------------------------------------------
train = ["the quarterly revenue rose by four percent on strong subscription growth",
         "customer asked to cancel the plan before renewal date"]
test = ["Quarterly revenue rose by four percent on strong subscription growth, said the CFO."]


def ngrams(t, n=6):
    w = norm(t)
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


test_grams = set().union(*(ngrams(t) for t in test))
for t in train:
    overlap = ngrams(t) & test_grams
    print(f"\ntrain example overlap with test (6-grams) = {len(overlap)} -> "
          f"{'DROP' if overlap else 'keep'}: {t[:50]}")
