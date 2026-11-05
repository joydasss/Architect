"""Low-rank adaptation (LoRA) demo in pure Python (no NumPy, no PyTorch).

A frozen layer W (d_out x d_in) is adapted by delta = (alpha / r) * B @ A.
We train only A and B by gradient descent so that W + delta reproduces a
teacher layer W_star = W + (rank-2 update). Then we show that merging the
update into W gives the same outputs as the unmerged path.

Run: python 01_lora_demo.py
"""
import math
import random

random.seed(7)


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))]
            for i in range(len(a))]


def transpose(a):
    return [list(r) for r in zip(*a)]


def add(a, b, s=1.0):
    return [[x + s * y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def scale(a, s):
    return [[x * s for x in r] for r in a]


def randn(r, c, std):
    return [[random.gauss(0, std) for _ in range(c)] for _ in range(r)]


def frob(a):
    return math.sqrt(sum(x * x for r in a for x in r))


d_out, d_in, r_true, r, alpha = 12, 10, 2, 4, 8
W = randn(d_out, d_in, 0.5)
# Teacher update has true rank 2.
U = randn(d_out, r_true, 0.5)
V = randn(r_true, d_in, 0.5)
W_star = add(W, matmul(U, V))

# LoRA init: A random small, B zero, so delta starts at exactly zero.
A = randn(r, d_in, 1 / math.sqrt(d_in))
B = [[0.0] * r for _ in range(d_out)]
s = alpha / r

X = randn(d_in, 64, 1.0)           # 64 input columns
Y = matmul(W_star, X)              # teacher outputs
n = len(X[0])


def loss_and_grads(A, B):
    delta = scale(matmul(B, A), s)
    pred = matmul(add(W, delta), X)
    E = add(pred, Y, -1.0)         # error
    loss = sum(x * x for row in E for x in row) / (d_out * n)
    G = scale(E, 2.0 / (d_out * n))               # dL/dpred
    dDelta = matmul(G, transpose(X))              # dL/ddelta (d_out x d_in)
    dB = scale(matmul(dDelta, transpose(A)), s)   # d_out x r
    dA = scale(matmul(transpose(B), dDelta), s)   # r x d_in
    return loss, dA, dB


full_params = d_out * d_in
lora_params = r * (d_in + d_out)
print(f"full layer params = {full_params}, LoRA params (r={r}) = {lora_params}, "
      f"ratio = {lora_params / full_params:.2f}")

lr = 0.05
for step in range(1501):
    loss, dA, dB = loss_and_grads(A, B)
    if step in (0, 100, 500, 1000, 1500):
        print(f"step {step:4d}  mse = {loss:.6f}")
    A = add(A, dA, -lr)
    B = add(B, dB, -lr)

# Merge: W_merged = W + s * B @ A. Compare to the unmerged path.
W_merged = add(W, scale(matmul(B, A), s))
x = randn(d_in, 1, 1.0)
unmerged = add(matmul(W, x), scale(matmul(B, matmul(A, x)), s))
merged = matmul(W_merged, x)
diff = max(abs(u[0] - m[0]) for u, m in zip(unmerged, merged))
print(f"max |merged - unmerged| output difference = {diff:.2e}")
print(f"relative error of learned update vs teacher update: "
      f"{frob(add(W_merged, W_star, -1.0)) / frob(add(W_star, W, -1.0)):.4f}")
