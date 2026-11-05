"""Chunking strategies on a small policy document (standard library only).

Compares fixed-window chunking with overlap, recursive splitting, sentence
packing, and structure-aware (heading path) chunking. "Tokens" are
whitespace-separated words, a stand-in for a real tokenizer. Prints chunk
counts and stored-token inflation, then the arithmetic from the chapter for a
corpus-scale index.
"""
import re

DOC = """# Travel Policy

## 1. Eligibility
All full-time employees may book business travel. Contractors may travel only
with written approval from a director. Approval must be recorded before booking.

## 2. Flights
Economy class is required for flights under 6 hours. Business class is allowed
for flights of 6 hours or more, subject to manager approval. Booking must occur
at least 14 days before departure unless an exception is filed.

### 2.1 Exceptions
An exception requires the cost-center owner to sign the exception form. The
form must state the business reason. Exceptions over 2000 USD also need
finance approval.

## 3. Expenses
Meals are reimbursed up to 60 USD per day. Receipts are required for any
single item above 25 USD. Claims must be submitted within 30 days of return.
"""


def words(text):
    return text.split()


def fixed(text, size, overlap):
    w = words(text)
    step = size - overlap
    out = []
    for start in range(0, max(len(w) - overlap, 1), step):
        out.append(" ".join(w[start:start + size]))
    return out


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def sentence_pack(text, max_words):
    out, cur = [], []
    for s in sentences(text):
        if cur and len(words(" ".join(cur + [s]))) > max_words:
            out.append(" ".join(cur))
            cur = []
        cur.append(s)
    if cur:
        out.append(" ".join(cur))
    return out


def recursive(text, max_words, seps=("\n\n", "\n", ". ", " ")):
    if len(words(text)) <= max_words or not seps:
        return [text.strip()] if text.strip() else []
    sep, rest = seps[0], seps[1:]
    parts = text.split(sep)
    out, cur = [], ""
    for p in parts:
        cand = (cur + sep + p) if cur else p
        if len(words(cand)) <= max_words:
            cur = cand
        else:
            if cur:
                out.append(cur.strip())
            if len(words(p)) > max_words:
                out.extend(recursive(p, max_words, rest))
                cur = ""
            else:
                cur = p
    if cur.strip():
        out.append(cur.strip())
    return out


def structure(text):
    """One chunk per heading section, prefixed with its heading path."""
    path, buf, out = [], [], []

    def flush():
        body = " ".join(" ".join(buf).split())
        if body:
            out.append(" > ".join(path) + ": " + body)

    for line in text.splitlines():
        m = re.match(r"^(#+)\s+(.*)", line)
        if m:
            flush()
            buf.clear()
            level = len(m.group(1))
            path[:] = path[:level - 1] + [m.group(2)]
        else:
            buf.append(line)
    flush()
    return out


def report(name, chunks):
    sizes = [len(words(c)) for c in chunks]
    print(f"{name:<28} chunks={len(chunks):>2} total_words={sum(sizes):>3} "
          f"min={min(sizes):>2} max={max(sizes):>3}")


if __name__ == "__main__":
    base = len(words(DOC))
    print("document words:", base)
    report("fixed 40, overlap 0", fixed(DOC, 40, 0))
    report("fixed 40, overlap 10", fixed(DOC, 40, 10))
    report("sentence pack <= 40", sentence_pack(DOC, 40))
    report("recursive <= 40", recursive(DOC, 40))
    st = structure(DOC)
    report("structure-aware", st)
    print("\nstructure-aware chunk heads:")
    for c in st:
        print("  ", c[:60])

    # Corpus-scale arithmetic (illustrative): 2,000,000 tokens of text.
    corpus = 2_000_000
    for size, ov in [(500, 0), (500, 100), (250, 50)]:
        step = size - ov
        n = -(-corpus // step)
        stored = n * size
        print(f"\nsize={size} overlap={ov}: chunks={n:,} "
              f"stored_tokens={stored:,} inflation={stored / corpus:.2f}x")
