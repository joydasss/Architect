"""Cost levers: cache hit-rate economics, model cascade arithmetic, Pareto
frontier, self-hosting break-even, and a 3-year build-vs-buy TCO calculator.

Standard library only. All prices and rates are ILLUSTRATIVE assumptions.

Run: python 03_levers_cascade_tco.py
"""


# ---------------------------------------------------------------- caching
def prompt_cache(prefix=6000, fresh=500, out=300, p_in=1.0, p_out=4.0,
                 read=0.10, write=1.25, hit=0.8):
    """Per-request cost with prefix caching. read/write are multiples of p_in.

    A miss writes the prefix (write premium); a hit reads it at the discount.
    """
    base = ((prefix + fresh) * p_in + out * p_out) / 1e6
    miss = (prefix * p_in * write + fresh * p_in + out * p_out) / 1e6
    hitc = (prefix * p_in * read + fresh * p_in + out * p_out) / 1e6
    exp = hit * hitc + (1 - hit) * miss
    return base, miss, hitc, exp


def cache_report():
    print("== Prompt-cache hit-rate economics (illustrative) ==")
    for h in (0.0, 0.2, 0.5, 0.8, 0.95):
        base, miss, hitc, exp = prompt_cache(hit=h)
        print(f"hit rate {h:>4.0%}  expected ${exp:.5f}  vs uncached ${base:.5f}  "
              f"saving {100 * (1 - exp / base):5.1f}%")
    base, miss, hitc, _ = prompt_cache()
    # break-even hit rate: h*hitc + (1-h)*miss = base
    h_be = (miss - base) / (miss - hitc)
    print(f"break-even hit rate {h_be:.3f}")

    print("\n-- Semantic response cache (illustrative) --")
    full = 0.0105
    lookup = 0.0002
    for h in (0.05, 0.15, 0.30):
        exp = lookup + (1 - h) * full
        print(f"hit {h:>4.0%}: expected ${exp:.5f} vs ${full:.5f} "
              f"saving {100 * (1 - exp / full):5.1f}%  "
              f"(wrong-answer hits at 2% of hits = {h * 0.02 * 100:.2f}% of traffic)")


# ---------------------------------------------------------------- cascade
def cascade():
    print("\n== Two-tier cascade, worked cost-quality arithmetic ==")
    c_small, c_large = 0.004, 0.021     # USD per attempt
    q_small, q_large = 0.55, 0.78       # first-pass acceptable rate (illustrative)
    c_judge = 0.0008                    # confidence check / verifier per attempt
    print(f"large only: cost ${c_large:.4f}, quality {q_large:.2f}")
    # Verifier accepts a small answer with recall of good answers 0.90 and
    # false accept rate 0.10 of bad answers.
    recall, fa = 0.90, 0.10
    good = q_small
    bad = 1 - q_small
    accept_good = good * recall
    accept_bad = bad * fa
    accepted = accept_good + accept_bad
    quality_of_accepted = accept_good / accepted
    escalate = 1 - accepted
    cost = c_small + c_judge + escalate * c_large
    # Quality: accepted answers are good w.p. quality_of_accepted; escalated
    # ones are good at q_large (assume escalated cases are harder: derate 0.9)
    q_esc = q_large * 0.9
    quality = accepted * quality_of_accepted + escalate * q_esc
    print(f"small accepted by verifier: {accepted:.3f} (precision {quality_of_accepted:.3f})")
    print(f"escalation rate {escalate:.3f}")
    print(f"cascade cost ${cost:.4f}  ({100 * (1 - cost / c_large):.1f}% below large-only)")
    print(f"cascade quality {quality:.3f} vs large-only {q_large:.3f}")
    # Cost per good outcome
    print(f"cost per good answer: large ${c_large / q_large:.4f}, cascade ${cost / quality:.4f}")


