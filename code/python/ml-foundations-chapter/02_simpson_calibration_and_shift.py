"""Simpson's paradox, calibration (reliability table), and importance weights
under covariate shift, quoted in Chapter 16.01.

Standard library only (random with a fixed seed). Run:
python 02_simpson_calibration_and_shift.py
"""
import math
import random


def simpson():
    # (successes, trials) per arm and segment. Illustrative counts.
    data = {
        "A": {"mild": (81, 87), "severe": (192, 263)},
        "B": {"mild": (234, 270), "severe": (55, 80)},
    }
    for arm, segs in data.items():
        s = sum(v[0] for v in segs.values())
        t = sum(v[1] for v in segs.values())
        parts = "  ".join(f"{k}: {v[0]}/{v[1]}={v[0] / v[1]:.3f}" for k, v in segs.items())
        print(f"arm {arm}: {parts}  overall: {s}/{t}={s / t:.3f}")
    # Standardize to a common 50/50 mix.
    for arm, segs in data.items():
        std = 0.5 * segs["mild"][0] / segs["mild"][1] + 0.5 * segs["severe"][0] / segs["severe"][1]
        print(f"arm {arm} standardized to 50/50 mix: {std:.3f}")


def calibration():
    rng = random.Random(7)
    n = 20000
    true_p, scores, labels = [], [], []
    for _ in range(n):
        p = rng.random()
        y = 1 if rng.random() < p else 0
        # Overconfident model: pushes probabilities toward 0 and 1.
        z = math.log(p / (1 - p)) * 2.0
        s = 1 / (1 + math.exp(-z))
        scores.append(s)
        labels.append(y)
    print("bin          n   mean_score  observed_rate")
    for lo in [0.0, 0.2, 0.4, 0.6, 0.8]:
        hi = lo + 0.2
        idx = [i for i, s in enumerate(scores) if lo <= s < hi or (hi >= 1.0 and s == 1.0)]
        ms = sum(scores[i] for i in idx) / len(idx)
        obs = sum(labels[i] for i in idx) / len(idx)
        print(f"[{lo:.1f},{hi:.1f})  {len(idx):6d}   {ms:.3f}       {obs:.3f}")
    ece = 0.0
    for lo in [i / 10 for i in range(10)]:
        hi = lo + 0.1
        idx = [i for i, s in enumerate(scores) if lo <= s < hi]
        if idx:
            ms = sum(scores[i] for i in idx) / len(idx)
            obs = sum(labels[i] for i in idx) / len(idx)
            ece += len(idx) / n * abs(ms - obs)
    print(f"expected calibration error (10 bins) = {ece:.3f}")


def covariate_shift():
    rng = random.Random(3)
    # Fit a straight line to y = x^2 + noise with x ~ N(0,1), test on x ~ N(1.5,1).
    def gen(mu, m):
        xs = [rng.gauss(mu, 1) for _ in range(m)]
        return xs, [x * x + rng.gauss(0, 0.3) for x in xs]

    xs, ys = gen(0, 5000)
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    a = my - b * mx
    tx, ty = gen(1.5, 5000)
    train_mse = sum((a + b * x - y) ** 2 for x, y in zip(xs, ys)) / len(xs)
    test_mse = sum((a + b * x - y) ** 2 for x, y in zip(tx, ty)) / len(tx)
    # Importance weights w = Q(x)/P(x) for two Gaussians with equal variance.
    w = [math.exp(1.5 * x - 1.5 ** 2 / 2) for x in xs]
    iw_mse = sum(wi * (a + b * x - y) ** 2 for wi, x, y in zip(w, xs, ys)) / sum(w)
    ess = sum(w) ** 2 / sum(wi * wi for wi in w)
    print(f"line: y = {a:.3f} + {b:.3f} x")
    print(f"MSE on training distribution = {train_mse:.3f}")
    print(f"MSE on shifted distribution  = {test_mse:.3f}")
    print(f"importance-weighted estimate = {iw_mse:.3f}  effective sample size = {ess:.0f} of {len(xs)}")


if __name__ == "__main__":
    print("== Simpson's paradox ==")
    simpson()
    print("\n== Calibration of an overconfident model ==")
    calibration()
    print("\n== Covariate shift and importance weights ==")
    covariate_shift()
