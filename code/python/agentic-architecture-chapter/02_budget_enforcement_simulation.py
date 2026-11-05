"""Runtime budget enforcement for an agent loop, plus tenant quotas.

Standard library only. A simulated runaway agent repeats the same search call
and never finishes. Independent budgets (steps, tokens, money, wall clock,
tool calls, identical-call repeats) stop it. The numbers are illustrative.
"""

from dataclasses import dataclass, field

PRICE_IN_PER_MTOK = 3.00    # illustrative USD per million input tokens
PRICE_OUT_PER_MTOK = 15.00  # illustrative USD per million output tokens


@dataclass
class Budget:
    max_steps: int = 20
    max_tokens: int = 150_000
    max_usd: float = 0.50
    max_seconds: float = 120.0
    max_tool_calls: int = 12
    max_identical_calls: int = 3


@dataclass
class RunState:
    steps: int = 0
    tokens: int = 0
    usd: float = 0.0
    seconds: float = 0.0
    tool_calls: int = 0
    seen: dict = field(default_factory=dict)


def check(b, s, call_key=None):
    """Return a terminal reason or None. Checked BEFORE each step."""
    if s.steps >= b.max_steps:
        return "steps_exhausted"
    if s.tokens >= b.max_tokens:
        return "tokens_exhausted"
    if s.usd >= b.max_usd:
        return "money_exhausted"
    if s.seconds >= b.max_seconds:
        return "wall_clock_exhausted"
    if s.tool_calls >= b.max_tool_calls:
        return "tool_calls_exhausted"
    if call_key is not None and s.seen.get(call_key, 0) >= b.max_identical_calls:
        return "no_progress_repeat"
    return None


def step_cost(tokens_in, tokens_out):
    return tokens_in / 1e6 * PRICE_IN_PER_MTOK + tokens_out / 1e6 * PRICE_OUT_PER_MTOK


def run_agent(b, ctx_growth=4_000, out_tokens=300, step_seconds=6.0, label=""):
    s = RunState()
    context = 6_000  # starting prompt tokens; grows each step as history is appended
    while True:
        key = "search:refund policy"  # the runaway agent repeats this call
        why = check(b, s, key)
        if why:
            print(f"{label:28s} stop={why:22s} steps={s.steps:2d} tokens={s.tokens:7d} "
                  f"usd={s.usd:.3f} sec={s.seconds:5.1f}")
            return s
        s.steps += 1
        s.tokens += context + out_tokens
        s.usd += step_cost(context, out_tokens)
        s.seconds += step_seconds
        s.tool_calls += 1
        s.seen[key] = s.seen.get(key, 0) + 1
        context += ctx_growth


class TenantQuota:
    """Fixed-window token quota shared by all runs of a tenant."""

    def __init__(self, tokens_per_window):
        self.limit = tokens_per_window
        self.used = 0

    def reserve(self, tokens):
        if self.used + tokens > self.limit:
            return False
        self.used += tokens
        return True


if __name__ == "__main__":
    print("== one runaway run, each budget alone (others set very high) ==")
    big = dict(max_steps=10**6, max_tokens=10**9, max_usd=1e9, max_seconds=1e9,
               max_tool_calls=10**6, max_identical_calls=10**6)
    for name, val in [("max_steps", 20), ("max_tokens", 150_000), ("max_usd", 0.50),
                      ("max_seconds", 120.0), ("max_tool_calls", 12),
                      ("max_identical_calls", 3)]:
        cfg = dict(big)
        cfg[name] = val
        run_agent(Budget(**cfg), label=f"only {name}={val}")

    print("== all budgets together ==")
    run_agent(Budget(), label="default budget")

    print("== tenant quota: 1,000,000 tokens per window ==")
    q = TenantQuota(1_000_000)
    admitted = 0
    per_run_reserve = 150_000  # worst case reserved up front = max_tokens
    for i in range(10):
        if q.reserve(per_run_reserve):
            admitted += 1
    print(f"runs admitted with worst-case reservation: {admitted} "
          f"(1,000,000 // 150,000 = {1_000_000 // 150_000})")
