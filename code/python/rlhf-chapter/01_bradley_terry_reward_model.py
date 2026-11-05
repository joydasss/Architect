"""Bradley-Terry reward model: worked numbers and a tiny trainable model.

Standard library only. Prints:
1. The worked example from the chapter (one pair, loss and gradient).
2. A linear reward model r(x) = w . features trained on synthetic pairwise
   preferences generated from a known Bradley-Terry process, including a
   length shortcut that the annotators partly follow.
"""

import math
import random


def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z))


def worked_example():
    r_a, r_b = 1.2, 0.4
    margin = r_a - r_b
    p = sigmoid(margin)
    loss_if_a_wins = -math.log(p)
    loss_if_b_wins = -math.log(1.0 - p)
    grad_wrt_margin = -(1.0 - p)  # d loss / d margin when a wins
    print("== Worked example ==")
    print(f"margin r_a - r_b      = {margin:.2f}")
    print(f"P(a preferred)        = {p:.4f}")
    print(f"loss if a wins        = {loss_if_a_wins:.4f}")
    print(f"loss if b wins        = {loss_if_b_wins:.4f}")
    print(f"d loss / d margin     = {grad_wrt_margin:.4f} (a wins)")


def make_data(n_pairs, rng, length_pull):
    """Each response has two features: quality q and length z (both ~N(0,1)).

    True utility used by annotators: u = 1.0*q + length_pull*z.
    The *intended* objective is quality only.
    """
    data = []
    for _ in range(n_pairs):
        a = (rng.gauss(0, 1), rng.gauss(0, 1))
        b = (rng.gauss(0, 1), rng.gauss(0, 1))
        ua = 1.0 * a[0] + length_pull * a[1]
        ub = 1.0 * b[0] + length_pull * b[1]
        a_wins = rng.random() < sigmoid(ua - ub)
        data.append((a, b) if a_wins else (b, a))  # (chosen, rejected)
    return data


def train(data, epochs=200, lr=0.5):
    w = [0.0, 0.0]
    for _ in range(epochs):
        g = [0.0, 0.0]
        for chosen, rejected in data:
            d = [chosen[i] - rejected[i] for i in range(2)]
            margin = w[0] * d[0] + w[1] * d[1]
            coef = -(1.0 - sigmoid(margin))
            g[0] += coef * d[0]
            g[1] += coef * d[1]
        for i in range(2):
            w[i] -= lr * g[i] / len(data)
    return w


def evaluate(w, data):
    correct, loss = 0, 0.0
    for chosen, rejected in data:
        margin = sum(w[i] * (chosen[i] - rejected[i]) for i in range(2))
        correct += margin > 0
        loss += -math.log(sigmoid(margin))
    return correct / len(data), loss / len(data)


def main():
    worked_example()
    rng = random.Random(7)
    train_set = make_data(3000, rng, length_pull=0.8)
    test_set = make_data(3000, rng, length_pull=0.8)
    w = train(train_set)
    acc, loss = evaluate(w, test_set)
    print("\n== Learned reward model (annotators partly follow length) ==")
    print(f"weights: quality={w[0]:.2f} length={w[1]:.2f} (true 1.00, 0.80)")
    print(f"held-out pairwise accuracy = {acc:.3f}, mean NLL = {loss:.3f}")

    # Accuracy ceiling: the best possible predictor knows the true utility.
    oracle_acc, oracle_loss = evaluate([1.0, 0.8], test_set)
    print(f"oracle (true weights)      = {oracle_acc:.3f}, mean NLL = {oracle_loss:.3f}")

    # Intended-quality-only judge disagrees with the labels this often.
    quality_only, _ = evaluate([1.0, 0.0], test_set)
    print(f"quality-only agreement with labels = {quality_only:.3f}")


if __name__ == "__main__":
    main()
