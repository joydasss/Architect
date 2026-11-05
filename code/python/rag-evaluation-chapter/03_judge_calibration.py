"""LLM-as-judge calibration: Cohen's kappa, bias checks, and judge cost.

Standard library only. Run: python 03_judge_calibration.py
"""

import math
import random


def cohens_kappa(a, b, labels):
    n = len(a)
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pe = 0.0
    for lab in labels:
        pa = sum(1 for x in a if x == lab) / n
        pb = sum(1 for y in b if y == lab) / n
        pe += pa * pb
    return po, pe, (po - pe) / (1 - pe)


def confusion_to_labels(table):
    """table[(human, judge)] = count -> parallel label lists."""
    h, j = [], []
    for (hl, jl), c in table.items():
        h += [hl] * c
        j += [jl] * c
    return h, j


def kappa_section():
    # 100 answers, human vs judge on supported (S) / unsupported (U).
    table = {("S", "S"): 70, ("S", "U"): 5, ("U", "S"): 12, ("U", "U"): 13}
    h, j = confusion_to_labels(table)
    po, pe, k = cohens_kappa(h, j, ["S", "U"])
    print("== Cohen's kappa, judge vs human, 100 answers ==")
    print(f"observed agreement po={po:.3f}  chance agreement pe={pe:.4f}  kappa={k:.3f}")
    tp = table[("U", "U")]
    fn = table[("U", "S")]
    fp = table[("S", "U")]
    print(f"judge recall on unsupported answers = {tp}/{tp + fn} = {tp / (tp + fn):.3f}")
    print(f"judge precision on unsupported flags = {tp}/{tp + fp} = {tp / (tp + fp):.3f}")
    # Naive "always supported" judge
    h2 = h
    j2 = ["S"] * len(h)
    po2, pe2, k2 = cohens_kappa(h2, j2, ["S", "U"])
    print(f"always-S judge: agreement={po2:.3f} kappa={k2:.3f}")


def corrected_rate_section():
    # Rogan-Gladen style correction of a judge-estimated rate using sensitivity/specificity.
    # Positive class = "answer is unsupported".
    sens = 13 / 25  # judge flags 13 of the 25 truly unsupported answers
    spec = 70 / 75  # judge passes 70 of the 75 truly supported answers
    observed_flag_rate = 0.18  # judge flags 18% of production sample
    true_rate = (observed_flag_rate + spec - 1) / (sens + spec - 1)
    print()
    print("== Correcting a judge-estimated unsupported rate ==")
    print(f"sensitivity={sens:.3f} specificity={spec:.3f} observed={observed_flag_rate:.2f}")
    print(f"corrected unsupported rate = {true_rate:.3f}")


def position_bias_section():
    # Simulated pairwise judge with a position bias. True win prob of B over A is 0.5.
    rng = random.Random(11)
    n = 2000
    bias = 0.12  # extra probability of choosing the first-listed answer

    def judge(first_is_b):
        p_b_true = 0.5
        p_first = 0.5 + bias
        pick_first = rng.random() < p_first
        # judge ignores quality here to isolate position effect
        return pick_first if first_is_b else (not pick_first)  # True means B chosen

    single = sum(judge(False) for _ in range(n)) / n
    swapped = []
    for _ in range(n):
        r1 = judge(False)
        r2 = judge(True)
        swapped.append((int(r1) + int(r2)) / 2)
    both_orders = sum(swapped) / n
    print()
    print("== Position bias in a pairwise judge (quality-blind simulation) ==")
    print(f"B wins when always listed second: {single:.3f}")
    print(f"B win rate averaged over both orders: {both_orders:.3f}")
    ties = sum(1 for s in swapped if s == 0.5) / n
    print(f"share of pairs where the two orders disagree (called ties): {ties:.3f}")


def cost_section():
    # Illustrative token prices, not real: replace with your provider's current price list.
    price_in, price_out = 3.00, 12.00  # USD per 1M tokens (illustrative)
    items = 1500
    judge_calls_per_item = 4  # faithfulness, context relevance, answer relevance, citation
    in_tokens = 2600
    out_tokens = 150
    per_call = in_tokens / 1e6 * price_in + out_tokens / 1e6 * price_out
    per_run = items * judge_calls_per_item * per_call
    print()
    print("== Judge cost for one regression run (illustrative prices) ==")
    print(f"cost per judge call = ${per_call:.5f}")
    print(f"cost per run ({items} items x {judge_calls_per_item} calls) = ${per_run:.2f}")
    print(f"30 runs per month = ${30 * per_run:.2f}")


if __name__ == "__main__":
    kappa_section()
    corrected_rate_section()
    position_bias_section()
    cost_section()
