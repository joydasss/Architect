"""Loss weights, parameterizations, rectified flow, and metric bias (standard library only).

Part A: DDPM posterior coefficients and the variational-bound weight of each step's
        noise-prediction error, versus the "simple" loss that gives every step weight 1.
Part B: eps, x0 and v parameterizations: conversions and how a fixed eps error maps to
        an x0 error at different noise levels.
Part C: rectified flow (straight-line path x_t = (1-t) x0 + t eps) on the 1-D mixture
        of 02_toy_diffusion_1d.py, with the exact velocity field and Euler sampling.
Part D: a one-dimensional Frechet distance (the FID formula in one dimension) computed
        from finite samples of the SAME distribution, to show metric bias with sample size.

Run: python 05_loss_parameterizations_and_flow.py
"""

import math
import os
import random
from importlib import util

_here = os.path.dirname(os.path.abspath(__file__))
_spec = util.spec_from_file_location("sched", os.path.join(_here, "01_noise_schedules.py"))
_m = util.module_from_spec(_spec)
_spec.loader.exec_module(_m)

T = 1000
AB = [1.0] + _m.linear_alpha_bar(T)  # AB[t], t = 0..T


def part_a():
    print("Part A: variational-bound weight versus the simple loss (linear schedule, T=1000)")
    print("%5s %9s %9s %10s %12s" % ("t", "beta_t", "ab_t", "sigma2_t", "lambda_t"))
    lam = {}
    for t in (1, 10, 100, 250, 500, 750, 1000):
        ab, abp = AB[t], AB[t - 1]
        beta = 1 - ab / abp
        alpha = 1 - beta
        sigma2 = beta * (1 - abp) / (1 - ab) if t > 1 else beta  # posterior variance
        lam[t] = beta ** 2 / (2 * sigma2 * alpha * (1 - ab))
        print("%5d %9.5f %9.5f %10.6f %12.5f" % (t, beta, ab, sigma2, lam[t]))
    print("lambda_1 / lambda_1000 = %.1f ; lambda_1 / lambda_500 = %.1f" % (lam[1] / lam[1000], lam[1] / lam[500]))
    t = 500
    ab, abp = AB[t], AB[t - 1]
    beta = 1 - ab / abp
    c0 = math.sqrt(abp) * beta / (1 - ab)
    ct = math.sqrt(1 - beta) * (1 - abp) / (1 - ab)
    x0, eps = 1.5, 0.7
    xt = math.sqrt(ab) * x0 + math.sqrt(1 - ab) * eps
    mu_x0 = c0 * x0 + ct * xt
    mu_eps = (xt - beta / math.sqrt(1 - ab) * eps) / math.sqrt(1 - beta)
    print("t=500 posterior mean coefficients: on x0 = %.5f, on x_t = %.5f" % (c0, ct))
    print("posterior mean via (x0, x_t) = %.6f ; via (eps) = %.6f ; difference %.1e" %
          (mu_x0, mu_eps, abs(mu_x0 - mu_eps)))


def part_b():
    print("\nPart B: parameterizations. Given x_t and eps, recover x0 and v = sqrt(ab) eps - sqrt(1-ab) x0")
    x0, eps = 1.5, 0.7
    print("%5s %8s %8s %8s %8s %14s" % ("t", "x_t", "x0_rec", "v", "SNR", "x0 err for eps err 0.10"))
    for t in (10, 250, 500, 900, 1000):
        ab = AB[t]
        sa, s1 = math.sqrt(ab), math.sqrt(1 - ab)
        xt = sa * x0 + s1 * eps
        x0_rec = (xt - s1 * eps) / sa
        v = sa * eps - s1 * x0
        snr = ab / (1 - ab)
        x0_err = s1 / sa * 0.10
        print("%5d %8.4f %8.4f %8.4f %8.4g %14.4f" % (t, xt, x0_rec, v, snr, x0_err))
    ab = AB[500]
    sa, s1 = math.sqrt(ab), math.sqrt(1 - ab)
    xt = sa * x0 + s1 * eps
    v = sa * eps - s1 * x0
    print("check x0 = sqrt(ab) x_t - sqrt(1-ab) v : %.6f (true 1.5)" % (sa * xt - s1 * v))
    print("check eps = sqrt(1-ab) x_t + sqrt(ab) v: %.6f (true 0.7)" % (s1 * xt + sa * v))


MEANS, STD = (-2.0, 2.0), 0.3


def velocity(x, t):
    """Exact E[eps - x0 | x_t = x] for x_t = (1-t) x0 + t eps, x0 from the mixture."""
    a, s = 1 - t, t
    var = a * a * STD ** 2 + s * s
    logw = [-0.5 * (x - a * m) ** 2 / var for m in MEANS]
    mx = max(logw)
    w = [math.exp(v - mx) for v in logw]
    z = sum(w)
    ex0 = 0.0
    for wi, m in zip(w, MEANS):
        ex0 += wi / z * (m + a * STD ** 2 / var * (x - a * m))
    eeps = (x - a * ex0) / s
    return eeps - ex0


def flow_euler(n, steps, rng):
    out = []
    ts = [1.0 - i / steps for i in range(steps + 1)]
    ts[-1] = 0.0
    for _ in range(n):
        x = rng.gauss(0, 1)
        for t, tn in zip(ts[:-1], ts[1:]):
            x = x + (tn - t) * velocity(x, max(t, 1e-3))
        out.append(x)
    return out


def w1(a, b):
    return sum(abs(p - q) for p, q in zip(sorted(a), sorted(b))) / len(a)


def part_c():
    print("\nPart C: rectified flow on the 1-D mixture, exact velocity, Euler steps")
    n = 1500
    rng = random.Random(123)
    ref = [rng.choice(MEANS) + STD * rng.gauss(0, 1) for _ in range(n)]
    print("%-22s %5s %7s %7s %8s" % ("sampler", "NFE", "frac+", "sd", "W1"))
    for steps in (1, 2, 4, 8, 32):
        xs = flow_euler(n, steps, random.Random(1))
        pos = sum(1 for v in xs if v >= 0) / n
        mean = sum(xs) / n
        sd = math.sqrt(sum((v - mean) ** 2 for v in xs) / n)
        print("%-22s %5d %7.3f %7.3f %8.4f" % ("flow Euler, %d steps" % steps, steps, pos, sd, w1(xs, ref)))
    print("(data sd = %.3f)" % math.sqrt(sum((v - sum(ref) / n) ** 2 for v in ref) / n))


def frechet_1d(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    sa = math.sqrt(sum((v - ma) ** 2 for v in a) / (len(a) - 1))
    sb = math.sqrt(sum((v - mb) ** 2 for v in b) / (len(b) - 1))
    return (ma - mb) ** 2 + (sa - sb) ** 2


def part_d():
    print("\nPart D: 1-D Frechet distance between two samples of the SAME N(0,1), 200 repeats")
    print("%8s %14s %14s" % ("n each", "mean distance", "max distance"))
    for n in (10, 50, 500, 5000):
        rng = random.Random(n)
        vals = []
        for _ in range(200):
            a = [rng.gauss(0, 1) for _ in range(n)]
            b = [rng.gauss(0, 1) for _ in range(n)]
            vals.append(frechet_1d(a, b))
        print("%8d %14.5f %14.5f" % (n, sum(vals) / len(vals), max(vals)))


if __name__ == "__main__":
    part_a()
    part_b()
    part_c()
    part_d()
