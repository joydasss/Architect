"""Request cost decomposition for single-call, RAG and agent requests.

Standard library only. All prices are ILLUSTRATIVE (USD) and are not any
provider's price list. Replace PRICES with your contract rates.

Run: python 01_request_cost_model.py
"""
from dataclasses import dataclass, field

# USD per 1,000,000 tokens: (input, cached input, output)
PRICES = {
    "small": (0.15, 0.015, 0.60),
    "mid": (1.00, 0.10, 4.00),
    "large": (3.00, 0.30, 15.00),
}
EMBED_PER_M = 0.02          # embedding model, USD per 1M tokens
VECTOR_QUERY = 0.00002      # vector store read cost per query
RERANK_PER_QUERY = 0.001    # reranker, per query (illustrative)
TOOL_CALL = 0.0005          # average external tool or API call
ORCHESTRATION = 0.0002      # workflow engine, queue, gateway compute
STORAGE_AND_LOGS = 0.0001   # trace, log, and cache storage per request
EGRESS_PER_GB = 0.09        # internet egress
HUMAN_RATE_PER_HOUR = 45.0  # loaded reviewer cost


@dataclass
class Cost:
    parts: dict = field(default_factory=dict)

    def add(self, name, value):
        self.parts[name] = self.parts.get(name, 0.0) + value

    @property
    def total(self):
        return sum(self.parts.values())


def llm(cost, tier, fresh_in, cached_in, out, reasoning=0, label="llm"):
    p_in, p_cache, p_out = PRICES[tier]
    cost.add(label + ".input", fresh_in * p_in / 1e6)
    cost.add(label + ".cached", cached_in * p_cache / 1e6)
    cost.add(label + ".output", (out + reasoning) * p_out / 1e6)


def overhead(cost, response_kb=20, review_rate=0.0, review_minutes=0.0):
    cost.add("orchestration", ORCHESTRATION)
    cost.add("storage_logs", STORAGE_AND_LOGS)
    cost.add("egress", response_kb / 1e6 * EGRESS_PER_GB)
    cost.add("human_review", review_rate * review_minutes / 60 * HUMAN_RATE_PER_HOUR)


def single_call():
    c = Cost()
    llm(c, "mid", fresh_in=1200, cached_in=0, out=300)
    overhead(c, review_rate=0.02, review_minutes=2)
    return c


def rag_request():
    c = Cost()
    c.add("embedding", 50 * EMBED_PER_M / 1e6)
    c.add("retrieval", VECTOR_QUERY)
    c.add("rerank", RERANK_PER_QUERY)
    # 800 token system prompt is a cache hit, 4,000 tokens retrieved context
    llm(c, "mid", fresh_in=4100, cached_in=800, out=350)
    overhead(c, review_rate=0.05, review_minutes=3)
    return c


def agent_request(steps=6, base=2000, step_growth=900, out_per_step=250,
                  reasoning_per_step=400, tool_calls=5):
    """Each step re-sends the whole transcript. The prefix is cached after step 1."""
    c = Cost()
    transcript = base
    for s in range(steps):
        cached = 0 if s == 0 else transcript
        fresh = transcript if s == 0 else step_growth
        llm(c, "large", fresh_in=fresh, cached_in=cached, out=out_per_step,
            reasoning=reasoning_per_step)
        transcript += step_growth + out_per_step
    c.add("tool_calls", tool_calls * TOOL_CALL)
    overhead(c, response_kb=40, review_rate=0.10, review_minutes=4)
    return c


def agent_without_cache(steps=6, base=2000, step_growth=900, out_per_step=250,
                        reasoning_per_step=400):
    c = Cost()
    transcript = base
    for _ in range(steps):
        llm(c, "large", fresh_in=transcript, cached_in=0, out=out_per_step,
            reasoning=reasoning_per_step)
        transcript += step_growth + out_per_step
    return c.total


def show(title, cost):
    print(f"\n{title}  total = ${cost.total:.5f}")
    for k, v in sorted(cost.parts.items(), key=lambda kv: -kv[1]):
        print(f"  {k:<16} ${v:>9.5f}  {100 * v / cost.total:5.1f}%")


