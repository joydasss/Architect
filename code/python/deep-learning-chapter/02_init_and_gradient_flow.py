"""Weight initialization and signal propagation in a deep plain network.

Standard library only. Builds a 30-layer, width-64 network without
normalization or residual connections and measures, per layer:
  * the standard deviation of forward activations,
  * the root-mean-square of the backward gradient signal.
It compares small-normal, Xavier (Glorot), He, and too-large initializations
for tanh and ReLU activations. Matches the table in the chapter.
"""

import math
import random

WIDTH = 64
DEPTH = 30
BATCH = 8
REPORT = [1, 5, 10, 20, 30]


def make_weights(std, rng):
    return [[rng.gauss(0.0, std) for _ in range(WIDTH)] for _ in range(WIDTH)]


def matvec(W, v):
    return [sum(W[j][i] * v[i] for i in range(WIDTH)) for j in range(WIDTH)]


def matTvec(W, v):
    return [sum(W[j][i] * v[j] for j in range(WIDTH)) for i in range(WIDTH)]


def rms(vs):
    flat = [a for v in vs for a in v]
    return math.sqrt(sum(a * a for a in flat) / len(flat))


def act(name, z):
    return math.tanh(z) if name == "tanh" else max(0.0, z)


def dact(name, z, a):
    return 1.0 - a * a if name == "tanh" else (1.0 if z > 0 else 0.0)


def run(name, std, seed=0):
    rng = random.Random(seed)
    Ws = [make_weights(std, rng) for _ in range(DEPTH)]
    xs = [[rng.gauss(0.0, 1.0) for _ in range(WIDTH)] for _ in range(BATCH)]
    zs_all, as_all = [], []
    cur = xs
    for l in range(DEPTH):
        zs = [matvec(Ws[l], v) for v in cur]
        a = [[act(name, z) for z in zv] for zv in zs]
        zs_all.append(zs)
        as_all.append(a)
        cur = a
    fwd = [rms(as_all[l - 1]) for l in REPORT]
    # backward: start with unit-variance gradient at the top activation
    g = [[rng.gauss(0.0, 1.0) for _ in range(WIDTH)] for _ in range(BATCH)]
    back = {}
    for l in range(DEPTH - 1, -1, -1):
        gz = [[g[b][j] * dact(name, zs_all[l][b][j], as_all[l][b][j]) for j in range(WIDTH)]
              for b in range(BATCH)]
        g = [matTvec(Ws[l], gz[b]) for b in range(BATCH)]
        back[l + 1] = rms(gz)
    bwd = [back[l] for l in REPORT]
    return fwd, bwd


def main():
    configs = [
        ("tanh", 0.01, "tanh, N(0, 0.01^2)"),
        ("tanh", math.sqrt(1.0 / WIDTH), "tanh, Xavier std=1/sqrt(64)"),
        ("tanh", 1.0, "tanh, N(0, 1)"),
        ("relu", math.sqrt(1.0 / WIDTH), "ReLU, Xavier std=1/sqrt(64)"),
        ("relu", math.sqrt(2.0 / WIDTH), "ReLU, He std=sqrt(2/64)"),
    ]
    print(f"depth={DEPTH} width={WIDTH} batch={BATCH}; layers reported: {REPORT}")
    print("\nForward activation RMS at those layers")
    results = []
    for name, std, label in configs:
        fwd, bwd = run(name, std)
        results.append((label, fwd, bwd))
        print(f"{label:32s} " + "  ".join(f"{v:10.3e}" for v in fwd))
    print("\nBackward pre-activation gradient RMS at those layers (top-layer gradient RMS ~ 1)")
    for label, fwd, bwd in results:
        print(f"{label:32s} " + "  ".join(f"{v:10.3e}" for v in bwd))


if __name__ == "__main__":
    main()
