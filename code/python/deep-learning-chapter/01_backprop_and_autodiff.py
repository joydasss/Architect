"""Backpropagation by hand, a reverse-mode autodiff engine, and a gradient check.

Standard library only (no NumPy or PyTorch needed).

Network: 2 inputs -> 2 ReLU hidden units -> 1 sigmoid output, binary cross-entropy.
The script
  1. runs the forward pass and the hand-derived backward pass (matrix-form rules),
  2. rebuilds the same computation with a tiny scalar autodiff engine and compares,
  3. checks every gradient against central finite differences,
  4. verifies the softmax cross-entropy gradient p - y on a 3-class example.
"""

import math

# ----------------------------------------------------------------------------
# Parameters and data (the chapter's worked example)
# ----------------------------------------------------------------------------
W1 = [[0.5, 0.4], [0.3, 0.8]]  # row j = weights into hidden unit j
b1 = [0.1, -0.2]
W2 = [0.6, -0.7]
b2 = 0.05
x = [1.0, 2.0]
y = 1.0


def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z))


def forward(W1, b1, W2, b2, x, y):
    z1 = [sum(W1[j][i] * x[i] for i in range(2)) + b1[j] for j in range(2)]
    h = [max(0.0, v) for v in z1]
    z2 = sum(W2[j] * h[j] for j in range(2)) + b2
    p = sigmoid(z2)
    loss = -(y * math.log(p) + (1 - y) * math.log(1 - p))
    return z1, h, z2, p, loss


def manual_backward(W1, b1, W2, b2, x, y):
    z1, h, z2, p, loss = forward(W1, b1, W2, b2, x, y)
    dz2 = p - y  # sigmoid + binary cross-entropy
    dW2 = [dz2 * h[j] for j in range(2)]
    db2 = dz2
    dh = [W2[j] * dz2 for j in range(2)]
    dz1 = [dh[j] * (1.0 if z1[j] > 0 else 0.0) for j in range(2)]
    dW1 = [[dz1[j] * x[i] for i in range(2)] for j in range(2)]
    db1 = dz1[:]
    return loss, dict(dz2=dz2, dW2=dW2, db2=db2, dh=dh, dz1=dz1, dW1=dW1, db1=db1)


# ----------------------------------------------------------------------------
# Minimal reverse-mode autodiff on scalars
# ----------------------------------------------------------------------------
class Value:
    def __init__(self, data, parents=(), backward=lambda: None):
        self.data = data
        self.grad = 0.0
        self._parents = parents
        self._backward = backward

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other))

        def _bw():
            self.grad += out.grad
            other.grad += out.grad

        out._backward = _bw
        return out

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other))

        def _bw():
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad

        out._backward = _bw
        return out

    def __neg__(self):
        return self * -1.0

    def __sub__(self, other):
        return self + (-other if isinstance(other, Value) else Value(-other))

    def relu(self):
        out = Value(max(0.0, self.data), (self,))

        def _bw():
            self.grad += (1.0 if self.data > 0 else 0.0) * out.grad

        out._backward = _bw
        return out

    def exp(self):
        e = math.exp(self.data)
        out = Value(e, (self,))

        def _bw():
            self.grad += e * out.grad

        out._backward = _bw
        return out

    def log(self):
        out = Value(math.log(self.data), (self,))

        def _bw():
            self.grad += out.grad / self.data

        out._backward = _bw
        return out

    def reciprocal(self):
        out = Value(1.0 / self.data, (self,))

        def _bw():
            self.grad += -1.0 / (self.data ** 2) * out.grad

        out._backward = _bw
        return out

    def backward(self):
        order, seen = [], set()

        def visit(v):
            if id(v) not in seen:
                seen.add(id(v))
                for p in v._parents:
                    visit(p)
                order.append(v)

        visit(self)
        self.grad = 1.0
        for v in reversed(order):
            v._backward()


def autodiff_run():
    w1 = [[Value(v) for v in row] for row in W1]
    bb1 = [Value(v) for v in b1]
    w2 = [Value(v) for v in W2]
    bb2 = Value(b2)
    xs = [Value(v) for v in x]
    h = []
    for j in range(2):
        z = w1[j][0] * xs[0] + w1[j][1] * xs[1] + bb1[j]
        h.append(z.relu())
    z2 = w2[0] * h[0] + w2[1] * h[1] + bb2
    p = (Value(1.0) + (-z2).exp()).reciprocal()
    loss = -(p.log()) if y == 1.0 else -((Value(1.0) - p).log())
    loss.backward()
    return loss, w1, bb1, w2, bb2


