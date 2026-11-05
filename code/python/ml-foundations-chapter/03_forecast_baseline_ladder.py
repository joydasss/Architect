"""Second end-to-end example for Chapter 16.01: forecasting daily support-ticket
volume with a time-respecting split and a baseline ladder.

Standard library only. Data is synthetic (fixed seed). Run:
python 03_forecast_baseline_ladder.py
"""
import math
import random

rng = random.Random(11)
DAYS = 28 * 14  # 392 days
WEEKDAY_EFFECT = [1.25, 1.10, 1.00, 0.98, 1.00, 0.55, 0.45]  # Mon..Sun multipliers
y = [round((200 + 0.35 * t) * WEEKDAY_EFFECT[t % 7] * math.exp(rng.gauss(0, 0.06))) for t in range(DAYS)]

TRAIN_END = 28 * 10  # first 280 days available at the first forecast origin
H = 7  # forecast horizon in days; a forecast is issued once per week


def mae(p, a):
    return sum(abs(x - z) for x, z in zip(p, a)) / len(p)


def asym_cost(p, a, c_under=3.0, c_over=1.0):
    total = 0.0
    for x, z in zip(p, a):
        e = x - z
        total += -e * c_under if e < 0 else e * c_over
    return total / len(p)


def solve(A, b):
    """Gaussian elimination with partial pivoting."""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[piv] = M[piv], M[c]
        for r in range(c + 1, n):
            f = M[r][c] / M[c][c]
            for k in range(c, n + 1):
                M[r][k] -= f * M[c][k]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (M[i][n] - sum(M[i][j] * x[j] for j in range(i + 1, n))) / M[i][i]
    return x


def features(t):
    return [1.0 if t % 7 == d else 0.0 for d in range(7)] + [float(t)]


def fit_linear(values, n):
    X = [features(t) for t in range(n)]
    d = len(X[0])
    XtX = [[sum(X[i][a] * X[i][b] for i in range(n)) for b in range(d)] for a in range(d)]
    Xty = [sum(X[i][a] * values[i] for i in range(n)) for a in range(d)]
    return solve(XtX, Xty)


def predict_linear(w, t):
    return sum(a * b for a, b in zip(w, features(t)))


def last_value(n, targets):
    return [y[n - 1]] * len(targets)


def same_weekday_last_week(n, targets):
    return [y[n - 7 + ((t - n) % 7)] for t in targets]


def mean_last_4_weeks(n, targets):
    return [sum(y[n - 28 + 7 * k + ((t - n) % 7)] for k in range(4)) / 4 for t in targets]


def linear_weekday_trend(n, targets):
    w = fit_linear(y[:n], n)
    return [predict_linear(w, t) for t in targets]


def log_linear(n, targets):
    w = fit_linear([math.log(v) for v in y[:n]], n)
    return [math.exp(predict_linear(w, t)) for t in targets]


def evaluate(method, margin=0.0):
    preds, actuals = [], []
    n = TRAIN_END
    while n + H <= DAYS:
        targets = list(range(n, n + H))
        preds += [p * (1 + margin) for p in method(n, targets)]
        actuals += y[n:n + H]
        n += H
    return preds, actuals


methods = [
    ("last value", last_value),
    ("same weekday last week", same_weekday_last_week),
    ("mean of last 4 same weekdays", mean_last_4_weeks),
    ("linear: weekday + trend", linear_weekday_trend),
    ("log-linear: weekday + trend", log_linear),
]

print(f"fit window starts with {TRAIN_END} days, test days={DAYS - TRAIN_END}, horizon={H}")
print(f"{'method':32s} {'MAE':>7s} {'asym cost':>10s}")
for name, m in methods:
    p, a = evaluate(m)
    print(f"{name:32s} {mae(p, a):7.2f} {asym_cost(p, a):10.2f}")

for margin in (0.0, 0.05, 0.10, 0.15):
    p, a = evaluate(log_linear, margin)
    print(f"log-linear with margin {margin:4.2f}: asym cost {asym_cost(p, a):7.2f}")