# ---------------------------------------------------------------- pareto
def pareto():
    print("\n== Pareto frontier over candidate configurations (illustrative) ==")
    cands = [
        ("small, no RAG", 0.0030, 0.48, 0.9),
        ("small + RAG", 0.0060, 0.62, 1.4),
        ("mid, no RAG", 0.0120, 0.60, 1.8),
        ("mid + RAG", 0.0210, 0.78, 2.6),
        ("mid + RAG + rerank", 0.0230, 0.82, 3.0),
        ("large + RAG", 0.0600, 0.84, 4.8),
        ("large + RAG + verify", 0.0900, 0.89, 7.5),
        ("large, no RAG", 0.0450, 0.66, 3.9),
        ("mid + RAG + verify", 0.0340, 0.80, 5.5),
        ("cascade small->mid", 0.0102, 0.76, 2.4),
        ("mid + RAG (cheap rerank)", 0.0190, 0.77, 2.9),
    ]
    front = []
    for n, c, q, l in cands:
        dominated = any((c2 <= c and q2 >= q and l2 <= l) and (c2, q2, l2) != (c, q, l)
                        for _, c2, q2, l2 in cands)
        if not dominated:
            front.append(n)
        print(f"{n:<26} cost ${c:.4f} quality {q:.2f} p95 {l:.1f}s "
              f"{'FRONTIER' if not dominated else 'dominated'}")
    print("frontier:", ", ".join(front))
    budget = 0.75
    ok = [(c, n) for n, c, q, l in cands if q >= budget and l <= 3.5]
    ok.sort()
    print(f"cheapest with quality >= {budget} and p95 <= 3.5s: {ok[0][1]} at ${ok[0][0]:.4f}")


# ---------------------------------------------------------------- self-hosting
def self_host():
    print("\n== Self-hosting break-even (illustrative) ==")
    gpu_hour = 4.00          # on-demand per GPU-hour, illustrative
    gpus = 2                 # tensor-parallel pair serving one replica
    replicas_min = 2         # redundancy
    hours = 730
    ops_month = 9000.0       # engineering/on-call share per month
    fixed = gpu_hour * gpus * replicas_min * hours + ops_month
    tput_per_replica = 2500  # output tokens/s at target latency, illustrative
    util = 0.45              # average utilization of replica capacity
    served = tput_per_replica * replicas_min * util * 3600 * hours   # tokens/month
    print(f"monthly fixed cost ${fixed:,.0f}")
    print(f"tokens/month at {util:.0%} utilization: {served / 1e9:.2f}B")
    print(f"effective self-host cost per 1M tokens ${fixed / (served / 1e6):.3f}")
    api = 0.60  # blended API price per 1M tokens for a comparable model, illustrative
    be = fixed / api * 1e6 / 1e9
    print(f"API at ${api:.2f}/1M: break-even volume {be:.2f}B tokens/month")
    for u in (0.15, 0.30, 0.45, 0.70):
        s = tput_per_replica * replicas_min * u * 3600 * hours
        print(f"  utilization {u:>4.0%}: ${fixed / (s / 1e6):.3f} per 1M tokens")


# ---------------------------------------------------------------- TCO
def tco(tokens0=4.0e9, tput=2500):
    print(f"\n== 3-year TCO, {tokens0 / 1e9:.0f}B tokens/month in year 1, {tput} tok/s per replica (illustrative) ==")
    years = 3
    # tokens0: tokens per month in year 1
    growth = 1.6             # yearly volume multiplier
    api = 0.60               # USD per 1M tokens
    api_discount = 0.10      # commitment discount in years 2 and 3
    price_drop = 0.25        # assumed yearly API price decline (uncertain)
    api_total = 0.0
    self_total = 0.0
    capex_setup = 120000.0   # platform build, evaluation, security review
    for y in range(1, years + 1):
        vol = tokens0 * growth ** (y - 1) * 12
        price = api * (1 - price_drop) ** (y - 1) * (1 - (api_discount if y > 1 else 0))
        api_y = vol / 1e6 * price + 30000          # gateway, evals, monitoring
        replicas = max(2, -(-vol / 12 // (tput * 3600 * 730 * 0.5)))
        gpu = 4.0 * 2 * replicas * 730 * 12 * (0.65 if y > 1 else 1.0)  # reserved after year 1
        ops = 9000 * 12 + 15000 * replicas
        self_y = gpu + ops + (capex_setup if y == 1 else 0)
        api_total += api_y
        self_total += self_y
        print(f"year {y}: volume {vol / 1e9:5.1f}B tok  API ${api_y:>10,.0f}   "
              f"self-host ${self_y:>10,.0f} ({int(replicas)} replicas)")
    print(f"3-year TCO: API ${api_total:,.0f}  self-host ${self_total:,.0f}")
    print("Self-host wins only if its volume and utilization assumptions hold.")


if __name__ == "__main__":
    cache_report()
    cascade()
    pareto()
    self_host()
    tco()
    tco(40.0e9)
    tco(40.0e9, tput=7500)
    tco(40.0e9, tput=15000)
