"""Regex-plus-checks PII redactor with measured precision and recall.

Standard library only. Detects email, phone, US SSN-like numbers, payment
card numbers (Luhn check), and IBANs (mod-97 check). Then scores the detector
against a small hand-labelled corpus and prints the failure cases.

The corpus is illustrative and tiny. The point is the method: label spans,
count true positives, false positives and false negatives, then read the
failures. Do not treat the numbers as a benchmark.
"""
import hashlib
import hmac
import re

EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE = re.compile(r"(?<![\w-])(?:\+\d{1,3}[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?![\w-])")
SSN = re.compile(r"\b(?!000|666|9\d\d)\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b")
CARD = re.compile(r"\b\d(?:[ -]?\d){12,18}\b")
IBAN = re.compile(r"\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){2,7}(?: ?[A-Z0-9]{1,3})?\b")


def luhn_ok(digits: str) -> bool:
    total, flip = 0, False
    for ch in reversed(digits):
        d = int(ch)
        if flip:
            d *= 2
            if d > 9:
                d -= 9
        total += d
        flip = not flip
    return total % 10 == 0


def iban_ok(raw: str) -> bool:
    s = raw.replace(" ", "")
    if not 15 <= len(s) <= 34:
        return False
    moved = s[4:] + s[:4]
    num = "".join(str(int(c, 36)) for c in moved)
    return int(num) % 97 == 1


def detect(text: str):
    """Return a list of (start, end, label) spans after validity checks."""
    spans = []
    for m in EMAIL.finditer(text):
        spans.append((m.start(), m.end(), "EMAIL"))
    for m in SSN.finditer(text):
        spans.append((m.start(), m.end(), "SSN"))
    for m in CARD.finditer(text):
        digits = re.sub(r"\D", "", m.group())
        if 13 <= len(digits) <= 19 and luhn_ok(digits):
            spans.append((m.start(), m.end(), "CARD"))
    for m in IBAN.finditer(text):
        if iban_ok(m.group()):
            spans.append((m.start(), m.end(), "IBAN"))
    for m in PHONE.finditer(text):
        spans.append((m.start(), m.end(), "PHONE"))
    return resolve_overlaps(spans)


def resolve_overlaps(spans):
    """Keep the longest span when two detectors overlap."""
    spans = sorted(spans, key=lambda s: (s[0], -(s[1] - s[0])))
    kept = []
    for s in spans:
        if kept and s[0] < kept[-1][1]:
            continue
        kept.append(s)
    return kept


def redact(text: str, key: bytes = b"demo-key-rotate-me"):
    """Replace each span with a keyed pseudonym token like <EMAIL:3fa9c1>."""
    out, last = [], 0
    for start, end, label in detect(text):
        value = text[start:end]
        tag = hmac.new(key, value.encode(), hashlib.sha256).hexdigest()[:6]
        out.append(text[last:start])
        out.append(f"<{label}:{tag}>")
        last = end
    out.append(text[last:])
    return "".join(out)


# Each item: (text, [(substring, label), ...]) with the ground-truth PII.
CORPUS = [
    ("Contact me at ana.silva@example.com about order 8841.", [("ana.silva@example.com", "EMAIL")]),
    ("Call 415-555-0134 after 5pm.", [("415-555-0134", "PHONE")]),
    ("My number is (415) 555 0199, thanks.", [("(415) 555 0199", "PHONE")]),
    ("SSN 123-45-6789 was on the form.", [("123-45-6789", "SSN")]),
    ("Card 4111 1111 1111 1111 was declined.", [("4111 1111 1111 1111", "CARD")]),
    ("Pay to GB82 WEST 1234 5698 7654 32 please.", [("GB82 WEST 1234 5698 7654 32", "IBAN")]),
    ("Write to jo@corp.io or call +1 212-555-0111.", [("jo@corp.io", "EMAIL"), ("+1 212-555-0111", "PHONE")]),
    # Hard positives the patterns miss (names, addresses, obfuscation).
    ("Hi, this is Maria Gonzalez from 14 Elm Street.", [("Maria Gonzalez", "NAME"), ("14 Elm Street", "ADDRESS")]),
    ("Reach me: ana dot silva at example dot com", [("ana dot silva at example dot com", "EMAIL")]),
    ("Phone: four one five, five five five, zero one three four", [("four one five, five five five, zero one three four", "PHONE")]),
    ("Dr. Chen said the patient, Li Wei, has diabetes.", [("Chen", "NAME"), ("Li Wei", "NAME")]),
    # Hard negatives: look like PII but are not.
    ("Order 123-45-6788 shipped via lane 4.", []),
    ("Tracking 4111111111111112 is in transit.", []),
    ("Part no. 555-123-4567 is back in stock.", []),
    ("Build 2024.11.05 failed at step 3.", []),
    ("Invoice ref DE00 1234 5678 9012 3456 78.", []),
]

REGEX_LABELS = {"EMAIL", "SSN", "CARD", "IBAN", "PHONE"}


def score():
    tp = fp = fn = 0
    missed, falsely = [], []
    for text, truth in CORPUS:
        found = [(text[s:e], lab) for s, e, lab in detect(text)]
        truth_vals = {t[0] for t in truth}
        found_vals = {f[0] for f in found}
        for t in truth_vals & found_vals:
            tp += 1
        for t in truth_vals - found_vals:
            fn += 1
            missed.append((t, text))
        for f in found_vals - truth_vals:
            fp += 1
            falsely.append((f, text))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall)
    return tp, fp, fn, precision, recall, f1, missed, falsely


def main():
    print("== Redaction examples ==")
    for text, _ in CORPUS[:7]:
        print(redact(text))
    tp, fp, fn, p, r, f1, missed, falsely = score()
    print("\n== Span scores on 16 labelled texts ==")
    print(f"TP={tp} FP={fp} FN={fn}")
    print(f"precision={p:.3f} recall={r:.3f} F1={f1:.3f}")
    print("\n== False negatives (PII that leaks) ==")
    for value, text in missed:
        print(f"  missed {value!r}")
    print("\n== False positives (over-redaction) ==")
    for value, text in falsely:
        print(f"  flagged {value!r} in: {text}")
    # Same detector, recall counted only on the pattern-shaped labels.
    shaped_truth = sum(1 for _, t in CORPUS for v, lab in t if lab in REGEX_LABELS)
    shaped_tp = sum(
        1
        for text, t in CORPUS
        for v, lab in t
        if lab in REGEX_LABELS and v in {text[s:e] for s, e, _ in detect(text)}
    )
    print(f"\nRecall on structured identifiers only: {shaped_tp}/{shaped_truth}")


if __name__ == "__main__":
    main()
