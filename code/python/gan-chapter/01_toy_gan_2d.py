"""Minimal GAN on a 2-D mixture of four Gaussians (CH11). Standard library only.

Both networks are small multilayer perceptrons with hand-written backpropagation,
so the update rule is visible. The generator uses the non-saturating loss.

Usage:
    python 01_toy_gan_2d.py [steps] [seed] [d_steps] [n_modes]

Defaults: 3000 steps, seed 0, 1 discriminator step per generator step, 4 modes.
With n_modes other than 4 the target is a ring of that many Gaussians (radius 2,
std 0.1), a standard mode-collapse benchmark.
Prints the discriminator loss, the generator loss, the mean discriminator
probability on real and fake batches, and mode coverage every 500 steps.
Pure Python is slow, so a default run takes a few minutes.
"""
import math
import random
import sys

STEPS = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 0
D_STEPS = int(sys.argv[3]) if len(sys.argv) > 3 else 1
N_MODES = int(sys.argv[4]) if len(sys.argv) > 4 else 4
BATCH = 32
HID = 16
LR = 2e-3
if N_MODES == 4:
    CENTERS = [(1.5, 1.5), (1.5, -1.5), (-1.5, 1.5), (-1.5, -1.5)]
    STD = 0.2
else:  # ring of N_MODES Gaussians, the classic mode-collapse benchmark
    CENTERS = [(2.0 * math.cos(2 * math.pi * k / N_MODES), 2.0 * math.sin(2 * math.pi * k / N_MODES))
               for k in range(N_MODES)]
    STD = 0.1
rng = random.Random(SEED)


def sample_real(n):
    out = []
    for _ in range(n):
        cx, cy = CENTERS[rng.randrange(N_MODES)]
        out.append([rng.gauss(cx, STD), rng.gauss(cy, STD)])
    return out


def make_mlp(sizes):
    layers = []
    for i in range(len(sizes) - 1):
        scale = math.sqrt(1.0 / sizes[i])
        layers.append({
            "W": [[rng.gauss(0, scale) for _ in range(sizes[i])] for _ in range(sizes[i + 1])],
            "b": [0.0] * sizes[i + 1],
        })
    return layers


def zero_grads(layers):
    return [{"W": [[0.0] * len(r) for r in L["W"]], "b": [0.0] * len(L["b"])} for L in layers]


def forward(layers, x):
    acts = [x]
    h = x
    for i, L in enumerate(layers):
        z = [sum(w * a for w, a in zip(row, h)) + b for row, b in zip(L["W"], L["b"])]
        h = z if i == len(layers) - 1 else [math.tanh(v) for v in z]
        acts.append(h)
    return h, acts


def backward(layers, acts, gout, grads):
    """Accumulate parameter gradients into grads. Return gradient w.r.t. the input."""
    g = gout
    for i in range(len(layers) - 1, -1, -1):
        L, G, h_in, h_out = layers[i], grads[i], acts[i], acts[i + 1]
        if i != len(layers) - 1:
            g = [gv * (1 - o * o) for gv, o in zip(g, h_out)]
        for j, gj in enumerate(g):
            G["b"][j] += gj
            row = G["W"][j]
            for k, a in enumerate(h_in):
                row[k] += gj * a
        g = [sum(L["W"][j][k] * g[j] for j in range(len(g))) for k in range(len(h_in))]
    return g


class Adam:
    def __init__(self, layers, lr, b1=0.5, b2=0.999):
        self.layers, self.lr, self.b1, self.b2, self.t = layers, lr, b1, b2, 0
        self.m = zero_grads(layers)
        self.v = zero_grads(layers)

    def step(self, grads, scale):
        self.t += 1
        c1 = 1 - self.b1 ** self.t
        c2 = 1 - self.b2 ** self.t
        for L, G, M, V in zip(self.layers, grads, self.m, self.v):
            for name in ("W", "b"):
                if name == "W":
                    pairs = [(L["W"][j], G["W"][j], M["W"][j], V["W"][j]) for j in range(len(L["W"]))]
                else:
                    pairs = [(L["b"], G["b"], M["b"], V["b"])]
                for p, g, m, v in pairs:
                    for k in range(len(p)):
                        gk = g[k] * scale
                        m[k] = self.b1 * m[k] + (1 - self.b1) * gk
                        v[k] = self.b2 * v[k] + (1 - self.b2) * gk * gk
                        p[k] -= self.lr * (m[k] / c1) / (math.sqrt(v[k] / c2) + 1e-8)


