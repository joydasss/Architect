"""Target-encoding leakage on a pure-noise categorical (standard library only).

A categorical feature with 400 levels has no relationship to the label
(base rate 0.2). Three encodings are compared by the area under the ROC
curve (AUC) of the encoded value used alone as a score:

* naive: mean label of each level over all training rows
* out-of-fold (5 folds): each row is encoded from the other four folds
* ordered: each row is encoded from earlier rows in a random permutation,
  with a prior of weight 1 (the idea behind CatBoost's ordered statistics)

An honest encoding should give AUC near 0.5 on both train and test.
"""

import random


def auc(scores, labels):
    pairs = sorted(zip(scores, labels))
    rank_sum, i, n = 0.0, 0, len(pairs)
    while i < n:
        j = i
        while j < n and pairs[j][0] == pairs[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2
        rank_sum += avg_rank * sum(1 for k in range(i, j) if pairs[k][1] == 1)
        i = j
    pos = sum(labels)
    neg = n - pos
    return (rank_sum - pos * (pos + 1) / 2) / (pos * neg)


def level_stats(cats, ys):
    s, c = {}, {}
    for a, b in zip(cats, ys):
        s[a] = s.get(a, 0) + b
        c[a] = c.get(a, 0) + 1
    return s, c


def enc_from(stats, cats, prior, w):
    s, c = stats
    return [(s.get(a, 0) + w * prior) / (c.get(a, 0) + w) for a in cats]


if __name__ == "__main__":
    rng = random.Random(0)
    LEVELS, N_TR, N_TE, P = 400, 1000, 4000, 0.2
    ctr = [rng.randrange(LEVELS) for _ in range(N_TR)]
    ytr = [1 if rng.random() < P else 0 for _ in range(N_TR)]
    cte = [rng.randrange(LEVELS) for _ in range(N_TE)]
    yte = [1 if rng.random() < P else 0 for _ in range(N_TE)]
    prior = sum(ytr) / N_TR
    print(f"rows per level in training: {N_TR / LEVELS:.2f} on average")

    full = level_stats(ctr, ytr)
    print(f"{'encoding':<22}{'train AUC':>10}{'test AUC':>10}")

    for name, w in (("naive (w=0)", 0.0), ("naive smoothed (w=10)", 10.0)):
        tr = enc_from(full, ctr, prior, w if w else 1e-9)
        te = enc_from(full, cte, prior, w if w else 1e-9)
        print(f"{name:<22}{auc(tr, ytr):>10.3f}{auc(te, yte):>10.3f}")

    # out-of-fold on training rows; test rows use the full-data statistics
    K = 5
    folds = [i % K for i in range(N_TR)]
    rng.shuffle(folds)
    oof = [0.0] * N_TR
    for k in range(K):
        tr_idx = [i for i in range(N_TR) if folds[i] != k]
        st = level_stats([ctr[i] for i in tr_idx], [ytr[i] for i in tr_idx])
        for i in range(N_TR):
            if folds[i] == k:
                oof[i] = (st[0].get(ctr[i], 0) + 10 * prior) / (
                    st[1].get(ctr[i], 0) + 10)
    te = enc_from(full, cte, prior, 10.0)
    print(f"{'out-of-fold (w=10)':<22}{auc(oof, ytr):>10.3f}"
          f"{auc(te, yte):>10.3f}")

    # ordered target statistics with prior weight 1
    perm = list(range(N_TR))
    rng.shuffle(perm)
    run_s, run_c = {}, {}
    ordered = [0.0] * N_TR
    for i in perm:
        a = ctr[i]
        ordered[i] = (run_s.get(a, 0) + prior) / (run_c.get(a, 0) + 1)
        run_s[a] = run_s.get(a, 0) + ytr[i]
        run_c[a] = run_c.get(a, 0) + 1
    te = enc_from(full, cte, prior, 1.0)
    print(f"{'ordered (prior w=1)':<22}{auc(ordered, ytr):>10.3f}"
          f"{auc(te, yte):>10.3f}")
