"""Parse -> schema-validate -> semantic-validate -> repair-and-retry pipeline.

Standard library only. The "model" is a seeded simulator that produces the
failure modes the chapter discusses: fenced JSON, trailing commas, missing
fields, wrong types, truncation, a refusal inside the structure, and valid but
wrong values. Run: python 01_validation_pipeline.py
"""
import json
import random
import re
from collections import Counter
from datetime import date

SCHEMA = {
    "invoice_number": str,
    "invoice_date": str,      # ISO 8601 date
    "currency": str,          # one of ALLOWED_CURRENCY
    "subtotal": (int, float),
    "tax": (int, float),
    "total": (int, float),
    "status": str,            # "ok" | "unreadable"
}
ALLOWED_CURRENCY = {"USD", "EUR", "GBP"}
SOURCE_TEXT = "Invoice INV-1042 dated 2026-03-14. Subtotal 200.00 EUR, VAT 40.00, total 240.00 EUR."
GOOD = {"invoice_number": "INV-1042", "invoice_date": "2026-03-14", "currency": "EUR",
        "subtotal": 200.0, "tax": 40.0, "total": 240.0, "status": "ok"}


def simulated_model(rng, attempt, repair_hint):
    """Return raw text. A repair hint lowers the formatting failure rate."""
    r = rng.random()
    # failure-rate table: first attempt vs attempt after an error message
    p = [0.55, 0.10, 0.08, 0.07, 0.05, 0.05, 0.10] if not repair_hint else \
        [0.80, 0.03, 0.04, 0.02, 0.04, 0.02, 0.05]
    kinds = ["clean", "fenced", "trailing_comma", "missing_field",
             "wrong_type", "refusal", "valid_but_wrong"]
    kind = kinds[-1]
    acc = 0.0
    for k, w in zip(kinds, p):
        acc += w
        if r < acc:
            kind = k
            break
    d = dict(GOOD)
    if kind == "clean":
        return json.dumps(d)
    if kind == "fenced":
        return "```json\n" + json.dumps(d) + "\n```"
    if kind == "trailing_comma":
        return json.dumps(d)[:-1] + ",}"
    if kind == "missing_field":
        del d["tax"]
        return json.dumps(d)
    if kind == "wrong_type":
        d["total"] = "240.00 EUR"
        return json.dumps(d)
    if kind == "refusal":
        return json.dumps({"error": "I cannot help with that."})
    d["total"] = 204.0           # valid shape, wrong value (dropped a digit)
    return json.dumps(d)


def parse(raw):
    text = raw.strip()
    m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.S)
    if m:
        text = m.group(1)
    return json.loads(text)       # raises json.JSONDecodeError


def schema_validate(obj):
    errors = []
    if not isinstance(obj, dict):
        return ["top level must be an object"]
    for key, typ in SCHEMA.items():
        if key not in obj:
            errors.append(f"missing field: {key}")
        elif not isinstance(obj[key], typ) or isinstance(obj[key], bool):
            errors.append(f"wrong type: {key}")
    for key in obj:
        if key not in SCHEMA:
            errors.append(f"unexpected field: {key}")
    return errors


def semantic_validate(obj, source):
    errors = []
    if obj["currency"] not in ALLOWED_CURRENCY:
        errors.append("currency not allowed")
    try:
        date.fromisoformat(obj["invoice_date"])
    except ValueError:
        errors.append("invoice_date is not a real ISO date")
    if abs(obj["subtotal"] + obj["tax"] - obj["total"]) > 0.005:
        errors.append("subtotal + tax != total")
    if obj["invoice_number"] not in source:      # grounding check
        errors.append("invoice_number not found in source")
    return errors


def run_once(rng, max_attempts=3):
    hint = None
    for attempt in range(1, max_attempts + 1):
        raw = simulated_model(rng, attempt, hint)
        try:
            obj = parse(raw)
        except json.JSONDecodeError as exc:
            hint, gate = f"JSON parse error: {exc.msg}", "parse"
            last = gate
            continue
        errs = schema_validate(obj)
        if errs:
            hint, gate = "; ".join(errs), "schema"
            last = gate
            continue
        errs = semantic_validate(obj, SOURCE_TEXT)
        if errs:
            hint, gate = "; ".join(errs), "semantic"
            last = gate
            continue
        return obj, attempt, None
    return None, max_attempts, last


def main():
    rng = random.Random(17)
    n = 10000
    outcomes = Counter()
    attempts = Counter()
    wrong_accepted = 0
    for _ in range(n):
        obj, used, gate = run_once(rng)
        attempts[used] += used
        if obj is None:
            outcomes["rejected_after_retries(" + gate + ")"] += 1
        else:
            outcomes["accepted"] += 1
            if obj != GOOD:
                wrong_accepted += 1
    total_calls = sum(attempts.values())
    print(f"requests: {n}")
    for k, v in sorted(outcomes.items()):
        print(f"{k}: {v} ({100 * v / n:.2f}%)")
    print(f"accepted but not equal to ground truth: {wrong_accepted}")
    print(f"model calls per request: {total_calls / n:.3f}")
    print("note: 'valid_but_wrong' with a total that breaks subtotal+tax is caught by the")
    print("semantic gate; a wrong value that stays internally consistent would pass.")


if __name__ == "__main__":
    main()
