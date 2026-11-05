"""Fairness metrics on a confusion-matrix table (standard library only).

Computes selection rate, TPR, FPR, PPV, accuracy per group, the gaps that define
demographic parity, equal opportunity, equalized odds and predictive parity,
a calibration-within-groups table, the Chouldechova identity that shows why
equal PPV and equal error rates cannot all hold when base rates differ, a
Wilson interval for subgroup uncertainty, and a toy individual-fairness check.

Run: python 01_fairness_metrics.py
"""

import math

# Illustrative counts (not real data): TP, FP, FN, TN per group.
GROUPS = {
    "A": {"tp": 300, "fp": 120, "fn": 100, "tn": 480},
    "B": {"tp": 60, "fp": 80, "fn": 40, "tn": 320},
}


def rates(c):
    n = c["tp"] + c["fp"] + c["fn"] + c["tn"]
    pos = c["tp"] + c["fn"]
    neg = c["fp"] + c["tn"]
    pred_pos = c["tp"] + c["fp"]
    return {
        "n": n,
        "base_rate": pos / n,
        "selection": pred_pos / n,
        "tpr": c["tp"] / pos,
        "fpr": c["fp"] / neg,
        "ppv": c["tp"] / pred_pos,
        "accuracy": (c["tp"] + c["tn"]) / n,
    }


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return centre - half, centre + half


def main():
    r = {g: rates(c) for g, c in GROUPS.items()}
    print("== Per-group rates ==")
    print(f"{'group':<6}{'n':>6}{'base':>8}{'select':>8}{'TPR':>8}{'FPR':>8}{'PPV':>8}{'acc':>8}")
    for g, x in r.items():
        print(f"{g:<6}{x['n']:>6}{x['base_rate']:>8.3f}{x['selection']:>8.3f}"
              f"{x['tpr']:>8.3f}{x['fpr']:>8.3f}{x['ppv']:>8.3f}{x['accuracy']:>8.3f}")

    a, b = r["A"], r["B"]
    print("\n== Criteria (A minus B, and ratio B/A where relevant) ==")
    print(f"Demographic parity gap (selection): {a['selection'] - b['selection']:+.3f}")
    print(f"Disparate impact ratio (B/A):       {b['selection'] / a['selection']:.3f}")
    print(f"Equal opportunity gap (TPR):        {a['tpr'] - b['tpr']:+.3f}")
    print(f"FPR gap:                            {a['fpr'] - b['fpr']:+.3f}")
    print(f"Equalized odds (max of TPR, FPR gap): {max(abs(a['tpr'] - b['tpr']), abs(a['fpr'] - b['fpr'])):.3f}")
    print(f"Predictive parity gap (PPV):        {a['ppv'] - b['ppv']:+.3f}")

    print("\n== Uncertainty: Wilson 95% interval for TPR ==")
    for g, c in GROUPS.items():
        lo, hi = wilson(c["tp"], c["tp"] + c["fn"])
        print(f"group {g}: TPR {rates(c)['tpr']:.3f}, 95% interval [{lo:.3f}, {hi:.3f}], positives={c['tp'] + c['fn']}")

    print("\n== Calibration within groups (illustrative score bins) ==")
    # (bin mean score, count, observed positives) per group.
    bins = {
        "A": [(0.2, 400, 84), (0.5, 300, 150), (0.8, 300, 246)],
        "B": [(0.2, 250, 70), (0.5, 150, 76), (0.8, 100, 54)],
    }
    for g, rows in bins.items():
        for score, cnt, pos in rows:
            print(f"group {g} score {score:.1f}: observed {pos / cnt:.3f} (gap {pos / cnt - score:+.3f}, n={cnt})")

    print("\n== Impossibility: equal PPV and TPR force unequal FPR if base rates differ ==")
    ppv, tpr = 0.7, 0.7
    for g, p in (("A", 0.4), ("B", 0.2)):
        fpr = p / (1 - p) * (1 - ppv) / ppv * tpr
        print(f"group {g}: base rate {p:.2f}, PPV {ppv}, TPR {tpr} -> FPR must be {fpr:.3f}")

    print("\n== Post-processing: group thresholds to equalize TPR (toy scores) ==")
    # Scores of true positives per group; choose the threshold giving TPR = 0.75.
    pos_scores = {
        "A": [0.95, 0.9, 0.85, 0.8, 0.7, 0.6, 0.5, 0.4],
        "B": [0.85, 0.7, 0.6, 0.5, 0.45, 0.4, 0.3, 0.2],
    }
    target = 0.75
    for g, s in pos_scores.items():
        s_sorted = sorted(s, reverse=True)
        k = math.ceil(target * len(s_sorted))
        thr = s_sorted[k - 1]
        print(f"group {g}: threshold {thr:.2f} gives TPR {sum(x >= thr for x in s) / len(s):.2f}")

    print("\n== Individual fairness: similar inputs, similar outputs ==")
    pairs = [((700, 0.30), (705, 0.30), 0.62, 0.35), ((700, 0.30), (702, 0.31), 0.62, 0.60)]
    lipschitz = 5.0  # allowed output change per unit of normalized feature distance
    for (x1, x2, s1, s2) in [(p[0], p[1], p[2], p[3]) for p in pairs]:
        dist = math.sqrt(((x1[0] - x2[0]) / 850) ** 2 + (x1[1] - x2[1]) ** 2)
        diff = abs(s1 - s2)
        verdict = "OK" if diff <= lipschitz * dist else "VIOLATION"
        print(f"distance {dist:.4f}, score gap {diff:.2f}, limit {lipschitz * dist:.3f} -> {verdict}")


if __name__ == "__main__":
    main()
