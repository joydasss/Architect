"""GRPO group-relative advantages and annotator agreement (Cohen's kappa).

Standard library only.
1. For several prompts, sample G=8 answers scored 0/1 by a verifier. Compute
   the GRPO advantage (reward - mean) / std, the Dr. GRPO style advantage
   (reward - mean), and flag groups with zero variance (no learning signal).
2. Compute raw agreement and Cohen's kappa for two annotators on a 2-way
   preference task, showing why raw agreement overstates reliability.
"""

import math


def advantages(rewards):
    g = len(rewards)
    mean = sum(rewards) / g
    var = sum((r - mean) ** 2 for r in rewards) / g
    std = math.sqrt(var)
    centered = [r - mean for r in rewards]
    normed = [c / (std + 1e-6) for c in centered] if std > 0 else [0.0] * g
    return mean, std, centered, normed


def cohen_kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    labels = set(a) | set(b)
    pe = sum((a.count(l) / n) * (b.count(l) / n) for l in labels)
    return po, pe, (po - pe) / (1 - pe)


def main():
    groups = {
        "hard (1 of 8 right)": [1, 0, 0, 0, 0, 0, 0, 0],
        "medium (4 of 8)": [1, 1, 1, 1, 0, 0, 0, 0],
        "easy (7 of 8)": [1, 1, 1, 1, 1, 1, 1, 0],
        "all wrong": [0] * 8,
        "all right": [1] * 8,
    }
    print("== GRPO advantages, G=8, binary reward ==")
    for name, rewards in groups.items():
        mean, std, centered, normed = advantages(rewards)
        print(f"{name:20} mean={mean:.3f} std={std:.3f} "
              f"adv(correct)={normed[rewards.index(1)] if 1 in rewards else 0.0:+.3f} "
              f"adv(wrong)={normed[rewards.index(0)] if 0 in rewards else 0.0:+.3f} "
              f"dr(correct)={centered[rewards.index(1)] if 1 in rewards else 0.0:+.3f}")

    print("\n== Annotator agreement ==")
    # 100 pairs, 80 where both pick A-position response, labels skewed.
    ann1 = ["A"] * 70 + ["B"] * 30
    ann2 = ["A"] * 62 + ["B"] * 8 + ["A"] * 12 + ["B"] * 18
    po, pe, kappa = cohen_kappa(ann1, ann2)
    print(f"raw agreement = {po:.3f}, chance agreement = {pe:.3f}, kappa = {kappa:.3f}")


if __name__ == "__main__":
    main()
