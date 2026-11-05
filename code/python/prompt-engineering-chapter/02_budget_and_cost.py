"""Context budget, prompt-chain vs single-prompt arithmetic, prompt-cache cost.

Standard library only. All prices are ILLUSTRATIVE, not any provider's list
price. Run: python 02_budget_and_cost.py
"""

PRICE_IN = 3.00 / 1_000_000       # dollars per input token (illustrative)
PRICE_OUT = 15.00 / 1_000_000     # dollars per output token (illustrative)
CACHE_READ = 0.10                 # multiplier on input price (illustrative)
CACHE_WRITE = 1.25                # multiplier on input price (illustrative)


def budget():
    window = 32_000
    static = 1_800
    tools = 900
    output_reserve = 2_000
    safety = 0.05 * window
    history_cap = 4_000
    task = 600
    evidence = window - static - tools - output_reserve - safety - history_cap - task
    print("== context budget ==")
    for name, v in [("window", window), ("static prompt", static), ("tool schemas", tools),
                    ("output reserve", output_reserve), ("safety margin 5%", safety),
                    ("history cap", history_cap), ("current task", task),
                    ("evidence budget (remainder)", evidence)]:
        print(f"{name:30s}{v:>9,.0f}")
    chunk = 450
    print(f"chunks of {chunk} tokens that fit: {int(evidence // chunk)}")


def chain_vs_single():
    print("\n== chain vs single prompt (per request) ==")
    doc = 3_000
    # single prompt: one call with long instructions, long answer
    single_in, single_out = 1_500 + doc, 400
    single_cost = single_in * PRICE_IN + single_out * PRICE_OUT
    # chain: extract -> classify -> compose, each re-reading part of the doc
    steps = [(600 + doc, 250), (500 + 250, 60), (700 + 250 + 60, 300)]
    chain_cost = sum(i * PRICE_IN + o * PRICE_OUT for i, o in steps)
    print(f"single: in={single_in} out={single_out} cost=${single_cost:.5f}")
    print(f"chain : in={sum(i for i, _ in steps)} out={sum(o for _, o in steps)} cost=${chain_cost:.5f}")
    print(f"cost ratio chain/single: {chain_cost / single_cost:.2f}")
    # accuracy arithmetic: independent step accuracies multiply
    single_acc = 0.86
    step_acc = [0.97, 0.96, 0.98]
    chain_acc = 1.0
    for a in step_acc:
        chain_acc *= a
    print(f"single accuracy {single_acc:.3f}; chain accuracy (product) {chain_acc:.3f}")
    # latency: sequential output tokens dominate, 60 tokens/s decode, 0.4 s per call overhead
    tps, overhead = 60.0, 0.4
    lat_single = overhead + single_out / tps
    lat_chain = sum(overhead + o / tps for _, o in steps)
    print(f"latency single {lat_single:.2f}s; chain {lat_chain:.2f}s")


def caching():
    print("\n== prompt caching (prefix reuse) ==")
    prefix, suffix, out = 6_000, 400, 300
    n = 1_000
    no_cache = n * ((prefix + suffix) * PRICE_IN + out * PRICE_OUT)
    # first request writes the prefix, the rest read it (assumes cache stays warm)
    first = prefix * PRICE_IN * CACHE_WRITE + suffix * PRICE_IN + out * PRICE_OUT
    rest = (n - 1) * (prefix * PRICE_IN * CACHE_READ + suffix * PRICE_IN + out * PRICE_OUT)
    cached = first + rest
    print(f"{n} requests, no cache : ${no_cache:.2f}")
    print(f"{n} requests, cached   : ${cached:.2f} (saving {100 * (1 - cached / no_cache):.1f}%)")
    # break-even number of requests inside one TTL window
    k = 1
    while prefix * PRICE_IN * (CACHE_WRITE + (k - 1) * CACHE_READ) >= k * prefix * PRICE_IN:
        k += 1
    print(f"prefix reads needed inside the TTL to beat no caching: {k} requests")
    # hit-rate sensitivity
    for h in (0.0, 0.3, 0.6, 0.9):
        per = (h * prefix * CACHE_READ + (1 - h) * prefix * CACHE_WRITE + suffix) * PRICE_IN + out * PRICE_OUT
        base = (prefix + suffix) * PRICE_IN + out * PRICE_OUT
        print(f"hit rate {h:.1f}: ${per:.5f} per request vs ${base:.5f} ({100 * (per / base - 1):+.1f}%)")


if __name__ == "__main__":
    budget()
    chain_vs_single()
    caching()
