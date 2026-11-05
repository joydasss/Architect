"""SelfCheck-style consistency scoring with a toy sampler (standard library only).

A fake 'model' answers a factual question. When it knows the fact it repeats it
in most samples; when it guesses, its samples scatter. The detector scores each
claim by how many extra samples support it, then reports an operating point.
Numbers are illustrative: real detectors must be measured on labelled data.
"""
import random

random.seed(11)
N_SAMPLES = 5


def sample_answers(knows):
    if knows:
        return ["paris" if random.random() < 0.92 else "lyon" for _ in range(N_SAMPLES)]
    pool = ["a", "b", "c", "d"]
    return [random.choice(pool) for _ in range(N_SAMPLES)]


def consistency(main_answer, samples):
    return sum(s == main_answer for s in samples) / len(samples)


items = []
for i in range(2000):
    knows = random.random() < 0.7  # 70 percent of questions are known to the model
    main = "paris" if knows else random.choice(["a", "b", "c", "d"])
    if knows and random.random() < 0.05:
        main = "lyon"  # confidently wrong in 5 percent of known cases
    correct = knows and main == "paris"
    items.append((correct, consistency(main, sample_answers(knows))))

print("accuracy of main answers:", round(sum(c for c, _ in items) / len(items), 3))
print("thr  flagged  precision(of flagged wrong)  recall(of wrong)")
wrong = [s for c, s in items if not c]
for thr in [0.4, 0.6, 0.8]:
    flagged = [(c, s) for c, s in items if s < thr]
    tp = sum(1 for c, s in flagged if not c)
    prec = tp / len(flagged) if flagged else 0
    rec = tp / len(wrong)
    print(f"{thr:.1f}  {len(flagged):5d}    {prec:.3f}                       {rec:.3f}")
