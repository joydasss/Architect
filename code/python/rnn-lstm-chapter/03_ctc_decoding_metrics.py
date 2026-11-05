"""Connectionist temporal classification (CTC), beam search, and metrics.

Standard library only. Run: python 03_ctc_decoding_metrics.py

Parts:
  A. CTC: brute-force path enumeration versus the forward algorithm, and why
     best-path decoding can return the wrong label sequence.
  B. Greedy versus beam search on a tiny autoregressive model, and length bias.
  C. Word error rate, perplexity, and clipped unigram precision (BLEU ingredient).
"""

import itertools
import math

BLANK = 0


def collapse(path):
    out, prev = [], None
    for s in path:
        if s != prev and s != BLANK:
            out.append(s)
        prev = s
    return tuple(out)


def brute_force_label_probs(probs):
    """probs[t][s] = P(symbol s at frame t). Returns {label: probability}."""
    T, S = len(probs), len(probs[0])
    totals = {}
    for path in itertools.product(range(S), repeat=T):
        p = 1.0
        for t, s in enumerate(path):
            p *= probs[t][s]
        lab = collapse(path)
        totals[lab] = totals.get(lab, 0.0) + p
    return totals


def ctc_forward(probs, label):
    """P(label) by the CTC forward algorithm over the blank-extended label."""
    ext = [BLANK]
    for s in label:
        ext += [s, BLANK]
    T, L = len(probs), len(ext)
    alpha = [[0.0] * L for _ in range(T)]
    alpha[0][0] = probs[0][ext[0]]
    if L > 1:
        alpha[0][1] = probs[0][ext[1]]
    for t in range(1, T):
        for s in range(L):
            a = alpha[t - 1][s]
            if s >= 1:
                a += alpha[t - 1][s - 1]
            if s >= 2 and ext[s] != BLANK and ext[s] != ext[s - 2]:
                a += alpha[t - 1][s - 2]
            alpha[t][s] = a * probs[t][ext[s]]
    end = alpha[T - 1][L - 1]
    if L > 1:
        end += alpha[T - 1][L - 2]
    return end


def part_a():
    print("== A. CTC ==")
    # Two frames, vocabulary {blank, a}.
    p2 = [[0.6, 0.4], [0.6, 0.4]]
    labs = brute_force_label_probs(p2)
    print("2 frames, P(blank)=0.6, P(a)=0.4 each frame")
    for lab, p in sorted(labs.items(), key=lambda kv: -kv[1]):
        print("  label %-6s P=%.4f" % (lab, p))
    best_path = tuple(max(range(2), key=lambda s: p2[t][s]) for t in range(2))
    print("  best path", best_path, "collapses to", collapse(best_path))
    # Four frames, vocabulary {blank, a, b}; check forward algorithm.
    p4 = [[0.1, 0.7, 0.2], [0.5, 0.3, 0.2], [0.2, 0.1, 0.7], [0.4, 0.1, 0.5]]
    brute = brute_force_label_probs(p4)
    fwd = ctc_forward(p4, (1, 2))
    print("4 frames, label (a,b): brute force %.6f, forward %.6f" % (brute[(1, 2)], fwd))
    print("  sum over all labels = %.6f" % sum(brute.values()))
    print("  CTC loss = -ln P = %.4f" % -math.log(fwd))
    print("  number of paths = %d, paths for (a,b) = %d"
          % (3 ** 4, sum(1 for p in itertools.product(range(3), repeat=4)
                         if collapse(p) == (1, 2))))


def part_b():
    print("\n== B. Greedy versus beam search ==")
    # P(first token), P(second token | first). Sequence ends after two tokens.
    first = {"A": 0.55, "B": 0.45}
    second = {"A": {"x": 0.40, "y": 0.30, "z": 0.30},
              "B": {"x": 0.95, "y": 0.03, "z": 0.02}}
    g1 = max(first, key=first.get)
    g2 = max(second[g1], key=second[g1].get)
    print("greedy:", g1 + g2, "P=%.4f" % (first[g1] * second[g1][g2]))
    best = max(((a + b, first[a] * second[a][b]) for a in first for b in second[a]),
               key=lambda kv: kv[1])
    print("exact best:", best[0], "P=%.4f" % best[1])
    beam = sorted(first.items(), key=lambda kv: -kv[1])[:2]
    cands = [(a + b, pa * second[a][b]) for a, pa in beam for b in second[a]]
    cands.sort(key=lambda kv: -kv[1])
    print("beam width 2 final:", cands[0][0], "P=%.4f" % cands[0][1])
    beam1 = sorted(first.items(), key=lambda kv: -kv[1])[:1]
    c1 = sorted(((a + b, pa * second[a][b]) for a, pa in beam1 for b in second[a]),
                key=lambda kv: -kv[1])
    print("beam width 1 final:", c1[0][0], "P=%.4f" % c1[0][1])
    print("length bias: short logP=-2.4 over 3 tokens, long logP=-4.8 over 8 tokens")
    print("  raw score favours short; per-token average: short %.2f, long %.2f"
          % (-2.4 / 3, -4.8 / 8))


def edit_distance(ref, hyp):
    d = [[0] * (len(hyp) + 1) for _ in range(len(ref) + 1)]
    for i in range(len(ref) + 1):
        d[i][0] = i
    for j in range(len(hyp) + 1):
        d[0][j] = j
    for i in range(1, len(ref) + 1):
        for j in range(1, len(hyp) + 1):
            cost = 0 if ref[i - 1] == hyp[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
    return d[-1][-1]


def part_c():
    print("\n== C. Metrics ==")
    ref = "the cat sat on the mat".split()
    hyp = "the cat sit on mat".split()
    e = edit_distance(ref, hyp)
    print("WER: edits=%d, reference words=%d, WER=%.4f" % (e, len(ref), e / len(ref)))
    probs = [0.5, 0.25, 0.125, 0.5]
    nll = -sum(math.log(p) for p in probs) / len(probs)
    print("perplexity: mean NLL=%.4f nats, perplexity=%.4f (= 2^1.75 = %.4f)"
          % (nll, math.exp(nll), 2 ** 1.75))
    ref2 = "the cat is on the mat".split()
    hyp2 = "the the the the the the the".split()
    clipped = min(hyp2.count("the"), ref2.count("the"))
    print("clipped unigram precision: %d/%d = %.4f (unclipped would be 1.0)"
          % (clipped, len(hyp2), clipped / len(hyp2)))


if __name__ == "__main__":
    part_a()
    part_b()
    part_c()
