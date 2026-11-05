"""Per-query cost and latency model for a RAG pipeline (standard library only).

All prices and latencies are ILLUSTRATIVE parameters, not vendor quotes.
Replace them with your own measured values. The script prints the arithmetic
used in the chapter: per-query cost, cost per million queries, a serial
latency budget, and the effect of a semantic-cache hit rate.
"""

PRICE_IN_PER_M = 3.00      # USD per million input tokens (illustrative)
PRICE_OUT_PER_M = 15.00    # USD per million output tokens (illustrative)
RERANK_PER_1K_SEARCHES = 2.00  # USD per 1,000 rerank requests (illustrative)
EMBED_PER_M = 0.10         # USD per million embedding tokens (illustrative)


def per_query_cost(question_tokens=40, system_tokens=400, context_tokens=3000,
                   history_tokens=300, output_tokens=350):
    embed = question_tokens * EMBED_PER_M / 1e6
    rerank = RERANK_PER_1K_SEARCHES / 1000
    prompt = system_tokens + context_tokens + history_tokens + question_tokens
    llm_in = prompt * PRICE_IN_PER_M / 1e6
    llm_out = output_tokens * PRICE_OUT_PER_M / 1e6
    return {"embed": embed, "rerank": rerank, "llm_in": llm_in,
            "llm_out": llm_out, "prompt_tokens": prompt,
            "total": embed + rerank + llm_in + llm_out}


def latency_budget(stages):
    total = sum(v for v in stages.values())
    return total


if __name__ == "__main__":
    c = per_query_cost()
    print("prompt tokens:", c["prompt_tokens"])
    for k in ("embed", "rerank", "llm_in", "llm_out", "total"):
        print(f"  {k:<8} ${c[k]:.6f}")
    print(f"cost per 1M queries: ${c['total'] * 1e6:,.0f}")

    # Same pipeline with context trimmed from 3000 to 1500 tokens.
    c2 = per_query_cost(context_tokens=1500)
    print(f"1500-token context: ${c2['total']:.6f}/query, "
          f"${c2['total'] * 1e6:,.0f} per 1M")

    # Semantic cache: hit costs only the embedding lookup (approx.).
    hit = 0.30
    cached = hit * c["embed"] + (1 - hit) * c["total"] + hit * 0
    print(f"semantic cache hit rate {hit:.0%}: ${cached:.6f}/query")

    stages = {"auth+rewrite (LLM small)": 350, "embed query": 30,
              "vector+BM25 (parallel)": 60, "rerank 50 docs": 180,
              "assemble": 10, "LLM time to first token": 450}
    ttft = latency_budget(stages)
    print("serial pre-generation latency ms:", ttft)
    for k, v in stages.items():
        print(f"  {k:<26} {v:>4} ms")
    gen = 350 / 60 * 1000
    print(f"generation of 350 tokens at 60 tok/s: {gen:.0f} ms; total {ttft + gen:.0f} ms")
