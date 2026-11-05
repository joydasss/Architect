"""Classifier-free guidance on a Gaussian toy, and latent-space compute arithmetic
(standard library only).

Part A: with p(x) = N(0, 2^2) and p(x | c) = N(1.5, 0.5^2), the guided score
  score_u + s * (score_c - score_u)
is the score of a density proportional to p(x) * p(c | x)^s, which for Gaussians is
again Gaussian. We print its mean and standard deviation for several guidance scales.

Part B: pixel-space versus latent-space cost for one denoiser call (illustrative
architecture-independent ratios based on position counts).

Run: python 03_guidance_and_cost.py
"""

import math


def guided_gaussian(s, mu_u=0.0, sd_u=2.0, mu_c=1.5, sd_c=0.5):
    # score_guided(x) = -(x-mu_u)/sd_u^2 + s * [ -(x-mu_c)/sd_c^2 + (x-mu_u)/sd_u^2 ]
    # = -prec * x + b  ->  Gaussian with precision prec and mean b / prec
    prec = s / sd_c ** 2 + (1 - s) / sd_u ** 2
    b = s * mu_c / sd_c ** 2 + (1 - s) * mu_u / sd_u ** 2
    return b / prec, math.sqrt(1 / prec)


def part_a():
    print("Part A: guided Gaussian (target class mean 1.5, class sd 0.5, prior sd 2.0)")
    print("scale s   guided mean   guided sd")
    for s in (0.0, 1.0, 3.0, 5.0, 7.5):
        m, sd = guided_gaussian(s)
        print(f"{s:7.1f}   {m:11.4f}   {sd:9.4f}")


def part_b():
    print("\nPart B: pixel versus latent cost, 512 x 512 RGB image")
    H = W = 512
    f, zc = 8, 4
    pix_values = H * W * 3
    lat_h, lat_w = H // f, W // f
    lat_values = lat_h * lat_w * zc
    print(f"pixel values        : {pix_values}")
    print(f"latent grid         : {lat_h} x {lat_w} x {zc} = {lat_values} values")
    print(f"data compression    : {pix_values / lat_values:.1f}x")
    pos_pix, pos_lat = H * W, lat_h * lat_w
    print(f"spatial positions   : {pos_pix} vs {pos_lat} -> conv cost ratio {pos_pix / pos_lat:.0f}x")
    print(f"attention pairs     : {pos_pix**2:.3e} vs {pos_lat**2:.3e} -> ratio {pos_pix**2 / pos_lat**2:.0f}x")
    patch = 2
    tokens = (lat_h // patch) * (lat_w // patch)
    print(f"DiT tokens (patch {patch}) : {tokens}; attention pairs {tokens**2:.3e}")
    H2 = 1024
    lat2 = (H2 // f) ** 2
    tok2 = (H2 // f // patch) ** 2
    print(f"1024x1024: latent positions {lat2}, DiT tokens {tok2}, pairs {tok2**2:.3e},"
          f" pairs ratio vs 512 = {tok2**2 / tokens**2:.0f}x")

    print("\nLatency arithmetic (illustrative per-call time 40 ms on one GPU, batch 1)")
    for steps, cfg in ((50, True), (30, True), (20, True), (8, True), (4, False), (1, False)):
        calls = steps * (2 if cfg else 1)
        t = calls * 0.040
        print(f"steps={steps:<3d} cfg={'yes' if cfg else 'no ':3s} denoiser calls={calls:<4d} "
              f"denoise time={t:6.2f} s")


if __name__ == "__main__":
    part_a()
    part_b()
