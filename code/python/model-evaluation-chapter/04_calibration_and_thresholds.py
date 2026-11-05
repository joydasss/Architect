"""Calibration (reliability bins, ECE, Platt, isotonic, temperature scaling),
split conformal prediction, and cost-based thresholds.

Standard library only. Run: python 04_calibration_and_thresholds.py
Synthetic overconfident scores; all numbers are illustrative.
"""
import math
import random


def sigmoid(z):
    return 1 / (1 + math.exp(-z))


def make(n, rng, scale=2.5):
    """True logit is z; the model reports scale*z (overconfident)."""
    zs, ys, logits = [], [], []
    for _ in range(n):
        z = rng.gauss(0, 1.5)
        y = 1 if rng.random() < sigmoid(z) else 0
        zs.append(z)
        ys.append(y)
        logits.append(scale * z)
    return logits, ys


def log_loss(ps, ys):
    eps = 1e-12
    return -sum(math.log(max(eps, p if y else 1 - p)) for p, y in zip(ps, ys)) / len(ys)


def brier(ps, ys):
    return sum((p - y) ** 2 for p, y in zip(ps, ys)) / len(ys)


def ece(ps, ys, bins=10):
    n = len(ps)
    total = 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        idx = [i for i, p in enumerate(ps) if lo <= p < hi or (b == bins - 1 and p == 1.0)]
        if idx:
            conf = sum(ps[i] for i in idx) / len(idx)
            acc = sum(ys[i] for i in idx) / len(idx)
            total += len(idx) / n * abs(conf - acc)
    return total


def fit_temperature(logits, ys):
    lo, hi = 0.05, 10.0
    for _ in range(60):  # golden-section-like ternary search on convex loss
        m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        l1 = log_loss([sigmoid(z / m1) for z in logits], ys)
        l2 = log_loss([sigmoid(z / m2) for z in logits], ys)
        if l1 < l2:
            hi = m2
        else:
            lo = m1
    return (lo + hi) / 2


def fit_platt(logits, ys, steps=3000, lr=0.05):
    a, b = 1.0, 0.0
    n = len(ys)
    for _ in range(steps):
        ga = gb = 0.0
        for z, y in zip(logits, ys):
            d = sigmoid(a * z + b) - y
            ga += d * z
            gb += d
        a -= lr * ga / n
        b -= lr * gb / n
    return a, b


def fit_isotonic(scores, ys):
    """Pool Adjacent Violators; returns (sorted scores, fitted values)."""
    order = sorted(range(len(scores)), key=lambda i: scores[i])
    blocks = [[float(ys[i]), 1.0] for i in order]  # [sum, weight]
    stack = []
    for blk in blocks:
        stack.append(blk)
        while len(stack) > 1 and stack[-2][0] / stack[-2][1] > stack[-1][0] / stack[-1][1]:
            s, w = stack.pop()
            stack[-1][0] += s
            stack[-1][1] += w
    fitted = []
    for s, w in stack:
        fitted.extend([s / w] * int(w))
    return [scores[i] for i in order], fitted


def iso_predict(xs, fit, x):
    lo, hi = 0, len(xs)
    while lo < hi:
        mid = (lo + hi) // 2
        if xs[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return fit[min(lo, len(fit) - 1)]


def split_conformal(cal_logits, cal_y, test_logits, test_y, alpha=0.1):
    """Score = 1 - probability of the true class; sets from the quantile."""
    cal_scores = []
    for z, y in zip(cal_logits, cal_y):
        p1 = sigmoid(z)
        cal_scores.append(1 - (p1 if y else 1 - p1))
    cal_scores.sort()
    n = len(cal_scores)
    k = math.ceil((n + 1) * (1 - alpha))
    q = cal_scores[min(k, n) - 1]
    covered = size = 0
    for z, y in zip(test_logits, test_y):
        p1 = sigmoid(z)
        s = {c for c, p in ((1, p1), (0, 1 - p1)) if 1 - p <= q}
        covered += y in s
        size += len(s)
    return q, covered / len(test_y), size / len(test_y)


def best_threshold(ps, ys, c_fp, c_fn):
    best = None
    for t in [i / 100 for i in range(1, 100)]:
        fp = sum(1 for p, y in zip(ps, ys) if p >= t and not y)
        fn = sum(1 for p, y in zip(ps, ys) if p < t and y)
        cost = c_fp * fp + c_fn * fn
        if best is None or cost < best[1]:
            best = (t, cost, fp, fn)
    return best


if __name__ == "__main__":
    rng = random.Random(21)
    tr_l, tr_y = make(20_000, rng)       # fit calibrators
    te_l, te_y = make(20_000, rng)       # evaluate

    raw = [sigmoid(z) for z in te_l]
    print("== Overconfident model (logits are 2.5x too large) ==")
    print(f"raw          log_loss={log_loss(raw, te_y):.4f} brier={brier(raw, te_y):.4f} ece={ece(raw, te_y):.4f}")

    T = fit_temperature(tr_l, tr_y)
    ts = [sigmoid(z / T) for z in te_l]
    print(f"temperature  T={T:.2f} log_loss={log_loss(ts, te_y):.4f} brier={brier(ts, te_y):.4f} ece={ece(ts, te_y):.4f}")

    a, b = fit_platt(tr_l[:4000], tr_y[:4000])
    pl = [sigmoid(a * z + b) for z in te_l]
    print(f"platt        a={a:.2f} b={b:.2f} log_loss={log_loss(pl, te_y):.4f} brier={brier(pl, te_y):.4f} ece={ece(pl, te_y):.4f}")

    xs, fit = fit_isotonic(tr_l, tr_y)
    iso = [iso_predict(xs, fit, z) for z in te_l]
    print(f"isotonic     log_loss={log_loss([min(max(p, 1e-4), 1 - 1e-4) for p in iso], te_y):.4f} brier={brier(iso, te_y):.4f} ece={ece(iso, te_y):.4f}")

    print("\nreliability table for raw scores (bin, count, mean predicted, observed rate):")
    for bi in range(0, 10, 3):
        lo, hi = bi / 10, (bi + 1) / 10
        idx = [i for i, p in enumerate(raw) if lo <= p < hi]
        if idx:
            print(f"  [{lo:.1f},{hi:.1f}) n={len(idx):<5} predicted={sum(raw[i] for i in idx)/len(idx):.3f} observed={sum(te_y[i] for i in idx)/len(idx):.3f}")

    q, cov, size = split_conformal(tr_l[:2000], tr_y[:2000], te_l, te_y, alpha=0.1)
    print(f"\n== Split conformal, alpha=0.10, 2000 calibration points ==")
    print(f"quantile={q:.3f} empirical coverage={cov:.3f} mean set size={size:.2f}")

    print("\n== Cost-based threshold on calibrated scores ==")
    for c_fp, c_fn in ((1, 1), (1, 10), (1, 50)):
        t, cost, fp, fn = best_threshold(ts, te_y, c_fp, c_fn)
        theory = c_fp / (c_fp + c_fn)
        print(f"cost FP={c_fp} FN={c_fn}: theory t*={theory:.3f} empirical best t={t:.2f} FP={fp} FN={fn} total_cost={cost}")
