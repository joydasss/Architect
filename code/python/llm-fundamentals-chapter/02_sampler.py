"""Decoding strategies on a toy next-token distribution.

Standard library only. Run: python 02_sampler.py

Shows, with numbers, how softmax, temperature, top-k, top-p, min-p,
repetition/frequency penalties, logit bias, seeds, and beam search change the
distribution or the selected sequence. The vocabulary and logits are
illustrative, not taken from a real model.
"""

import math
import random

VOCAB = ["Paris", "France", "the", "a", "Lyon", "Rome", "banana", "<eos>"]
LOGITS = [4.0, 2.5, 2.0, 1.0, 1.0, 0.5, -1.0, 0.0]


def softmax(logits, temperature=1.0):
    scaled = [z / temperature for z in logits]
    m = max(scaled)  # subtract the max for numerical stability
    exps = [math.exp(z - m) for z in scaled]
    total = sum(exps)
    return [e / total for e in exps]


def entropy_bits(p):
    return -sum(x * math.log2(x) for x in p if x > 0)


def top_k(p, k):
    keep = set(sorted(range(len(p)), key=lambda i: -p[i])[:k])
    q = [x if i in keep else 0.0 for i, x in enumerate(p)]
    s = sum(q)
    return [x / s for x in q]


def top_p(p, mass):
    order = sorted(range(len(p)), key=lambda i: -p[i])
    keep, cum = set(), 0.0
    for i in order:
        keep.add(i)
        cum += p[i]
        if cum >= mass:
            break
    q = [x if i in keep else 0.0 for i, x in enumerate(p)]
    s = sum(q)
    return [x / s for x in q]


def min_p(p, ratio):
    threshold = ratio * max(p)
    q = [x if x >= threshold else 0.0 for x in p]
    s = sum(q)
    return [x / s for x in q]


def penalize(logits, history, repetition=1.0, frequency=0.0, presence=0.0):
    """Apply penalties to tokens already generated (history is a list of ids)."""
    out = list(logits)
    counts = {}
    for t in history:
        counts[t] = counts.get(t, 0) + 1
    for t, c in counts.items():
        z = out[t]
        z = z / repetition if z > 0 else z * repetition  # multiplicative form
        z -= frequency * c + presence  # additive form (frequency and presence)
        out[t] = z
    return out


def show(title, p):
    row = " ".join(f"{VOCAB[i]}={p[i]:.3f}" for i in range(len(p)))
    print(f"{title:<26} H={entropy_bits(p):.2f} bits | {row}")


def sample(p, rng):
    r, cum = rng.random(), 0.0
    for i, x in enumerate(p):
        cum += x
        if r < cum:
            return i
    return len(p) - 1


def beam_vs_greedy():
    """Two-step toy: greedy picks the locally best first token, beam does not."""
    # step 1 distribution over {A, B}; step 2 distributions depend on the first token.
    step1 = {"A": 0.55, "B": 0.45}
    step2 = {"A": {"x": 0.40, "y": 0.35, "z": 0.25},
             "B": {"x": 0.90, "y": 0.05, "z": 0.05}}
    g1 = max(step1, key=step1.get)
    g2 = max(step2[g1], key=step2[g1].get)
    greedy = (g1 + g2, step1[g1] * step2[g1][g2])
    best = max(((a + b, step1[a] * step2[a][b]) for a in step1 for b in step2[a]),
               key=lambda t: t[1])
    print(f"greedy sequence {greedy[0]} p={greedy[1]:.3f}; best sequence {best[0]} p={best[1]:.3f}")


def main():
    base = softmax(LOGITS)
    print("== Temperature ==")
    for t in (0.2, 0.7, 1.0, 1.5):
        show(f"T={t}", softmax(LOGITS, t))

    print("\n== Truncation at T=1 ==")
    show("untruncated", base)
    show("top-k k=3", top_k(base, 3))
    show("top-p p=0.90", top_p(base, 0.90))
    show("min-p ratio=0.10", min_p(base, 0.10))

    print("\n== Truncation after T=1.5 (flatter) ==")
    flat = softmax(LOGITS, 1.5)
    show("T=1.5", flat)
    show("T=1.5 + top-p 0.90", top_p(flat, 0.90))
    show("T=1.5 + min-p 0.10", min_p(flat, 0.10))

    print("\n== Penalties (history: Paris, Paris, the) ==")
    hist = [0, 0, 2]
    show("no penalty", softmax(LOGITS))
    show("repetition 1.3", softmax(penalize(LOGITS, hist, repetition=1.3)))
    show("frequency 0.8", softmax(penalize(LOGITS, hist, frequency=0.8)))
    biased = list(LOGITS)
    biased[VOCAB.index("<eos>")] += 3.0
    show("logit bias <eos> +3", softmax(biased))

    print("\n== Seeds: 12 draws at T=1 ==")
    for seed in (1, 1, 2):
        rng = random.Random(seed)
        draws = [VOCAB[sample(base, rng)] for _ in range(12)]
        print(f"seed={seed}: {' '.join(draws)}")

    print("\n== Beam search versus greedy ==")
    beam_vs_greedy()

    print("\n== Sequence log-probability ==")
    lp = [math.log(0.6), math.log(0.3), math.log(0.9)]
    print("token logprobs:", [round(x, 3) for x in lp])
    print("sequence logprob:", round(sum(lp), 3), "-> probability", round(math.exp(sum(lp)), 3))
    print("perplexity:", round(math.exp(-sum(lp) / len(lp)), 3))


if __name__ == "__main__":
    main()
