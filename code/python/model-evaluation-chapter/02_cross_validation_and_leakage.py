"""Random vs group vs time-ordered validation, and selection bias.

Standard library only. Run: python 02_cross_validation_and_leakage.py
Synthetic data: each customer has a persistent offset, so rows from one
customer are not independent. A 1-nearest-neighbour model memorises customers.
"""
import random
import statistics


def make_data(rng, n_customers=200, rows_each=10):
    rows = []
    for c in range(n_customers):
        offset = rng.gauss(0, 3.0)          # customer-specific signal
        label = 1 if rng.random() < 0.5 else 0
        # The label is a customer-level coin flip. The feature only identifies
        # the customer (a stable fingerprint), so it cannot predict a new one.
        for t in range(rows_each):
            x = offset + rng.gauss(0, 0.02)
            rows.append((c, t, x, label))
    return rows


def predict_1nn(train, x):
    return min(train, key=lambda r: abs(r[2] - x))[3]


def accuracy(train, test):
    return sum(predict_1nn(train, r[2]) == r[3] for r in test) / len(test)


def random_kfold(rows, k, rng):
    idx = list(range(len(rows)))
    rng.shuffle(idx)
    folds = [idx[i::k] for i in range(k)]
    scores = []
    for f in folds:
        fs = set(f)
        test = [rows[i] for i in f]
        train = [rows[i] for i in idx if i not in fs]
        scores.append(accuracy(train, test))
    return statistics.mean(scores)


def group_kfold(rows, k, rng):
    groups = sorted({r[0] for r in rows})
    rng.shuffle(groups)
    scores = []
    for i in range(k):
        held = set(groups[i::k])
        test = [r for r in rows if r[0] in held]
        train = [r for r in rows if r[0] not in held]
        scores.append(accuracy(train, test))
    return statistics.mean(scores)


def selection_bias(rng):
    """Pick the best of M useless models on one validation set."""
    n_val, m = 500, 40
    y = [rng.random() < 0.5 for _ in range(n_val)]
    best = 0.0
    for _ in range(m):
        guess = [rng.random() < 0.5 for _ in range(n_val)]
        acc = sum(a == b for a, b in zip(guess, y)) / n_val
        best = max(best, acc)
    fresh = [rng.random() < 0.5 for _ in range(n_val)]
    fresh_guess = [rng.random() < 0.5 for _ in range(n_val)]
    fresh_acc = sum(a == b for a, b in zip(fresh_guess, fresh)) / n_val
    return best, fresh_acc


def rolling_origin_demo():
    print("== Rolling-origin splits over 12 months (expanding window) ==")
    months = list(range(1, 13))
    start, horizon = 6, 2
    origin = start
    while origin + horizon <= 12:
        tr = f"{months[0]}-{origin}"
        te = f"{origin + 1}-{origin + horizon}"
        print(f"train months {tr:<5} test months {te}")
        origin += horizon
    print()


if __name__ == "__main__":
    rng = random.Random(11)
    rows = make_data(rng)
    print("== Customer-persistent data, 200 customers x 10 rows, 1-NN ==")
    print(f"random 5-fold accuracy: {random_kfold(rows, 5, random.Random(1)):.3f}")
    print(f"group  5-fold accuracy: {group_kfold(rows, 5, random.Random(1)):.3f}")
    print("(true generalisation to new customers is the group number)\n")
    srng = random.Random(5)
    trials = [selection_bias(srng) for _ in range(300)]
    print("== Selection bias: best of 40 coin-flip models, 500 validation rows ==")
    print(f"mean best validation accuracy over 300 repeats: {statistics.mean(t[0] for t in trials):.3f}")
    print(f"mean accuracy of the chosen kind of model on fresh data: {statistics.mean(t[1] for t in trials):.3f}\n")
    rolling_origin_demo()
