"""Model merging (task arithmetic, TIES, SLERP) and 4-bit quantization error.

Standard library only. Weights are tiny vectors so the arithmetic is visible.

Run: python 04_merging_and_nf4.py
"""
import math
import random

random.seed(3)

base = [0.50, -0.20, 0.10, 0.80, -0.60, 0.30]
ft_a = [0.62, -0.20, 0.10, 0.70, -0.60, 0.34]    # task A fine-tune
ft_b = [0.40, -0.20, 0.25, 0.70, -0.45, 0.30]    # task B fine-tune
tv_a = [a - b for a, b in zip(ft_a, base)]
tv_b = [a - b for a, b in zip(ft_b, base)]
fmt = lambda v: "[" + ", ".join(f"{x:+.3f}" for x in v) + "]"
print("task vector A:", fmt(tv_a))
print("task vector B:", fmt(tv_b))

lam = 0.7
ta = [b + lam * (x + y) for b, x, y in zip(base, tv_a, tv_b)]
print(f"task arithmetic (lambda={lam}):", fmt(ta))


def ties(tvs, density=0.5, lam=1.0):
    # trim: keep top-density fraction by magnitude per task vector
    trimmed = []
    for tv in tvs:
        k = max(1, int(round(density * len(tv))))
        thr = sorted((abs(x) for x in tv), reverse=True)[k - 1]
        trimmed.append([x if abs(x) >= thr else 0.0 for x in tv])
    out = []
    for i in range(len(tvs[0])):
        vals = [t[i] for t in trimmed]
        mass = sum(vals)                       # elect sign by total mass
        sign = 1 if mass >= 0 else -1
        agree = [v for v in vals if v * sign > 0]
        out.append(lam * sum(agree) / len(agree) if agree else 0.0)  # disjoint mean
    return out


tm = ties([tv_a, tv_b])
print("TIES merged update:", fmt(tm))
print("TIES merged weights:", fmt([b + x for b, x in zip(base, tm)]))


def slerp(p, q, t):
    dot = sum(a * b for a, b in zip(p, q))
    n = math.sqrt(sum(a * a for a in p)) * math.sqrt(sum(b * b for b in q))
    omega = math.acos(max(-1, min(1, dot / n)))
    s = math.sin(omega)
    return [(math.sin((1 - t) * omega) / s) * a + (math.sin(t * omega) / s) * b
            for a, b in zip(p, q)]


sl = slerp(ft_a, ft_b, 0.5)
lerp = [(a + b) / 2 for a, b in zip(ft_a, ft_b)]
norm = lambda v: math.sqrt(sum(x * x for x in v))
print(f"SLERP midpoint norm = {norm(sl):.4f}, linear midpoint norm = {norm(lerp):.4f}, "
      f"endpoint norms = {norm(ft_a):.4f} / {norm(ft_b):.4f}")

# ---- 4-bit quantization error ---------------------------------------
# NF4 levels are quantiles of a standard normal scaled to [-1, 1]. We use the
# published 16 NF4 values from the QLoRA paper (Dettmers et al., 2023).
NF4 = [-1.0, -0.6962, -0.5251, -0.3949, -0.2844, -0.1848, -0.0911, 0.0,
       0.0796, 0.1609, 0.2461, 0.3379, 0.4407, 0.5626, 0.7230, 1.0]
INT4 = [(i - 7.5) / 7.5 for i in range(16)]        # uniform 16-level grid


def quant(block, levels):
    absmax = max(abs(x) for x in block)
    return [absmax * min(levels, key=lambda l: abs(x / absmax - l)) for x in block]


def mse(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) / len(a)


w = [random.gauss(0, 0.02) for _ in range(64 * 400)]
blocks = [w[i:i + 64] for i in range(0, len(w), 64)]
e_nf4 = sum(mse(b, quant(b, NF4)) for b in blocks) / len(blocks)
e_int = sum(mse(b, quant(b, INT4)) for b in blocks) / len(blocks)
var = sum(x * x for x in w) / len(w)
print(f"\nGaussian weights, block 64: signal-to-noise NF4 = {var / e_nf4:.1f}x, "
      f"uniform 4-bit = {var / e_int:.1f}x")