def support_case_study():
    """Support assistant, naive to tuned, one lever at a time (illustrative).

    Technical cost per request = model + retrieval + overhead. Cost per resolved
    case adds human review and the human handling of escalated cases.
    """
    print("\n== Support assistant: naive to tuned ==")
    ESC, REVIEW_MIN = 4.50, 2.0
    OVER = ORCHESTRATION + STORAGE_AND_LOGS + VECTOR_QUERY

    def large_price(i, o):
        return (i * PRICES["large"][0] + o * PRICES["large"][2]) / 1e6

    # step 0: naive. large tier, 8,000 input tokens, 600 output, 10% retries
    s0 = large_price(8000, 600) * 1.10 + OVER
    # step 1: trim context (top-5 chunks of 400, summarized history) and cap output
    s1 = large_price(4100, 350) * 1.10 + OVER
    # step 2: prompt cache on 2,000-token prefix, 85% hit, write premium 1.25
    p_in, p_cache, p_out = PRICES["large"]
    prefix = 0.85 * 2000 * p_cache + 0.15 * 2000 * p_in * 1.25
    s2 = ((prefix + 2100 * p_in + 350 * p_out) / 1e6) * 1.10 + OVER
    # step 3: cascade. mid answers, small verifier, 15% escalate to large; rerank
    m_in, m_cache, m_out = PRICES["mid"]
    mprefix = 0.85 * 2000 * m_cache + 0.15 * 2000 * m_in * 1.25
    mid = (mprefix + 2600 * m_in + 300 * m_out) / 1e6
    ver = (3000 * PRICES["small"][0] + 20 * PRICES["small"][2]) / 1e6
    esc = 0.15 * large_price(4600, 350)
    s3 = (mid + ver + esc) * 1.10 + RERANK_PER_QUERY + OVER
    # step 4: fix retries (10% -> 4%)
    s4 = (mid + ver + esc) * 1.04 + RERANK_PER_QUERY + OVER
    print(f"tech cost/request: naive {s0:.5f}, trim {s1:.5f}, cache {s2:.5f}, "
          f"cascade {s3:.5f}, retries fixed {s4:.5f}")
    print(f"  mid {mid:.6f} verifier {ver:.6f} expected escalation {esc:.6f}")

    def per_case(tech, review_rate, success):
        review = review_rate * REVIEW_MIN / 60 * HUMAN_RATE_PER_HOUR
        rework = (1 - success) * ESC
        case = tech + review + rework
        return review, rework, case, case / success

    n = per_case(s0, 0.08, 0.62)
    t = per_case(s4, 0.04, 0.74)
    for name, tech, vals in (("naive", s0, n), ("tuned", s4, t)):
        print(f"{name}: tech ${tech:.5f} review ${vals[0]:.4f} rework ${vals[1]:.4f} "
              f"per case ${vals[2]:.4f} per resolved ${vals[3]:.4f}")
    vol = 1_000_000
    print(f"monthly at {vol:,} cases: tech naive ${s0 * vol:,.0f} tuned ${s4 * vol:,.0f}; "
          f"review ${n[0] * vol:,.0f} -> ${t[0] * vol:,.0f}; "
          f"escalations ${n[1] * vol:,.0f} -> ${t[1] * vol:,.0f}")
    print(f"all-human baseline ${ESC * vol:,.0f}/month; naive total ${n[2] * vol:,.0f}; "
          f"tuned total ${t[2] * vol:,.0f}")
    print(f"tech cost cut {100 * (1 - s4 / s0):.1f}%, cost per resolved case cut "
          f"{100 * (1 - t[3] / n[3]):.1f}%")


if __name__ == "__main__":
    support_case_study()
    show("Single call (mid tier)", single_call())
    show("RAG request (mid tier)", rag_request())
    agent = agent_request()
    show("Agent request (6 steps, large tier)", agent)
    llm_only = sum(v for k, v in agent.parts.items() if k.startswith("llm"))
    print(f"\nAgent model cost with prefix caching:    ${llm_only:.5f}")
    print(f"Agent model cost without prefix caching: ${agent_without_cache():.5f}")
    for steps in (3, 6, 12, 24):
        a = agent_request(steps=steps)
        print(f"agent steps={steps:>2}  total ${a.total:.4f}")
