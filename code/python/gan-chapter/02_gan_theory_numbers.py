"""Worked numbers for the GAN chapter (CH11). Standard library only.

Checks, with plain arithmetic:
  A. optimal discriminator and the identity V(D*, G) = -log 4 + 2 JSD
  B. JS divergence is flat for disjoint supports, Wasserstein-1 is not
  C. gradient of the saturating and non-saturating generator losses
  D. gradient penalty for a linear critic
  E. spectral norm by power iteration
  F. EMA half-life
  G. closed-form Gaussian KL used in the VAE evidence lower bound
  H. FID between two 2-D Gaussians (closed form for 2x2 matrices)
  I. Inception Score on a four-sample toy example
  J. one-dimensional VAE: ELBO, exact log-likelihood, and the KL gap
  K. EMA decay from a half-life stated in images shown
  L. birthday-paradox estimate of support size
"""
import math


def kl(p, q):
    return sum(pi * math.log(pi / qi) for pi, qi in zip(p, q) if pi > 0)


def jsd(p, q):
    m = [(a + b) / 2 for a, b in zip(p, q)]
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


print("A. Optimal discriminator")
p_data = [0.4, 0.3, 0.2, 0.1]
p_gen = [0.1, 0.2, 0.3, 0.4]
d_star = [a / (a + b) for a, b in zip(p_data, p_gen)]
print("   D* per point        :", [round(v, 3) for v in d_star])
v = sum(a * math.log(d) + b * math.log(1 - d)
        for a, b, d in zip(p_data, p_gen, d_star))
print("   V(D*, G)            : %.4f" % v)
print("   JSD(p_data || p_gen): %.4f" % jsd(p_data, p_gen))
print("   -log 4 + 2 JSD     : %.4f" % (-math.log(4) + 2 * jsd(p_data, p_gen)))
print("   -log 4             : %.4f" % (-math.log(4)))

print("B. Disjoint supports: JSD vs Wasserstein-1 (point mass at 0 vs point mass at theta)")
for theta in (0.1, 1.0, 5.0):
    print("   theta=%-4s JSD=%.4f (log 2 = %.4f)  W1=%.1f" % (theta, math.log(2), math.log(2), theta))

print("C. Generator gradient w.r.t. the discriminator logit a, D = sigmoid(a)")
print("   saturating   loss log(1-D): d/da = -D")
print("   non-saturating loss -log D : d/da = -(1-D)")
for d in (0.001, 0.01, 0.1, 0.5, 0.9):
    print("   D=%-5s |saturating|=%.3f  |non-saturating|=%.3f  loss values: %.4f vs %.4f"
          % (d, d, 1 - d, math.log(1 - d), -math.log(d)))

print("D. Gradient penalty for linear critic f(x)=w.x, lambda=10")
w = (3.0, 4.0)
g = math.hypot(*w)
print("   ||grad f|| = %.1f, penalty = 10*(%.1f-1)^2 = %.1f" % (g, g, 10 * (g - 1) ** 2))
w = (0.6, 0.8)
g = math.hypot(*w)
print("   w=(0.6,0.8): ||grad f|| = %.1f, penalty = %.1f" % (g, 10 * (g - 1) ** 2))

print("E. Spectral norm by power iteration, W = [[3,0],[4,5]]")
W = [[3.0, 0.0], [4.0, 5.0]]
u = [1.0, 1.0]
for _ in range(50):
    # v = W^T u / ||.||, u = W v / ||.||
    v_ = [sum(W[i][j] * u[i] for i in range(2)) for j in range(2)]
    n = math.hypot(*v_)
    v_ = [x / n for x in v_]
    u = [sum(W[i][j] * v_[j] for j in range(2)) for i in range(2)]
    sigma = math.hypot(*u)
    u = [x / sigma for x in u]
print("   sigma_max ~ %.4f, exact sqrt(45) = %.4f" % (sigma, math.sqrt(45)))
print("   normalised matrix W/sigma has spectral norm 1")

