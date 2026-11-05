"""Context assembly: deduplicate, budget, and order retrieved passages.

Standard library only. Tokens are whitespace words. Shows (1) near-duplicate
removal by word-set Jaccard overlap, (2) greedy packing under a token budget
with a per-source cap, and (3) edge-first ordering that places the strongest
passages at the start and end of the context to counter lost-in-the-middle.
"""

CANDIDATES = [
    # (chunk_id, source, score, text)
    ("a#1", "travel.pdf", 0.92, "Business class is allowed for flights of 6 hours or more with manager approval."),
    ("a#2", "travel.pdf", 0.90, "Business class is allowed for flights of 6 hours or more, with manager approval required."),
    ("b#1", "faq.html", 0.85, "Exceptions to the 14 day booking rule need the cost-center owner to sign the form."),
    ("c#1", "finance.pdf", 0.80, "Exceptions over 2000 USD also need finance approval before the booking is made."),
    ("a#3", "travel.pdf", 0.78, "Economy class is required for flights under 6 hours."),
    ("d#1", "hr.docx", 0.60, "Contractors may travel only with written approval from a director."),
]


def jaccard(a, b):
    sa, sb = set(a.lower().split()), set(b.lower().split())
    return len(sa & sb) / len(sa | sb)


def dedupe(cands, threshold=0.7):
    kept = []
    for c in sorted(cands, key=lambda x: -x[2]):
        if all(jaccard(c[3], k[3]) < threshold for k in kept):
            kept.append(c)
    return kept


def pack(cands, budget, per_source_cap=2):
    used, per_src, out = 0, {}, []
    for c in cands:
        n = len(c[3].split())
        if used + n > budget or per_src.get(c[1], 0) >= per_source_cap:
            continue
        out.append(c)
        used += n
        per_src[c[1]] = per_src.get(c[1], 0) + 1
    return out, used


def edge_first(cands):
    """Best at the start, second best at the end, weakest in the middle."""
    front, back = [], []
    for i, c in enumerate(cands):
        (front if i % 2 == 0 else back).append(c)
    return front + back[::-1]


if __name__ == "__main__":
    print("candidates:", len(CANDIDATES))
    print("jaccard(a#1, a#2) =", round(jaccard(CANDIDATES[0][3], CANDIDATES[1][3]), 3))
    d = dedupe(CANDIDATES)
    print("after dedupe:", [c[0] for c in d])
    packed, used = pack(d, budget=40)
    print("packed under 40-token budget:", [c[0] for c in packed], "tokens used:", used)
    print("edge-first order:", [c[0] for c in edge_first(packed)])
