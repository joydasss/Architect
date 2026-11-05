"""Reviewer quality: Cohen's kappa, canary (seeded error) catch rate, audit escape rate.

Standard library only. Counts are illustrative.
"""
import math


def cohen_kappa(table):
    """table[i][j] = items rater A labeled i and rater B labeled j."""
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


def main() -> None:
    # Two reviewers label 200 cases as approve / reject.
    #                B approve  B reject
    table = [[150, 10],    # A approve
             [15, 25]]     # A reject
    po, pe, k = cohen_kappa(table)
    print(f"Observed agreement {po:.3f}, chance agreement {pe:.3f}, kappa {k:.3f}")

    # A reviewer who approves almost everything: high raw agreement, low kappa.
    table2 = [[190, 4], [4, 2]]
    po2, pe2, k2 = cohen_kappa(table2)
    print(f"Rubber-stamp pair: agreement {po2:.3f}, chance {pe2:.3f}, kappa {k2:.3f}")

    # Canary cases: seeded known errors mixed into the queue.
    seeded, caught = 60, 41
    lo, hi = wilson(caught, seeded)
    print(f"\nCanary catch rate {caught}/{seeded} = {caught / seeded:.1%} "
          f"(95% interval {lo:.1%} to {hi:.1%})")

    # Sampled audit of automatically approved items.
    audited, escapes = 400, 6
    lo, hi = wilson(escapes, audited)
    print(f"Audit escape rate {escapes}/{audited} = {escapes / audited:.2%} "
          f"(95% interval {lo:.2%} to {hi:.2%})")
    # Sample size needed to see at least one escape with 95% probability.
    for rate in (0.02, 0.005, 0.001):
        n = math.ceil(math.log(0.05) / math.log(1 - rate))
        print(f"  true escape rate {rate:.1%}: need {n} audited items "
              f"to see one escape with 95% probability")

    # Override rate as a decay signal under rising workload.
    print("\nOverride rate versus load (illustrative reviewer data):")
    print(f"{'load':>6} {'sec/review':>10} {'override %':>10} {'canary catch %':>14}")
    for load, sec, ov, cc in [(0.6, 95, 14.0, 78), (0.8, 70, 9.5, 71),
                              (0.95, 41, 4.2, 52), (1.05, 22, 1.1, 31)]:
        print(f"{load:>6.2f} {sec:>10} {ov:>10.1f} {cc:>14}")


if __name__ == "__main__":
    main()
