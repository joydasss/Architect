"""A mini evaluation runner: versioned dataset, cached judge calls, regression report.

Standard library only. Run: python 03_mini_eval_runner.py

The "systems under test" and the "judge" are deterministic stubs so the output
is reproducible. The architecture is the point: dataset digest, evaluator
version, content-addressed judge cache, per-slice results, paired comparison
with a bootstrap interval, and a gate decision.
"""
from __future__ import annotations

import hashlib
import json
import random

DATASET_VERSION = "golden-2026-10-a"
JUDGE_VERSION = "judge-rubric-v3"

CASES = [{"id": f"c{i:03d}", "slice": "billing" if i % 3 == 0 else "tech" if i % 3 == 1 else "legal",
          "question": f"q{i}"} for i in range(120)]


def dataset_digest(cases: list[dict]) -> str:
    blob = json.dumps(cases, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:12]


def system_under_test(version: str, case: dict) -> str:
    """Stub: the candidate regresses on the legal slice."""
    h = int(hashlib.sha256(f"{version}|{case['id']}".encode()).hexdigest(), 16)
    bad_rate = {"baseline": 0.10, "candidate": 0.10}[version]
    if version == "candidate" and case["slice"] == "legal":
        bad_rate = 0.30
    return "bad" if (h % 1000) / 1000 < bad_rate else "good"


class CachedJudge:
    """Judge calls are cached by (judge version, input, output) so reruns cost nothing."""

    def __init__(self) -> None:
        self.cache: dict[str, int] = {}
        self.calls = 0
        self.hits = 0

    def score(self, question: str, answer: str) -> int:
        key = hashlib.sha256(f"{JUDGE_VERSION}|{question}|{answer}".encode()).hexdigest()
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.calls += 1  # a real judge would call a model here
        s = 1 if answer == "good" else 0
        self.cache[key] = s
        return s


def run(version: str, judge: CachedJudge) -> dict[str, int]:
    return {c["id"]: judge.score(c["question"], system_under_test(version, c)) for c in CASES}


def paired_bootstrap(a: list[int], b: list[int], iters: int = 2000, seed: int = 7) -> tuple[float, float]:
    rng = random.Random(seed)
    n = len(a)
    diffs = []
    for _ in range(iters):
        idx = [rng.randrange(n) for _ in range(n)]
        diffs.append(sum(b[i] - a[i] for i in idx) / n)
    diffs.sort()
    return diffs[int(0.025 * iters)], diffs[int(0.975 * iters)]


if __name__ == "__main__":
    judge = CachedJudge()
    print("dataset", DATASET_VERSION, "digest", dataset_digest(CASES), "judge", JUDGE_VERSION)
    base = run("baseline", judge)
    cand = run("candidate", judge)
    run("candidate", judge)  # rerun: all cache hits
    print(f"judge calls={judge.calls} cache hits={judge.hits}")

    ids = [c["id"] for c in CASES]
    a = [base[i] for i in ids]
    b = [cand[i] for i in ids]
    print(f"overall pass: baseline={sum(a)/len(a):.3f} candidate={sum(b)/len(b):.3f}")
    lo, hi = paired_bootstrap(a, b)
    print(f"overall delta 95% interval: [{lo:+.3f}, {hi:+.3f}]")
    for sl in ("billing", "tech", "legal"):
        sub = [i for i, c in enumerate(CASES) if c["slice"] == sl]
        sa, sb = [a[i] for i in sub], [b[i] for i in sub]
        lo, hi = paired_bootstrap(sa, sb)
        print(f"  slice {sl:8s} n={len(sub)} base={sum(sa)/len(sa):.3f} cand={sum(sb)/len(sb):.3f}"
              f" delta interval [{lo:+.3f}, {hi:+.3f}]")
    worst = min(
        (sum(b[i] for i, c in enumerate(CASES) if c["slice"] == sl) / sum(1 for c in CASES if c["slice"] == sl), sl)
        for sl in ("billing", "tech", "legal"))
    gate = "BLOCK" if worst[0] < 0.85 else "PASS"
    print(f"gate (every slice pass rate >= 0.85): {gate} (worst slice {worst[1]} at {worst[0]:.3f})")