def numeric_grads(h=1e-6):
    base = [[W1[j][:] for j in range(2)], b1[:], W2[:], b2]

    def L(W1_, b1_, W2_, b2_):
        return forward(W1_, b1_, W2_, b2_, x, y)[4]

    out = {}
    g = [[0.0, 0.0], [0.0, 0.0]]
    for j in range(2):
        for i in range(2):
            a = [r[:] for r in W1]
            c = [r[:] for r in W1]
            a[j][i] += h
            c[j][i] -= h
            g[j][i] = (L(a, b1, W2, b2) - L(c, b1, W2, b2)) / (2 * h)
    out["dW1"] = g
    out["db1"] = []
    for j in range(2):
        a, c = b1[:], b1[:]
        a[j] += h
        c[j] -= h
        out["db1"].append((L(W1, a, W2, b2) - L(W1, c, W2, b2)) / (2 * h))
    out["dW2"] = []
    for j in range(2):
        a, c = W2[:], W2[:]
        a[j] += h
        c[j] -= h
        out["dW2"].append((L(W1, b1, a, b2) - L(W1, b1, c, b2)) / (2 * h))
    out["db2"] = (L(W1, b1, W2, b2 + h) - L(W1, b1, W2, b2 - h)) / (2 * h)
    return out


def softmax(z):
    m = max(z)
    e = [math.exp(v - m) for v in z]
    s = sum(e)
    return [v / s for v in e]


def main():
    z1, h, z2, p, loss = forward(W1, b1, W2, b2, x, y)
    print("== Forward pass ==")
    print(f"z1 = {[round(v, 4) for v in z1]}   h = {[round(v, 4) for v in h]}")
    print(f"z2 = {z2:.4f}   p = {p:.5f}   loss = {loss:.5f}")

    loss_m, g = manual_backward(W1, b1, W2, b2, x, y)
    print("\n== Manual backward pass ==")
    print(f"dL/dz2 = p - y = {g['dz2']:.5f}")
    print(f"dL/dW2 = {[round(v, 5) for v in g['dW2']]}   dL/db2 = {g['db2']:.5f}")
    print(f"dL/dh  = {[round(v, 5) for v in g['dh']]}")
    print(f"dL/dz1 = {[round(v, 5) for v in g['dz1']]}")
    print(f"dL/dW1 = {[[round(v, 5) for v in r] for r in g['dW1']]}")
    print(f"dL/db1 = {[round(v, 5) for v in g['db1']]}")

    loss_a, w1, bb1, w2, bb2 = autodiff_run()
    print("\n== Autodiff engine ==")
    print(f"loss = {loss_a.data:.5f}")
    print(f"dL/dW1 = {[[round(v.grad, 5) for v in r] for r in w1]}")
    print(f"dL/dW2 = {[round(v.grad, 5) for v in w2]}   dL/db2 = {bb2.grad:.5f}")

    n = numeric_grads()
    print("\n== Finite-difference check (h = 1e-6) ==")
    worst = 0.0
    pairs = []
    for j in range(2):
        for i in range(2):
            pairs.append((g["dW1"][j][i], n["dW1"][j][i], w1[j][i].grad))
        pairs.append((g["db1"][j], n["db1"][j], bb1[j].grad))
        pairs.append((g["dW2"][j], n["dW2"][j], w2[j].grad))
    pairs.append((g["db2"], n["db2"], bb2.grad))
    for man, num, auto in pairs:
        denom = max(abs(man), abs(num), 1e-12)
        worst = max(worst, abs(man - num) / denom, abs(man - auto) / denom)
    print(f"largest relative difference over {len(pairs)} parameters: {worst:.2e}")

    # One SGD step, learning rate 0.1
    lr = 0.1
    W1n = [[W1[j][i] - lr * g["dW1"][j][i] for i in range(2)] for j in range(2)]
    b1n = [b1[j] - lr * g["db1"][j] for j in range(2)]
    W2n = [W2[j] - lr * g["dW2"][j] for j in range(2)]
    b2n = b2 - lr * g["db2"]
    new_loss = forward(W1n, b1n, W2n, b2n, x, y)[4]
    print(f"\nAfter one SGD step (lr=0.1): loss {loss:.5f} -> {new_loss:.5f}")

    # Dead ReLU variant: same weights, input chosen so unit 0 is inactive
    xd = [-1.0, -2.0]
    z1d, hd, z2d, pd, ld = forward(W1, b1, W2, b2, xd, y)
    print(f"\nDead-unit input {xd}: z1 = {[round(v, 3) for v in z1d]}, "
          f"h = {[round(v, 3) for v in hd]}, p = {pd:.4f}, loss = {ld:.4f}")

    # Softmax cross-entropy gradient: p - y
    logits = [2.0, 1.0, 0.1]
    target = 0

    def ce(z):
        return -math.log(softmax(z)[target])

    p3 = softmax(logits)
    analytic = [p3[k] - (1.0 if k == target else 0.0) for k in range(3)]
    numeric = []
    for k in range(3):
        a, c = logits[:], logits[:]
        a[k] += 1e-6
        c[k] -= 1e-6
        numeric.append((ce(a) - ce(c)) / 2e-6)
    print("\n== Softmax cross-entropy ==")
    print(f"logits {logits} -> probs {[round(v, 4) for v in p3]}, loss {ce(logits):.4f}")
    print(f"analytic p - y : {[round(v, 4) for v in analytic]}")
    print(f"finite diff    : {[round(v, 4) for v in numeric]}")


if __name__ == "__main__":
    main()