print("F. EMA of generator weights")
for decay in (0.99, 0.999, 0.9999):
    print("   decay=%-6s half-life = %.1f steps" % (decay, math.log(0.5) / math.log(decay)))

print("G. Gaussian KL( N(mu, diag(s^2)) || N(0, I) ) = 0.5 * sum(mu^2 + s^2 - 1 - log s^2)")
mu = [0.5, -1.0]
s = [0.8, 1.2]
terms = [0.5 * (m * m + sd * sd - 1 - math.log(sd * sd)) for m, sd in zip(mu, s)]
print("   per-dimension: %s  total = %.4f nats" % ([round(t, 4) for t in terms], sum(terms)))


def sqrtm_trace_2x2(m):
    tr = m[0][0] + m[1][1]
    det = m[0][0] * m[1][1] - m[0][1] * m[1][0]
    return math.sqrt(tr + 2 * math.sqrt(det))


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]


print("H. FID between two 2-D Gaussians")
m1, c1 = (0.0, 0.0), [[1.0, 0.0], [0.0, 1.0]]
m2, c2 = (1.0, 0.0), [[2.0, 0.0], [0.0, 0.5]]
mean_term = sum((a - b) ** 2 for a, b in zip(m1, m2))
tr_sum = c1[0][0] + c1[1][1] + c2[0][0] + c2[1][1]
cross = 2 * sqrtm_trace_2x2(matmul(c1, c2))
print("   ||mu1-mu2||^2 = %.4f, Tr(C1)+Tr(C2) = %.4f, 2 Tr sqrt(C1 C2) = %.4f"
      % (mean_term, tr_sum, cross))
print("   FID = %.4f" % (mean_term + tr_sum - cross))

print("I. Inception Score, 3 classes, 4 samples")
rows = [[0.9, 0.05, 0.05], [0.05, 0.9, 0.05], [0.05, 0.05, 0.9], [0.9, 0.05, 0.05]]
marg = [sum(r[k] for r in rows) / len(rows) for k in range(3)]
print("   marginal p(y) =", [round(x, 4) for x in marg])
mean_kl = sum(kl(r, marg) for r in rows) / len(rows)
print("   mean KL = %.4f, IS = exp(mean KL) = %.4f" % (mean_kl, math.exp(mean_kl)))
collapsed = [[0.9, 0.05, 0.05]] * 4
marg = [0.9, 0.05, 0.05]
print("   collapsed to one class: IS = %.4f" % math.exp(sum(kl(r, marg) for r in collapsed) / 4))

print("J. One-dimensional VAE check: prior N(0,1), decoder x|z ~ N(z,1), observation x=1")
x_obs, q_mu, q_var = 1.0, 0.5, 0.64
recon = -0.5 * math.log(2 * math.pi) - 0.5 * ((x_obs - q_mu) ** 2 + q_var)
kl_term = 0.5 * (q_mu ** 2 + q_var - 1 - math.log(q_var))
elbo = recon - kl_term
log_px = -0.5 * math.log(2 * math.pi * 2) - x_obs ** 2 / (2 * 2)  # marginal x ~ N(0, 2)
post_mu, post_var = x_obs / 2, 0.5                                   # exact posterior N(x/2, 1/2)
gap = 0.5 * (q_var / post_var + (q_mu - post_mu) ** 2 / post_var - 1 + math.log(post_var / q_var))
print("   E_q[log p(x|z)] = %.4f, KL(q||prior) = %.4f, ELBO = %.4f" % (recon, kl_term, elbo))
print("   exact log p(x)  = %.4f, gap = %.4f, KL(q||true posterior) = %.4f" % (log_px, log_px - elbo, gap))

print("K. EMA decay for a half-life stated in images shown")
half_life_images, batch = 10000, 32
steps_half = half_life_images / batch
print("   half-life %d images at batch %d = %.1f steps, decay = %.5f"
      % (half_life_images, batch, steps_half, 0.5 ** (1 / steps_half)))

print("L. Birthday-paradox support estimate: s=400 samples, one duplicate pair")
s = 400
print("   N ~ s(s-1)/2 = %d" % (s * (s - 1) // 2))
