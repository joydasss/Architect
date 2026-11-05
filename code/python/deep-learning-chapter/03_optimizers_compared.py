"""Optimizer update rules compared on an ill-conditioned quadratic.

Standard library only. Loss f(w) = 0.5 * (w1^2 + 100 * w2^2), so the Hessian
eigenvalues are 1 and 100 (condition number 100) and the stability limit for
plain gradient descent is learning rate 2/100 = 0.02.

Part 1: steps for each optimizer to reach f < 1e-6 from (1, 1).
Part 2: SGD learning-rate sensitivity around the stability limit.
Part 3: Adam with L2 in the loss versus AdamW (decoupled decay) when two
        weights see gradients of different scale.
"""

import math

A = (1.0, 100.0)


def f(w):
    return 0.5 * (A[0] * w[0] ** 2 + A[1] * w[1] ** 2)


def grad(w):
    return [A[0] * w[0], A[1] * w[1]]


def run(name, step_fn, max_steps=5000, tol=1e-6):
    w = [1.0, 1.0]
    state = {}
    for t in range(1, max_steps + 1):
        g = grad(w)
        w = step_fn(w, g, state, t)
        val = f(w)
        if not math.isfinite(val) or val > 1e12:
            return name, None, val
        if val < tol:
            return name, t, val
    return name, max_steps, f(w)


def sgd(lr):
    def step(w, g, s, t):
        return [w[i] - lr * g[i] for i in range(2)]
    return step


def momentum(lr, mu, nesterov=False):
    def step(w, g, s, t):
        v = s.setdefault("v", [0.0, 0.0])
        if nesterov:
            # gradient at the look-ahead point w - lr*mu*v
            look = [w[i] - lr * mu * v[i] for i in range(2)]
            g = grad(look)
        for i in range(2):
            v[i] = mu * v[i] + g[i]
        return [w[i] - lr * v[i] for i in range(2)]
    return step


def rmsprop(lr, rho=0.9, eps=1e-8):
    def step(w, g, s, t):
        sq = s.setdefault("sq", [0.0, 0.0])
        for i in range(2):
            sq[i] = rho * sq[i] + (1 - rho) * g[i] ** 2
        return [w[i] - lr * g[i] / (math.sqrt(sq[i]) + eps) for i in range(2)]
    return step


def adam(lr, b1=0.9, b2=0.999, eps=1e-8):
    def step(w, g, s, t):
        m = s.setdefault("m", [0.0, 0.0])
        v = s.setdefault("v", [0.0, 0.0])
        out = []
        for i in range(2):
            m[i] = b1 * m[i] + (1 - b1) * g[i]
            v[i] = b2 * v[i] + (1 - b2) * g[i] ** 2
            mh = m[i] / (1 - b1 ** t)
            vh = v[i] / (1 - b2 ** t)
            out.append(w[i] - lr * mh / (math.sqrt(vh) + eps))
        return out
    return step


def decay_demo(mode, lam=0.1, lr=0.05, steps=6000, b1=0.9, b2=0.999, eps=1e-8):
    """Two scalar weights; loss gradients -1 and -5 push both upward."""
    gs = [-1.0, -5.0]
    w = [0.0, 0.0]
    m = [0.0, 0.0]
    v = [0.0, 0.0]
    for t in range(1, steps + 1):
        for i in range(2):
            g = gs[i] + (lam * w[i] if mode == "adam_l2" else 0.0)
            m[i] = b1 * m[i] + (1 - b1) * g
            v[i] = b2 * v[i] + (1 - b2) * g * g
            mh = m[i] / (1 - b1 ** t)
            vh = v[i] / (1 - b2 ** t)
            upd = mh / (math.sqrt(vh) + eps)
            if mode == "adamw":
                upd += lam * w[i]
            w[i] -= lr * upd
    return w


def main():
    print("== Steps to reach f < 1e-6 from (1, 1) (None = diverged, 5000 = not reached) ==")
    rows = [
        run("SGD lr=0.01 (= 1/L)", sgd(0.01)),
        run("SGD lr=0.019", sgd(0.019)),
        run("SGD lr=0.021 (> 2/L)", sgd(0.021)),
        run("Momentum lr=0.01 mu=0.9", momentum(0.01, 0.9)),
        run("Nesterov lr=0.01 mu=0.9", momentum(0.01, 0.9, True)),
        run("RMSProp lr=0.01", rmsprop(0.01)),
        run("Adam lr=0.1", adam(0.1)),
        run("Adam lr=0.01", adam(0.01)),
    ]
    for name, steps, val in rows:
        print(f"{name:28s} steps={steps!s:>5}  final f={val:.2e}")

    print("\n== SGD learning-rate sensitivity: f after 100 steps ==")
    for lr in (0.001, 0.005, 0.01, 0.015, 0.019, 0.02, 0.021):
        w = [1.0, 1.0]
        for _ in range(100):
            g = grad(w)
            w = [w[i] - lr * g[i] for i in range(2)]
        print(f"lr={lr:<6} f={f(w):.3e}")

    print("\n== Adam + L2 versus AdamW (lambda=0.1, loss gradients -1 and -5) ==")
    print("Equilibrium of loss + L2 penalty: w = -g/lambda -> (10, 50)")
    print("Adam with L2 in loss : w = %s" % [round(x, 2) for x in decay_demo("adam_l2")])
    print("AdamW decoupled decay: w = %s" % [round(x, 2) for x in decay_demo("adamw")])


if __name__ == "__main__":
    main()
