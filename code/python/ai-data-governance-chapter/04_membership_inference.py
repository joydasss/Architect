"""Loss-threshold membership inference on an overfit toy model.

Standard library only. Trains logistic regression on noisy data with many
features and few examples, so it memorizes. An attacker who sees only the loss
on a candidate record guesses whether the record was in the training set.
Reports attack AUC and advantage (TPR minus FPR at the median loss) for an
overfit model and a regularized model, to show that the generalization gap
drives leakage.

This is a toy. Real attacks on large models are harder to run and to defend
against; see the chapter text for caveats.
"""
import math
import random

random.seed(3)
N_TRAIN, N_OUT, DIM = 60, 60, 100


def make(n):
    X, y = [], []
    for _ in range(n):
        x = [random.gauss(0, 1) for _ in range(DIM)]
        z = x[0] - x[1] + 0.5 * x[2]  # weak signal, 97 noise features
        p = 1 / (1 + math.exp(-z))
        X.append(x)
        y.append(1.0 if random.random() < p else 0.0)
    return X, y


def dot(w, x):
    return sum(a * b for a, b in zip(w, x))


def sigmoid(z):
    return 1 / (1 + math.exp(-max(min(z, 30), -30)))


def train(X, y, l2, steps=1500, lr=0.2):
    w = [0.0] * DIM
    n = len(y)
    for _ in range(steps):
        grad = [l2 * wj for wj in w]
        for x, t in zip(X, y):
            err = (sigmoid(dot(w, x)) - t) / n
            for j in range(DIM):
                grad[j] += err * x[j]
        w = [wj - lr * g for wj, g in zip(w, grad)]
    return w


def loss(w, x, t):
    z = dot(w, x)
    return math.log1p(math.exp(-abs(z))) + max(z, 0) - t * z


def accuracy(w, X, y):
    return sum((dot(w, x) > 0) == (t > 0.5) for x, t in zip(X, y)) / len(y)


def auc(pos, neg):
    s = 0.0
    for a in pos:
        for b in neg:
            s += 1.0 if a > b else 0.5 if a == b else 0.0
    return s / (len(pos) * len(neg))


def run(l2, label):
    Xi, yi = make(N_TRAIN)
    Xo, yo = make(N_OUT)
    w = train(Xi, yi, l2)
    li = [loss(w, x, t) for x, t in zip(Xi, yi)]
    lo = [loss(w, x, t) for x, t in zip(Xo, yo)]
    a = auc([-v for v in li], [-v for v in lo])
    allv = sorted(li + lo)
    thr = (allv[len(allv) // 2 - 1] + allv[len(allv) // 2]) / 2
    tpr = sum(v < thr for v in li) / len(li)
    fpr = sum(v < thr for v in lo) / len(lo)
    gap = accuracy(w, Xi, yi) - accuracy(w, Xo, yo)
    print(f"{label:24} train acc={accuracy(w, Xi, yi):.2f} held-out acc={accuracy(w, Xo, yo):.2f} "
          f"gap={gap:.2f} | attack AUC={a:.3f} advantage={tpr - fpr:.2f}")


def main():
    run(l2=0.0, label="unregularized (overfit)")
    run(l2=0.5, label="strong L2 (regularized)")


if __name__ == "__main__":
    main()
