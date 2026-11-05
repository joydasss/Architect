"""Build-vs-adopt weighted scoring with sensitivity analysis, plus transitive
dependency counting. Standard library only.

Part A: weighted scoring matrix (scores 1-5 are ILLUSTRATIVE judgments from the
chapter's worked example, not measurements). It reports the winner, the margin,
and how many random +/-1 perturbations of the weights change the winner.
Part B: transitive dependency closure on a small ILLUSTRATIVE graph, and the same
function applied to the real installed distributions via importlib.metadata.

Run: python 03_scoring_and_dependencies.py
"""
from __future__ import annotations

import random
import re
from importlib import metadata

CRITERIA = ["fit", "visibility", "ops", "portability", "security", "skills", "speed"]
WEIGHTS = {"fit": 5, "visibility": 4, "ops": 4, "portability": 4, "security": 4, "skills": 2, "speed": 3}
SCORES = {
    "A direct SDK + own glue":     {"fit": 4, "visibility": 5, "ops": 4, "portability": 4, "security": 4, "skills": 3, "speed": 2},
    "B thin library (typed, small)": {"fit": 4, "visibility": 4, "ops": 4, "portability": 4, "security": 4, "skills": 4, "speed": 4},
    "C full orchestration framework": {"fit": 5, "visibility": 2, "ops": 3, "portability": 2, "security": 3, "skills": 4, "speed": 5},
    "D low-code platform":           {"fit": 2, "visibility": 1, "ops": 3, "portability": 1, "security": 3, "skills": 5, "speed": 5},
}


def total(weights: dict, scores: dict) -> int:
    return sum(weights[c] * scores[c] for c in CRITERIA)


def part_a() -> None:
    print("Part A: weighted scores (max =", 5 * sum(WEIGHTS.values()), ")")
    ranked = sorted(SCORES, key=lambda k: -total(WEIGHTS, SCORES[k]))
    for name in ranked:
        print(f"  {total(WEIGHTS, SCORES[name]):3d}  {name}")
    base_winner = ranked[0]
    rng = random.Random(7)
    changed = 0
    trials = 2000
    for _ in range(trials):
        w = {c: max(1, WEIGHTS[c] + rng.choice([-1, 0, 1])) for c in CRITERIA}
        win = max(SCORES, key=lambda k: total(w, SCORES[k]))
        changed += win != base_winner
    print(f"  winner: {base_winner}; changes in {changed}/{trials} random +/-1 weight perturbations")
    # Gate criteria: any option scoring 1 on a gate is disqualified regardless of total.
    gates = {"visibility": 2, "portability": 2}
    for name, sc in SCORES.items():
        failed = [g for g, mn in gates.items() if sc[g] < mn]
        if failed:
            print(f"  gate fail: {name} -> {', '.join(failed)}")


def closure(graph: dict, root: str) -> set:
    seen, stack = set(), [root]
    while stack:
        node = stack.pop()
        for dep in graph.get(node, []):
            if dep not in seen:
                seen.add(dep)
                stack.append(dep)
    return seen


ILLUSTRATIVE = {
    "app-direct": ["httpx"],
    "httpx": ["httpcore", "certifi", "idna", "anyio"],
    "httpcore": ["h11", "certifi"],
    "anyio": ["idna", "sniffio"],
    "app-thin": ["httpx", "pydantic"],
    "pydantic": ["annotated-types", "pydantic-core", "typing-extensions"],
    "app-framework": ["fw-core", "fw-openai", "fw-community"],
    "fw-core": ["pydantic", "pyyaml", "tenacity", "jsonpatch", "langsmith-like", "numpy"],
    "fw-openai": ["httpx", "tiktoken"],
    "tiktoken": ["regex", "requests"],
    "requests": ["urllib3", "charset-normalizer", "idna", "certifi"],
    "fw-community": ["sqlalchemy", "aiohttp", "dataclasses-json", "requests"],
    "aiohttp": ["multidict", "yarl", "frozenlist", "aiosignal", "attrs", "aiohappyeyeballs"],
    "dataclasses-json": ["marshmallow", "typing-inspect"],
    "sqlalchemy": ["greenlet", "typing-extensions"],
}


def part_b() -> None:
    print("Part B: transitive dependency counts on an ILLUSTRATIVE graph")
    for root in ("app-direct", "app-thin", "app-framework"):
        print(f"  {root:14s} {len(closure(ILLUSTRATIVE, root)):3d} transitive packages")
    print("Real installed environment:")
    graph = {}
    for dist in metadata.distributions():
        name = dist.metadata["Name"]
        if not name:
            continue
        deps = []
        for req in dist.requires or []:
            if "extra ==" in req:
                continue
            m = re.match(r"[A-Za-z0-9_.\-]+", req)
            if m:
                deps.append(m.group(0).lower().replace("_", "-"))
        graph[name.lower().replace("_", "-")] = deps
    print(f"  installed distributions: {len(graph)}")
    if graph:
        widest = max(graph, key=lambda n: len(closure(graph, n)))
        print(f"  widest closure: {widest} -> {len(closure(graph, widest))} packages")


if __name__ == "__main__":
    part_a()
    part_b()
