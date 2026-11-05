"""Sample-size and power arithmetic for evaluation release gates (standard library).

Covers: confidence interval half-width, one-sided gate with zero failures
(rule of three), paired and unpaired two-proportion sample sizes, and the
number of annotated items needed to estimate a rate with a given margin.
"""
import math
from statistics import NormalDist

nd = NormalDist()


def n_for_margin(p, margin, conf=0.95):
    z = nd.inv_cdf(1 - (1 - conf) / 2)
    return math.ceil(z * z * p * (1 - p) / margin ** 2)


def n_two_prop(p1, p2, alpha=0.05, power=0.80):
    za = nd.inv_cdf(1 - alpha / 2)
    zb = nd.inv_cdf(power)
    pbar = (p1 + p2) / 2
    num = (za * math.sqrt(2 * pbar * (1 - pbar)) +
           zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return math.ceil(num / (p1 - p2) ** 2)


def n_zero_failures(max_rate, conf=0.95):
    return math.ceil(math.log(1 - conf) / math.log(1 - max_rate))


def n_paired(p_disc_a, p_disc_b, alpha=0.05, power=0.80):
    """Discordant-pair design (McNemar approximation).

    p_disc_a: probability only the candidate passes, p_disc_b: only baseline.
    """
    za = nd.inv_cdf(1 - alpha / 2)
    zb = nd.inv_cdf(power)
    psi = p_disc_a + p_disc_b
    delta = p_disc_a - p_disc_b
    return math.ceil(((za * math.sqrt(psi) + zb * math.sqrt(psi - delta ** 2)) / delta) ** 2)


print("CI half-width at n=200, p=0.91:", round(1.96 * math.sqrt(0.91 * 0.09 / 200), 4))
print("n for p=0.90 margin 0.02:", n_for_margin(0.90, 0.02))
print("n for p=0.50 margin 0.05:", n_for_margin(0.50, 0.05))
print("unpaired n per arm, 90% vs 92%:", n_two_prop(0.90, 0.92))
print("unpaired n per arm, 90% vs 95%:", n_two_prop(0.90, 0.95))
print("zero failures needed for rate <= 1%:", n_zero_failures(0.01))
print("zero failures needed for rate <= 0.1%:", n_zero_failures(0.001))
print("paired n, discordant 0.06 vs 0.02:", n_paired(0.06, 0.02))
