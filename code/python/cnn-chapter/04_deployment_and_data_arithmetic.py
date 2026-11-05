"""Arithmetic for augmentation, quantization, distillation, class imbalance,
adversarial sensitivity, latency budgets, and labeling cost.

Standard library only. Run: python 04_deployment_and_data_arithmetic.py

All inputs marked "illustrative" are assumptions chosen to show the
calculation, not measurements of any product.
"""

import math
import random


def softmax(z, t=1.0):
    m = max(z)
    e = [math.exp((v - m) / t) for v in z]
    s = sum(e)
    return [v / s for v in e]


def quantize_symmetric(values, bits=8):
    qmax = 2 ** (bits - 1) - 1
    scale = max(abs(v) for v in values) / qmax
    q = [max(-qmax - 1, min(qmax, round(v / scale))) for v in values]
    return [x * scale for x in q], scale


def main():
    print("=== mixup and CutMix label arithmetic ===")
    lam = 0.7
    y_a, y_b = [1, 0, 0], [0, 1, 0]
    print("mixup lambda 0.7 label:", [round(lam * a + (1 - lam) * b, 2)
                                       for a, b in zip(y_a, y_b)])
    h = w = 224
    cut_h = cut_w = 112
    lam_cut = 1 - (cut_h * cut_w) / (h * w)
    print("CutMix 112x112 patch on 224x224: lambda =", lam_cut)
    target = 0.3
    side = math.sqrt(1 - target) * 224
    print("for lambda 0.3 the patch side is sqrt(0.7)*224 =", round(side, 1), "pixels")

    print("\n=== Model size by precision (ResNet-50, 25,557,032 parameters) ===")
    n = 25_557_032
    for name, b in (("fp32", 4), ("fp16", 2), ("int8", 1)):
        print(f"{name}: {n * b} bytes = {n * b / 2**20:.1f} MiB")

    print("\n=== int8 symmetric quantization: per-tensor versus per-channel ===")
    random.seed(7)
    scales = [0.05, 0.1, 0.5, 2.0]
    channels = [[random.gauss(0, s) for _ in range(64)] for s in scales]
    flat = [v for ch in channels for v in ch]
    deq, sc = quantize_symmetric(flat)
    err_tensor = sum(abs(a - b) for a, b in zip(flat, deq)) / len(flat)
    print("per-tensor scale:", round(sc, 5), " mean abs error:", round(err_tensor, 5))
    errs = []
    for ch in channels:
        d, s = quantize_symmetric(ch)
        errs.extend(abs(a - b) for a, b in zip(ch, d))
    print("per-channel mean abs error:", round(sum(errs) / len(errs), 5))
    # relative error on the smallest-scale channel
    d0, s0 = quantize_symmetric(channels[0])
    rel_pc = sum(abs(a - b) for a, b in zip(channels[0], d0)) / sum(abs(a) for a in channels[0])
    seg = flat[:64]
    deq_t = deq[:64]
    rel_pt = sum(abs(a - b) for a, b in zip(seg, deq_t)) / sum(abs(a) for a in seg)
    print("relative error on the narrow channel: per-tensor",
          round(rel_pt, 3), " per-channel", round(rel_pc, 3))

    print("\n=== Distillation temperature ===")
    logits = [8.0, 4.0, 1.0]
    for t in (1.0, 4.0):
        print(f"T={t}:", [round(p, 4) for p in softmax(logits, t)])

    print("\n=== Class imbalance: positive predictive value ===")
    for prev, sens, spec in ((0.01, 0.90, 0.95), (0.002, 0.95, 0.99), (0.002, 0.95, 0.999)):
        tp = prev * sens
        fp = (1 - prev) * (1 - spec)
        print(f"prevalence {prev}, sensitivity {sens}, specificity {spec}: "
              f"PPV {tp / (tp + fp):.4f}, flags per 10,000 images {10000 * (tp + fp):.0f}")

    print("\n=== High-dimensional linear sensitivity (FGSM intuition) ===")
    d = 224 * 224 * 3
    w_mag = 0.01
    l1 = d * w_mag
    eps = 1 / 255
    print("input dimensions:", d, " |w_i| = 0.01 -> ||w||_1 =", l1)
    print("worst-case logit change for L-infinity budget 1/255:", round(eps * l1, 2))
    print("worst-case logit change for L-infinity budget 0.5/255:", round(0.5 * eps * l1, 2))

    print("\n=== Latency budget (illustrative) ===")
    macs = 4_089_184_256
    flops = 2 * macs
    for name, peak_tflops, util in (("edge accelerator", 4.0, 0.25),
                                     ("data-centre GPU", 100.0, 0.30),
                                     ("embedded CPU", 0.05, 0.50)):
        seconds = flops / (peak_tflops * 1e12 * util)
        print(f"{name:18s} peak {peak_tflops} TFLOPS, utilization {util}: "
              f"{seconds * 1000:.2f} ms per image at batch 1")

    print("\n=== Labeling cost: random versus uncertainty sampling (illustrative 1-D task) ===")
    random.seed(3)
    true_t = 0.37
    pool = [random.random() for _ in range(20000)]

    def est_error(lo, hi):
        return (hi - lo) / 2

    def random_labels(n):
        pts = random.sample(pool, n)
        lo = max([p for p in pts if p < true_t], default=0.0)
        hi = min([p for p in pts if p >= true_t], default=1.0)
        return est_error(lo, hi)

    def active_labels(n):
        lo, hi = 0.0, 1.0
        for _ in range(n):
            mid = (lo + hi) / 2
            q = min(pool, key=lambda p: abs(p - mid))
            if q < true_t:
                lo = max(lo, q)
            else:
                hi = min(hi, q)
        return est_error(lo, hi)

    for n in (10, 20, 40, 80):
        r = sum(random_labels(n) for _ in range(20)) / 20
        print(f"{n:3d} labels: random mean error {r:.4f}, active error {active_labels(n):.5f}")


if __name__ == "__main__":
    main()
