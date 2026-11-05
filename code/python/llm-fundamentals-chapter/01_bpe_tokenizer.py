"""Byte-pair encoding (BPE) by hand: learn merges, encode, and show byte fallback.

Standard library only. Run: python 01_bpe_tokenizer.py

Part 1 reproduces the classic word-level BPE worked example (Sennrich, Haddow
and Birch, 2016) on a four-word corpus so every count can be checked by hand.
Part 2 encodes an unseen word with the learned merges.
Part 3 shows why byte-level fallback never fails and why non-Latin text costs
more tokens when a vocabulary is dominated by English.
"""

from collections import Counter

CORPUS = {"low": 5, "lower": 2, "newest": 6, "widest": 3}  # word -> frequency


def to_symbols(word):
    """Split a word into characters and append an end-of-word marker."""
    return tuple(word) + ("</w>",)


def pair_counts(vocab):
    counts = Counter()
    for symbols, freq in vocab.items():
        for a, b in zip(symbols, symbols[1:]):
            counts[(a, b)] += freq
    return counts


def merge_pair(vocab, pair):
    merged = {}
    for symbols, freq in vocab.items():
        out, i = [], 0
        while i < len(symbols):
            if i < len(symbols) - 1 and (symbols[i], symbols[i + 1]) == pair:
                out.append(symbols[i] + symbols[i + 1])
                i += 2
            else:
                out.append(symbols[i])
                i += 1
        merged[tuple(out)] = merged.get(tuple(out), 0) + freq
    return merged


def learn_bpe(corpus, num_merges):
    vocab = {to_symbols(w): f for w, f in corpus.items()}
    merges = []
    for step in range(1, num_merges + 1):
        counts = pair_counts(vocab)
        if not counts:
            break
        # Deterministic tie-break: highest count, then lexicographically smallest pair.
        best = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0]
        pair, count = best
        merges.append(pair)
        vocab = merge_pair(vocab, pair)
        print(f"merge {step:2d}: {pair[0]!r} + {pair[1]!r} -> {pair[0] + pair[1]!r}  (count {count})")
    return merges, vocab


def encode_word(word, merges):
    symbols = list(to_symbols(word))
    for pair in merges:  # apply merges in the order they were learned
        i = 0
        while i < len(symbols) - 1:
            if (symbols[i], symbols[i + 1]) == pair:
                symbols[i:i + 2] = [symbols[i] + symbols[i + 1]]
            else:
                i += 1
    return symbols


def main():
    print("== Part 1: learning merges ==")
    start = pair_counts({to_symbols(w): f for w, f in CORPUS.items()})
    top = sorted(start.items(), key=lambda kv: (-kv[1], kv[0]))[:4]
    print("initial top pair counts:", top)
    merges, vocab = learn_bpe(CORPUS, 10)
    print("final segmentation:")
    for symbols, freq in vocab.items():
        print("  ", list(symbols), "x", freq)

    print("\n== Part 2: encoding words with the learned merges ==")
    for w in ["newest", "lowest", "wider", "xyz"]:
        print(f"{w!r:10} -> {encode_word(w, merges)}")

    print("\n== Part 3: byte-level fallback and multilingual inflation ==")
    samples = {
        "English": "The invoice is overdue.",
        "French": "La facture est en retard.",
        "Japanese": "請求書は支払期限を過ぎています。",
        "Emoji": "ok \U0001F600",
    }
    for lang, text in samples.items():
        raw = text.encode("utf-8")
        print(f"{lang:9} chars={len(text):3d} utf8_bytes={len(raw):3d} "
              f"bytes_per_char={len(raw) / len(text):.2f}")
    # With a byte-only vocabulary (no merges) every UTF-8 byte is a token.
    print("worst case token count = utf-8 byte count; merges only ever reduce it")
    print("bytes of the emoji:", list("\U0001F600".encode("utf-8")))


if __name__ == "__main__":
    main()
