"""Deadline budget checker for an AI request path (standard library only).

Allocates a total deadline across stages, checks that per-hop timeouts nest
inside the remaining parent budget, and shows what a retry does to the budget.
All latencies are illustrative.
"""

from dataclasses import dataclass


@dataclass
class Stage:
    name: str
    p99_ms: int        # measured 99th percentile latency of one attempt
    timeout_ms: int    # configured per-attempt timeout
    attempts: int      # attempts allowed at this stage (1 = no retry)
    mandatory: bool    # False means the stage may be skipped when budget is short


TOTAL_MS = 10_000
RESERVE_MS = 1_000     # reserved for fallback or error response and delivery

PATH = [
    Stage("auth_and_policy", 150, 300, 1, True),
    Stage("retrieval", 600, 1_200, 2, False),
    Stage("rerank", 250, 500, 1, False),
    Stage("generation", 5_500, 6_500, 1, True),
    Stage("validation", 200, 400, 1, True),
]


def worst_case_ms(stage: Stage) -> int:
    return stage.timeout_ms * stage.attempts


def check(path, total_ms, reserve_ms):
    usable = total_ms - reserve_ms
    spent_p99 = sum(s.p99_ms for s in path)
    spent_worst = sum(worst_case_ms(s) for s in path)
    print(f"total deadline      : {total_ms} ms")
    print(f"reserve (fallback)  : {reserve_ms} ms")
    print(f"usable for stages   : {usable} ms")
    print(f"sum of p99 (1 try)  : {spent_p99} ms")
    print(f"sum of worst cases  : {spent_worst} ms")
    print()
    ok = True
    if spent_worst > usable:
        print(f"WARN worst case {spent_worst} ms exceeds usable {usable} ms:")
        print("     timeouts do not nest; the deadline must cut stages short.")
        ok = False
    for s in path:
        if s.timeout_ms < s.p99_ms:
            print(f"WARN {s.name}: timeout {s.timeout_ms} ms below p99 {s.p99_ms} ms"
                  " (will time out healthy requests)")
            ok = False
    return ok


def simulate_remaining(path, total_ms, reserve_ms, observed):
    """Walk the path with propagated deadline; observed maps stage -> ms taken."""
    deadline_left = total_ms - reserve_ms
    print("\npropagated deadline walk (retrieval is slow, 2 attempts used):")
    for s in path:
        took = observed.get(s.name, s.p99_ms)
        allowed = min(worst_case_ms(s), deadline_left)
        if allowed <= 0:
            action = "skip (optional)" if not s.mandatory else "MANDATORY, no budget"
            print(f"  {s.name:16s} left={deadline_left:5d} ms -> {action}")
            continue
        used = min(took, allowed)
        deadline_left -= used
        flag = " (cut by deadline)" if took > allowed else ""
        print(f"  {s.name:16s} left={deadline_left + used:5d} ms, used={used:5d} ms{flag}")
    print(f"  remaining after path: {deadline_left} ms (plus {reserve_ms} ms reserve)")


FIXED = [
    Stage("auth_and_policy", 150, 300, 1, True),
    Stage("retrieval", 600, 1_000, 1, False),
    Stage("rerank", 250, 500, 1, False),
    Stage("generation", 5_500, 6_800, 1, True),
    Stage("validation", 200, 400, 1, True),
]


if __name__ == "__main__":
    print("### naive configuration")
    ok = check(PATH, TOTAL_MS, RESERVE_MS)
    print("\nnesting check:", "PASS" if ok else "FAIL")
    # Slow day: retrieval takes 1,200 ms on both attempts, generation takes 6,500 ms.
    simulate_remaining(PATH, TOTAL_MS, RESERVE_MS,
                       {"retrieval": 2_400, "generation": 6_500})
    print("\n### redesigned configuration")
    ok = check(FIXED, TOTAL_MS, RESERVE_MS)
    print("\nnesting check:", "PASS" if ok else "FAIL")
