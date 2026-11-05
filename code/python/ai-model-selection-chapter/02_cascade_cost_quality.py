"""Cost and quality arithmetic for a two-stage model cascade.

Standard library only. All numbers are ILLUSTRATIVE assumptions, not vendor
prices or measured accuracies. Stage 1 is a cheap model with a confidence
score. Requests whose confidence is below a threshold escalate to a strong
model. The script sweeps the threshold on a synthetic confidence model and
prints cost per task, quality, and escalation rate, then the break-even
escalation rate against always using the strong model.
"""
import random

CHEAP_COST = 0.0004   # currency units per task, illustrative
STRONG_COST = 0.0060  # per task, illustrative
CHEAP_ACC = 0.82      # accuracy of cheap model over all tasks
# Strong model accuracy: 0.97 on items the cheap model gets right, 0.80 on the
# rest, which averages to about 0.94 over all tasks (0.82*0.97 + 0.18*0.80).


def simulate(threshold, n=20000, seed=3):
    rng = random.Random(seed)
    correct = cost = escalated = 0
    for _ in range(n):
        cheap_ok = rng.random() < CHEAP_ACC
        # Confidence is informative: higher when the cheap answer is right.
        conf = min(1.0, max(0.0, rng.gauss(0.80 if cheap_ok else 0.50, 0.15)))
        cost += CHEAP_COST
        if conf < threshold:
            escalated += 1
            cost += STRONG_COST
            # The strong model is also worse on items the cheap model misses.
            correct += rng.random() < (0.97 if cheap_ok else 0.80)
        else:
            correct += cheap_ok
    return correct / n, cost / n, escalated / n


def main():
    print("threshold  quality  cost/task  escalation")
    for t in (0.0, 0.4, 0.5, 0.6, 0.7, 0.8, 1.01):
        q, c, e = simulate(t)
        print(f"{t:9.2f}  {q:7.3f}  {c:9.5f}  {e:10.3f}")
    # Closed-form break-even: cascade cost = CHEAP + e*STRONG vs STRONG.
    e_star = (STRONG_COST - CHEAP_COST) / STRONG_COST
    print(f"\nbreak-even escalation rate vs always-strong: {e_star:.3f}")
    print(f"always-strong cost/task: {STRONG_COST:.5f}")
    e = 0.35
    print(f"at e={e:.2f} expected cost/task = {CHEAP_COST + e * STRONG_COST:.5f}")


if __name__ == "__main__":
    main()
