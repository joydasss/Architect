"""Voice-agent latency budget: cascaded (ASR -> LLM -> TTS) vs speech-to-speech.

Standard library only. All stage latencies are ILLUSTRATIVE assumptions
(median ms and a lognormal spread). Replace them with your own measurements.
The simulation shows why p95 of the sum is not the sum of p95s.
"""
import math
import random

random.seed(7)

# (name, median_ms, sigma of log-normal)
CASCADED = [
    ("network up", 40, 0.30),
    ("endpoint wait", 400, 0.20),
    ("ASR final", 120, 0.35),
    ("LLM first token", 350, 0.45),
    ("sentence buffer", 150, 0.30),
    ("TTS first audio", 150, 0.35),
    ("network down", 40, 0.30),
    ("playout buffer", 60, 0.10),
]
S2S = [
    ("network up", 40, 0.30),
    ("endpoint wait", 300, 0.20),
    ("model first audio", 300, 0.40),
    ("network down", 40, 0.30),
    ("playout buffer", 60, 0.10),
]


def sample(stage):
    _, med, sigma = stage
    return random.lognormvariate(math.log(med), sigma)


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(p / 100 * len(xs)))]


def report(name, stages, n=50_000):
    sums = [sum(sample(s) for s in stages) for _ in range(n)]
    med_sum = sum(s[1] for s in stages)
    p95_each = sum(pct([sample(s) for _ in range(n)], 95) for s in stages)
    print(f"{name}")
    print(f"  sum of medians        : {med_sum:>6.0f} ms")
    print(f"  sum of per-stage p95  : {p95_each:>6.0f} ms")
    print(f"  simulated total p50   : {pct(sums, 50):>6.0f} ms")
    print(f"  simulated total p95   : {pct(sums, 95):>6.0f} ms")
    print(f"  share over 800 ms     : {sum(x > 800 for x in sums) / n:>6.1%}")
    return sums


if __name__ == "__main__":
    report("Cascaded", CASCADED)
    print()
    report("Speech-to-speech", S2S)
    print()
    print("Endpointing trade-off: silence threshold vs cut-offs (illustrative)")
    for thr, cutoff in [(200, 0.18), (400, 0.07), (700, 0.03), (1000, 0.01)]:
        print(f"  threshold {thr:>4} ms -> adds {thr} ms, premature cut-off rate {cutoff:.0%}")
