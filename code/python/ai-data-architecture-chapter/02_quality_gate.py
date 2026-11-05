"""Quality gate with thresholds, drift (PSI), and label agreement (standard library).

Run: python 02_quality_gate.py
"""

import math
import random

random.seed(7)


def completeness(values):
    return sum(v is not None for v in values) / len(values)


def uniqueness(keys):
    return len(set(keys)) / len(keys)


def psi(expected, actual, bins=10):
    """Population Stability Index over equal-width bins of the expected range."""
    lo, hi = min(expected), max(expected)
    width = (hi - lo) / bins

    def hist(xs):
        counts = [0] * bins
        for x in xs:
            idx = min(max(int((x - lo) / width), 0), bins - 1)
            counts[idx] += 1
        return [max(c / len(xs), 1e-4) for c in counts]

    e, a = hist(expected), hist(actual)
    return sum((ai - ei) * math.log(ai / ei) for ei, ai in zip(e, a))


def cohens_kappa(a, b):
    n = len(a)
    labels = sorted(set(a) | set(b))
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(l) / n) * (b.count(l) / n) for l in labels)
    return (po - pe) / (1 - pe)


GATES = {"completeness": 0.99, "uniqueness": 1.0, "psi_warn": 0.10, "psi_block": 0.25, "kappa": 0.70}

if __name__ == "__main__":
    n = 1000
    ids = [f"id{i}" for i in range(n)]
    ids[10] = ids[11] = "id_dup"  # one duplicate pair -> 999 unique of 1000
    spend = [None if i % 125 == 0 else random.gauss(50, 10) for i in range(n)]  # 8 nulls
    comp = completeness(spend)
    uniq = uniqueness(ids)
    print(f"completeness={comp:.3f} gate>={GATES['completeness']} -> {'PASS' if comp >= GATES['completeness'] else 'FAIL'}")
    print(f"uniqueness={uniq:.3f} gate>={GATES['uniqueness']} -> {'PASS' if uniq >= GATES['uniqueness'] else 'FAIL'}")

    ref = [random.gauss(50, 10) for _ in range(5000)]
    same = [random.gauss(50, 10) for _ in range(5000)]
    shifted = [random.gauss(55, 10) for _ in range(5000)]
    for name, cur in (("no shift", same), ("mean +0.5 sigma", shifted)):
        v = psi(ref, cur)
        verdict = "BLOCK" if v >= GATES["psi_block"] else "WARN" if v >= GATES["psi_warn"] else "OK"
        print(f"psi[{name}]={v:.3f} -> {verdict}")

    # Label agreement: 200 items, two annotators, 90% raw agreement on a skewed label set.
    a, b = [], []
    for i in range(200):
        la = "neg" if i < 170 else "pos"
        lb = la if i % 10 != 0 else ("pos" if la == "neg" else "neg")
        a.append(la)
        b.append(lb)
    raw = sum(x == y for x, y in zip(a, b)) / len(a)
    k = cohens_kappa(a, b)
    print(f"label raw_agreement={raw:.3f} kappa={k:.3f} gate>={GATES['kappa']} -> {'PASS' if k >= GATES['kappa'] else 'FAIL'}")
