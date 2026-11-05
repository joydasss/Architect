"""Probability, information theory, MLE/MAP, and a saddle point, with numbers
quoted in Chapter 16.01 (Machine Learning Foundations).

Standard library only. Run: python 01_probability_information_and_estimation.py
"""
import math


def bayes(prevalence, sensitivity, false_positive_rate):
    p_pos = sensitivity * prevalence + false_positive_rate * (1 - prevalence)
    return sensitivity * prevalence / p_pos, p_pos


def entropy(p, base=2):
    return -sum(x * math.log(x, base) for x in p if x > 0)


def cross_entropy(p, q, base=2):
    return -sum(x * math.log(y, base) for x, y in zip(p, q) if x > 0)


def kl(p, q, base=2):
    return cross_entropy(p, q, base) - entropy(p, base)


def main():
    print("== Bayes rule (screening) ==")
    post, p_pos = bayes(0.01, 0.90, 0.05)
    print(f"P(positive)={p_pos:.4f}  P(condition | positive)={post:.4f}")
    post2, _ = bayes(0.10, 0.90, 0.05)
    print(f"prevalence 10%: P(condition | positive)={post2:.4f}")

    print("\n== MLE and MAP for a Bernoulli rate (7 successes in 10) ==")
    k, n = 7, 10
    print(f"MLE p = k/n = {k / n:.4f}")
    a, b = 2, 2
    print(f"MAP with Beta({a},{b}) = (k+a-1)/(n+a+b-2) = {(k + a - 1) / (n + a + b - 2):.4f}")
    k, n = 3, 3
    print(f"3 of 3: MLE={k / n:.4f}  MAP Beta(2,2)={(k + 1) / (n + 2):.4f}")

    print("\n== Gaussian MLE ==")
    xs = [2.0, 4.0, 4.0, 6.0]
    mu = sum(xs) / len(xs)
    var_mle = sum((x - mu) ** 2 for x in xs) / len(xs)
    var_unb = sum((x - mu) ** 2 for x in xs) / (len(xs) - 1)
    print(f"mean={mu:.3f}  variance MLE (divide by n)={var_mle:.3f}  unbiased (n-1)={var_unb:.3f}")

    print("\n== Entropy, cross-entropy, KL (bits) ==")
    p = [0.5, 0.25, 0.25]
    q = [1 / 3, 1 / 3, 1 / 3]
    print(f"H(p)={entropy(p):.4f}  H(p,q)={cross_entropy(p, q):.4f}  KL(p||q)={kl(p, q):.4f}")
    print(f"KL(q||p)={kl(q, p):.4f}  (asymmetric)")
    one_hot = [1.0, 0.0, 0.0]
    probs = [0.7, 0.2, 0.1]
    print(f"one-hot label, model probs {probs}: cross-entropy in nats={cross_entropy(one_hot, probs, math.e):.4f}")

    print("\n== Saddle point f(x,y)=x^2-y^2, gradient descent eta=0.1 from (1.0, 0.01) ==")
    x, y = 1.0, 0.01
    for step in range(0, 31):
        if step in (0, 5, 10, 20, 30):
            print(f"step {step:2d}  x={x:9.5f}  y={y:9.5f}  f={x * x - y * y:9.5f}")
        gx, gy = 2 * x, -2 * y
        x, y = x - 0.1 * gx, y - 0.1 * gy


if __name__ == "__main__":
    main()
