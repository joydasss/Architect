"""Noise schedules for a variance-preserving diffusion process (standard library only).

Computes alpha_bar_t and the signal-to-noise ratio (SNR) for the linear schedule of
Ho et al. (2020) and the cosine schedule of Nichol and Dhariwal (2021), then shows
the closed-form forward sample x_t = sqrt(ab) x0 + sqrt(1-ab) eps on a 1-D value.

Run: python 01_noise_schedules.py
"""

import math
import random

T = 1000


def linear_alpha_bar(T=T, b0=1e-4, b1=0.02):
    ab, out = 1.0, []
    for i in range(T):
        beta = b0 + (b1 - b0) * i / (T - 1)
        ab *= 1.0 - beta
        out.append(ab)
    return out


def cosine_alpha_bar(T=T, s=0.008):
    def f(t):
        return math.cos((t / T + s) / (1 + s) * math.pi / 2) ** 2

    f0 = f(0)
    return [min(f(t) / f0, 0.999999) for t in range(1, T + 1)]


def snr_db(ab):
    return 10 * math.log10(ab / (1 - ab))


def main():
    lin, cos = linear_alpha_bar(), cosine_alpha_bar()
    print("t     lin_ab    lin_SNR   lin_dB |  cos_ab    cos_SNR   cos_dB")
    for t in (1, 100, 250, 500, 750, 900, 1000):
        a, c = lin[t - 1], cos[t - 1]
        print(f"{t:<5d} {a:8.5f} {a/(1-a):10.4g} {snr_db(a):7.2f} | "
              f"{c:8.5f} {c/(1-c):10.4g} {snr_db(c):7.2f}")

    def first_below(ab, thr):
        return next(t + 1 for t, v in enumerate(ab) if v < thr)

    print("\nFirst step where alpha_bar < 0.5 :  linear", first_below(lin, 0.5),
          " cosine", first_below(cos, 0.5))
    print("First step where alpha_bar < 0.01:  linear", first_below(lin, 0.01),
          " cosine", first_below(cos, 0.01))
    print("Terminal alpha_bar (t=1000):         linear %.2e  cosine %.2e" % (lin[-1], cos[-1]))

    rng = random.Random(0)
    x0 = 1.5
    print("\nClosed-form forward samples of x0 = 1.5 (linear schedule, same eps):")
    eps = rng.gauss(0, 1)
    for t in (10, 250, 500, 1000):
        ab = lin[t - 1]
        xt = math.sqrt(ab) * x0 + math.sqrt(1 - ab) * eps
        print(f"t={t:<5d} sqrt(ab)={math.sqrt(ab):.4f} sqrt(1-ab)={math.sqrt(1-ab):.4f} x_t={xt:+.4f}")


if __name__ == "__main__":
    main()
