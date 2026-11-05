"""PCA two ways on a small dataset: covariance eigen-decomposition and SVD-style
power iteration on the centered data matrix. Standard library only.

Prints the covariance matrix, eigenpairs, explained variance, projection and
reconstruction error for k=1, and shows that the two routes agree.
Run: python 03_pca_by_hand.py
"""
import math

X = [(2.5, 2.4), (0.5, 0.7), (2.2, 2.9), (1.9, 2.2), (3.1, 3.0),
     (2.3, 2.7), (2.0, 1.6), (1.0, 1.1), (1.5, 1.6), (1.1, 0.9)]


def center(rows):
    n = len(rows)
    mu = [sum(r[j] for r in rows) / n for j in range(len(rows[0]))]
    return [[r[j] - mu[j] for j in range(len(r))] for r in rows], mu


def cov2(rows):
    n = len(rows)
    sxx = sum(r[0] * r[0] for r in rows) / (n - 1)
    sxy = sum(r[0] * r[1] for r in rows) / (n - 1)
    syy = sum(r[1] * r[1] for r in rows) / (n - 1)
    return sxx, sxy, syy


def eig2(sxx, sxy, syy):
    tr, det = sxx + syy, sxx * syy - sxy * sxy
    disc = math.sqrt(tr * tr / 4 - det)
    l1, l2 = tr / 2 + disc, tr / 2 - disc
    v1 = (sxy, l1 - sxx)
    n1 = math.hypot(*v1)
    v1 = (v1[0] / n1, v1[1] / n1)
    return (l1, l2), v1, (-v1[1], v1[0])


def power_iteration_svd(rows, iters=200):
    """Top right-singular vector of centered matrix A via power iteration on A^T A."""
    v = [1.0, 0.0]
    for _ in range(iters):
        av = [sum(r[j] * v[j] for j in range(2)) for r in rows]
        w = [sum(rows[i][j] * av[i] for i in range(len(rows))) for j in range(2)]
        nrm = math.hypot(*w)
        v = [wi / nrm for wi in w]
    av = [sum(r[j] * v[j] for j in range(2)) for r in rows]
    sigma = math.sqrt(sum(a * a for a in av))
    return sigma, v


def main():
    A, mu = center(X)
    n = len(A)
    print("mean = (%.2f, %.2f)" % tuple(mu))
    sxx, sxy, syy = cov2(A)
    print("covariance: [[%.4f, %.4f], [%.4f, %.4f]]" % (sxx, sxy, sxy, syy))
    (l1, l2), v1, v2 = eig2(sxx, sxy, syy)
    print("eigenvalues: %.4f, %.4f  (explained %.1f%%, %.1f%%)"
          % (l1, l2, 100 * l1 / (l1 + l2), 100 * l2 / (l1 + l2)))
    print("pc1 = (%.4f, %.4f), pc2 = (%.4f, %.4f)" % (v1 + v2))

    scores = [r[0] * v1[0] + r[1] * v1[1] for r in A]
    print("scores on pc1:", " ".join("%.3f" % s for s in scores))
    recon_err = 0.0
    for r, s in zip(A, scores):
        rec = (s * v1[0], s * v1[1])
        recon_err += (r[0] - rec[0]) ** 2 + (r[1] - rec[1]) ** 2
    print("k=1 total squared reconstruction error = %.4f (should equal (n-1)*lambda2 = %.4f)"
          % (recon_err, (n - 1) * l2))

    sigma, v = power_iteration_svd(A)
    print("\nSVD route: sigma1 = %.4f, sigma1^2/(n-1) = %.4f, v1 = (%.4f, %.4f)"
          % (sigma, sigma ** 2 / (n - 1), v[0], v[1]))
    print("sign-insensitive agreement |v1.pc1| = %.6f" % abs(v[0] * v1[0] + v[1] * v1[1]))

    print("\n== Why scaling matters: same data, second feature in 1000x units ==")
    B = [[r[0], r[1] * 1000] for r in A]
    bxx, bxy, byy = cov2(B)
    (m1, m2), w1, _ = eig2(bxx, bxy, byy)
    print("explained pc1 = %.2f%%, pc1 = (%.4f, %.4f)" % (100 * m1 / (m1 + m2), w1[0], w1[1]))


if __name__ == "__main__":
    main()
