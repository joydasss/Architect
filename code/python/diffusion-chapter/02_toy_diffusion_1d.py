"""A tiny 1-D diffusion model with an exact (analytic) denoiser (standard library only).

Data distribution: an equal mixture of N(-2, 0.3^2) and N(+2, 0.3^2). For a Gaussian
mixture the noisy marginal p_t(x) is again a mixture, so the exact score and therefore
the exact noise prediction eps_hat(x, t) are available in closed form. This isolates the
sampler from network error: any difference between samplers below comes from the
discretisation, not from a learned model.

Samplers compared: DDPM ancestral (1000 steps), DDIM (eta=0) with few steps, and Euler
and Heun (second-order) integration of the probability-flow ODE.

Run: python 02_toy_diffusion_1d.py
"""

import math
import random

from importlib import util
import os

# Reuse the linear schedule from the sibling script.
_spec = util.spec_from_file_location(
    "sched", os.path.join(os.path.dirname(os.path.abspath(__file__)), "01_noise_schedules.py"))
_m = util.module_from_spec(_spec)
_spec.loader.exec_module(_m)

T = 1000
AB = [1.0] + _m.linear_alpha_bar(T)  # AB[t], t = 0..T ; AB[0] = 1
MEANS, STD = (-2.0, 2.0), 0.3


def eps_hat(x, t):
    """Exact E[eps | x_t = x] for the mixture data distribution."""
    ab = AB[t]
    sa, s1 = math.sqrt(ab), math.sqrt(1 - ab)
    var = ab * STD ** 2 + (1 - ab)
    logw = [-0.5 * (x - sa * m) ** 2 / var for m in MEANS]
    mx = max(logw)
    w = [math.exp(v - mx) for v in logw]
    z = sum(w)
    score = sum(wi / z * (-(x - sa * m) / var) for wi, m in zip(w, MEANS))
    return -s1 * score


def sample_data(n, rng):
    return [rng.choice(MEANS) + STD * rng.gauss(0, 1) for _ in range(n)]


def ddpm(n, rng):
    out = []
    for _ in range(n):
        x = rng.gauss(0, 1)
        for t in range(T, 0, -1):
            ab, abp = AB[t], AB[t - 1]
            beta = 1 - ab / abp
            alpha = 1 - beta
            e = eps_hat(x, t)
            mean = (x - beta / math.sqrt(1 - ab) * e) / math.sqrt(alpha)
            sigma = math.sqrt(beta * (1 - abp) / (1 - ab))  # posterior variance
            x = mean + (sigma * rng.gauss(0, 1) if t > 1 else 0.0)
        out.append(x)
    return out


def timesteps(steps):
    return [round(T * (1 - i / steps)) for i in range(steps + 1)]  # T ... 0


def ddim(n, steps, rng):
    ts = timesteps(steps)
    out = []
    for _ in range(n):
        x = rng.gauss(0, 1)
        for t, tp in zip(ts[:-1], ts[1:]):
            e = eps_hat(x, t)
            x0 = (x - math.sqrt(1 - AB[t]) * e) / math.sqrt(AB[t])
            x = math.sqrt(AB[tp]) * x0 + math.sqrt(1 - AB[tp]) * e
        out.append(x)
    return out


def ode_solver(n, steps, order, rng):
    """Integrate the probability-flow ODE in y = x / sqrt(ab) vs. s = sqrt((1-ab)/ab).
    dy/ds = eps_hat. Euler (order 1) or Heun (order 2, 2 evaluations per step except last)."""
    ts = timesteps(steps)

    def s_of(t):
        return math.sqrt((1 - AB[t]) / AB[t])

    out = []
    for _ in range(n):
        x = rng.gauss(0, 1)
        y = x / math.sqrt(AB[ts[0]])
        for t, tp in zip(ts[:-1], ts[1:]):
            ds = s_of(tp) - s_of(t)
            k1 = eps_hat(y * math.sqrt(AB[t]), t)
            y_next = y + ds * k1
            if order == 2 and tp > 0:
                k2 = eps_hat(y_next * math.sqrt(AB[tp]), tp)
                y_next = y + ds * 0.5 * (k1 + k2)
            y = y_next
        out.append(y * math.sqrt(AB[0]))
    return out


def w1(a, b):
    """1-D Wasserstein-1 distance between two equal-size samples (mean abs quantile gap)."""
    return sum(abs(p - q) for p, q in zip(sorted(a), sorted(b))) / len(a)


def summary(xs):
    left = [v for v in xs if v < 0]
    right = [v for v in xs if v >= 0]

    def mean(v):
        return sum(v) / len(v)

    def sd(v):
        m = mean(v)
        return math.sqrt(sum((q - m) ** 2 for q in v) / len(v))

    return len(right) / len(xs), mean(left), sd(left), mean(right), sd(right)


def main():
    n = 1500
    ref = sample_data(n, random.Random(123))
    ref2 = sample_data(n, random.Random(456))
    print("Target: 0.5*N(-2,0.3^2) + 0.5*N(2,0.3^2); n =", n)
    print("%-26s %5s %6s %7s %6s %7s %6s %7s" %
          ("sampler", "NFE", "frac+", "mean-", "sd-", "mean+", "sd+", "W1"))
    rows = [("data (fresh sample)", 0, ref2)]
    rows.append(("DDPM ancestral", T, ddpm(n, random.Random(1))))
    for s in (50, 10, 4):
        rows.append((f"DDIM eta=0, {s} steps", s, ddim(n, s, random.Random(1))))
    for s in (10, 4):
        rows.append((f"Euler ODE, {s} steps", s, ode_solver(n, s, 1, random.Random(1))))
        rows.append((f"Heun ODE, {s} steps", 2 * s - 1, ode_solver(n, s, 2, random.Random(1))))
    for name, nfe, xs in rows:
        f, ml, sl, mr, sr = summary(xs)
        print("%-26s %5d %6.3f %7.3f %6.3f %7.3f %6.3f %7.4f" %
              (name, nfe, f, ml, sl, mr, sr, w1(xs, ref)))

    # Determinism: same noise, same DDIM trajectory.
    a = ddim(3, 10, random.Random(7))
    b = ddim(3, 10, random.Random(7))
    print("\nDDIM same seed twice identical:", a == b)
    c = ddpm(1, random.Random(7))[0]
    d = ddpm(1, random.Random(8))[0]
    print("DDPM sample, seed 7 vs 8 (different noise):", round(c, 3), round(d, 3))


if __name__ == "__main__":
    main()
