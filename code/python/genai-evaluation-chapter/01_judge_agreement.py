"""Judge-versus-human agreement statistics (standard library only).

Computes raw agreement, Cohen's kappa, a Wilson interval, precision/recall of
the judge against human labels, and the pairwise position-bias swap test.
"""
import math


def cohen_kappa(table):
    """table[i][j] = count where rater A said i and rater B said j."""
    n = sum(sum(r) for r in table)
    po = sum(table[i][i] for i in range(len(table))) / n
    rows = [sum(r) / n for r in table]
    cols = [sum(table[i][j] for i in range(len(table))) / n for j in range(len(table))]
    pe = sum(r * c for r, c in zip(rows, cols))
    return po, pe, (po - pe) / (1 - pe)


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return centre - half, centre + half


# rows = human (pass, fail), cols = judge (pass, fail)
table = [[120, 10], [20, 50]]
po, pe, kappa = cohen_kappa(table)
print(f"observed agreement po = {po:.3f}")
print(f"chance agreement   pe = {pe:.3f}")
print(f"Cohen kappa           = {kappa:.3f}")

lo, hi = wilson(170, 200)
print(f"agreement 95% Wilson interval = [{lo:.3f}, {hi:.3f}]")

tp, fn = table[1][1], table[1][0]  # treat 'fail' as the positive (bad) class
fp = table[0][1]
tn = table[0][0]
print(f"judge recall on bad answers   = {tp}/{tp+fn} = {tp/(tp+fn):.3f}")
print(f"judge precision on bad flags  = {tp}/{tp+fp} = {tp/(tp+fp):.3f}")

# Position-bias swap test: 100 pairs judged in order (A,B) and again as (B,A).
# Outcome codes: the judge's pick expressed as which *answer* it chose.
consistent_a, consistent_b, flip_first, flip_second = 41, 27, 24, 8
total = consistent_a + consistent_b + flip_first + flip_second
print(f"swap-consistent pairs = {consistent_a + consistent_b}/{total}")
print(f"first-position wins on inconsistent pairs = {flip_first}/{flip_first + flip_second}")
print(f"first-position preference among flips = {flip_first/(flip_first+flip_second):.3f}")

# Weighted corrected win rate: count only swap-consistent pairs.
wins_a = consistent_a
wins_b = consistent_b
print(f"corrected win rate of A = {wins_a/(wins_a+wins_b):.3f} on {wins_a+wins_b} pairs")