def sigmoid(a):
    return 1 / (1 + math.exp(-a)) if a >= 0 else math.exp(a) / (1 + math.exp(a))


def softplus(a):
    return max(a, 0) + math.log1p(math.exp(-abs(a)))


G_NET = make_mlp([2, HID, HID, 2])
D_NET = make_mlp([2, HID, HID, 1])
g_opt = Adam(G_NET, LR)
d_opt = Adam(D_NET, LR)


def generate(n):
    return [forward(G_NET, [rng.gauss(0, 1), rng.gauss(0, 1)])[0] for _ in range(n)]


def coverage(n=1000):
    """Count samples within 3 std of each mode. Return per-mode counts and the on-mode fraction."""
    counts = [0] * N_MODES
    for x, y in generate(n):
        for k, (cx, cy) in enumerate(CENTERS):
            if math.hypot(x - cx, y - cy) < 3 * STD:
                counts[k] += 1
                break
    return counts, sum(counts) / n


print("steps=%d seed=%d d_steps=%d batch=%d hidden=%d lr=%g" % (STEPS, SEED, D_STEPS, BATCH, HID, LR))
d_loss_acc = g_loss_acc = dr_acc = df_acc = 0.0
n_acc = 0
for step in range(1, STEPS + 1):
    for _ in range(D_STEPS):
        grads = zero_grads(D_NET)
        real = sample_real(BATCH)
        fake = generate(BATCH)
        dl = 0.0
        for x in real:
            a, acts = forward(D_NET, x)
            dl += softplus(-a[0])
            dr_acc += sigmoid(a[0])
            backward(D_NET, acts, [-(1 - sigmoid(a[0]))], grads)
        for x in fake:
            a, acts = forward(D_NET, x)
            dl += softplus(a[0])
            df_acc += sigmoid(a[0])
            backward(D_NET, acts, [sigmoid(a[0])], grads)
        d_opt.step(grads, 1.0 / BATCH)
        d_loss_acc += dl / BATCH
    # generator step, non-saturating loss: minimise softplus(-a) = -log D(G(z))
    g_grads = zero_grads(G_NET)
    scratch = zero_grads(D_NET)
    gl = 0.0
    for _ in range(BATCH):
        z = [rng.gauss(0, 1), rng.gauss(0, 1)]
        x, g_acts = forward(G_NET, z)
        a, d_acts = forward(D_NET, x)
        gl += softplus(-a[0])
        gx = backward(D_NET, d_acts, [-(1 - sigmoid(a[0]))], scratch)
        backward(G_NET, g_acts, gx, g_grads)
    g_opt.step(g_grads, 1.0 / BATCH)
    g_loss_acc += gl / BATCH
    n_acc += 1
    if step % 500 == 0:
        counts, frac = coverage()
        print("step %5d  D_loss %.3f  G_loss %.3f  D(real) %.2f  D(fake) %.2f  modes_hit %d/%d  on_mode %.2f  counts %s"
              % (step, d_loss_acc / (n_acc * D_STEPS), g_loss_acc / n_acc,
                 dr_acc / (n_acc * D_STEPS * BATCH), df_acc / (n_acc * D_STEPS * BATCH),
                 sum(1 for c in counts if c > 20), N_MODES, frac, counts))
        d_loss_acc = g_loss_acc = dr_acc = df_acc = 0.0
        n_acc = 0
