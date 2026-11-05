"""Confusion-matrix metrics, base-rate effects, ROC/PR areas, log loss, Brier.

Standard library only. Run: python 01_metrics_and_base_rates.py
All data are synthetic and illustrative.
"""
import math
import random


def confusion(tp, fp, fn, tn):
    p = tp / (tp + fp) if tp + fp else float("nan")
    r = tp / (tp + fn)
    spec = tn / (tn + fp)
    f1 = 2 * p * r / (p + r)
    beta = 2.0
    fb = (1 + beta**2) * p * r / (beta**2 * p + r)
    mcc_den = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = (tp * tn - fp * fn) / mcc_den
    return dict(precision=p, recall=r, specificity=spec, f1=f1, f2=fb,
                mcc=mcc, balanced_acc=(r + spec) / 2,
                accuracy=(tp + tn) / (tp + fp + fn + tn))


def show(title, d):
    print(title)
    print("  " + "  ".join(f"{k}={v:.3f}" for k, v in d.items()))


def base_rate_demo():
    print("== Base-rate effect: same recall 0.90 and FPR 0.05 ==")
    for prevalence in (0.5, 0.1, 0.01, 0.001):
        n = 100_000
        pos = round(n * prevalence)
        neg = n - pos
        tp = round(0.90 * pos)
        fn = pos - tp
        fp = round(0.05 * neg)
        tn = neg - fp
        c = confusion(tp, fp, fn, tn)
        print(f"prevalence={prevalence:<6} TP={tp:<6} FP={fp:<6} "
              f"precision={c['precision']:.4f} mcc={c['mcc']:.3f} "
              f"balanced_acc={c['balanced_acc']:.3f} accuracy={c['accuracy']:.4f}")
    print()


def roc_points(scores, labels):
    pairs = sorted(zip(scores, labels), key=lambda t: -t[0])
    P = sum(labels)
    N = len(labels) - P
    tp = fp = 0
    roc = [(0.0, 0.0)]
    pr = []
    i = 0
    while i < len(pairs):
        j = i
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:
            if pairs[j][1]:
                tp += 1
            else:
                fp += 1
            j += 1
        roc.append((fp / N, tp / P))
        pr.append((tp / P, tp / (tp + fp)))
        i = j
    return roc, pr


def auc_trapezoid(points):
    return sum((x2 - x1) * (y1 + y2) / 2
               for (x1, y1), (x2, y2) in zip(points, points[1:]))


def average_precision(pr):
    prev_r = 0.0
    ap = 0.0
    for r, p in pr:
        ap += (r - prev_r) * p
        prev_r = r
    return ap


def synth(n, prevalence, sep, rng):
    labels = [1 if rng.random() < prevalence else 0 for _ in range(n)]
    scores = [rng.gauss(sep if y else 0.0, 1.0) for y in labels]
    return scores, labels


def roc_vs_pr():
    print("== Same score quality (separation d=2), different prevalence ==")
    rng = random.Random(7)
    for prevalence in (0.5, 0.01):
        s, y = synth(200_000, prevalence, 2.0, rng)
        roc, pr = roc_points(s, y)
        print(f"prevalence={prevalence:<5} ROC-AUC={auc_trapezoid(roc):.3f} "
              f"average_precision={average_precision(pr):.3f} "
              f"baseline_AP(prevalence)={prevalence:.3f}")
    print()


def log_loss_brier():
    print("== Log loss and Brier on 5 predictions ==")
    y = [1, 0, 1, 0, 1]
    p = [0.9, 0.2, 0.6, 0.4, 0.05]
    ll = -sum(math.log(pi if yi else 1 - pi) for yi, pi in zip(y, p)) / len(y)
    br = sum((pi - yi) ** 2 for yi, pi in zip(y, p)) / len(y)
    print(f"log_loss={ll:.4f} brier={br:.4f}")
    print("per-example log loss:",
          [round(-math.log(pi if yi else 1 - pi), 3) for yi, pi in zip(y, p)])
    print()


if __name__ == "__main__":
    # Fraud example from the chapter: 10,000 transactions, 100 fraud.
    show("Fraud queue TP=90 FP=900 FN=10 TN=9000:", confusion(90, 900, 10, 9000))
    print()
    base_rate_demo()
    roc_vs_pr()
    log_loss_brier()
