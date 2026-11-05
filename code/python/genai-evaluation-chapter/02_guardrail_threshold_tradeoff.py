"""Guardrail threshold trade-off on a synthetic classifier (standard library only).

Scores for harmful and benign inputs are drawn from seeded Beta distributions.
The script prints precision, recall, false positive rate and expected cost at
several thresholds, then picks the cheapest threshold. All numbers are
illustrative: replace the distributions with your labelled traffic.
"""
import random

random.seed(7)
N_BENIGN, N_HARM = 99000, 1000  # 1 percent prevalence of harmful input
benign = [random.betavariate(2, 8) for _ in range(N_BENIGN)]
harm = [random.betavariate(7, 3) for _ in range(N_HARM)]

COST_FN = 500.0  # illustrative cost of one missed harmful request
COST_FP = 2.0    # illustrative cost of one wrongly blocked benign request


def at(threshold):
    tp = sum(s >= threshold for s in harm)
    fn = N_HARM - tp
    fp = sum(s >= threshold for s in benign)
    tn = N_BENIGN - fp
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / N_HARM
    fpr = fp / N_BENIGN
    cost = fn * COST_FN + fp * COST_FP
    return tp, fn, fp, tn, precision, recall, fpr, cost


print("thr    TP    FN     FP  precision recall   FPR    cost")
best = None
for t in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
    tp, fn, fp, tn, p, r, fpr, cost = at(t)
    print(f"{t:.1f} {tp:5d} {fn:5d} {fp:6d}   {p:.3f}    {r:.3f}  {fpr:.4f} {cost:9.0f}")
    if best is None or cost < best[1]:
        best = (t, cost)
print(f"cheapest threshold on this grid: {best[0]} (cost {best[1]:.0f})")

# Two layers in series (any layer blocks): assume independent errors.
r1, f1 = 0.80, 0.02
r2, f2 = 0.70, 0.01
print(f"two layers OR-ed: recall {1-(1-r1)*(1-r2):.3f}, FPR {1-(1-f1)*(1-f2):.4f}")
