"""Token-based cost, latency, and memory arithmetic for an LLM feature.

Standard library only. Run: python 03_cost_latency_memory.py

All prices, speeds, and model dimensions are ILLUSTRATIVE assumptions chosen
for round arithmetic. Replace them with your provider's current price sheet
and your own measurements before using any result for a decision.
"""

# ---- Workload (illustrative summarization feature) ----
REQUESTS_PER_DAY = 50_000
DOC_TOKENS = 5_000          # document to summarize (varies per request)
STATIC_TOKENS = 1_000       # system prompt + instructions + schema (identical per request)
OUTPUT_TOKENS = 400         # visible summary
REASONING_TOKENS = 3_000    # hidden reasoning tokens for a reasoning model (billed as output)

# ---- Illustrative prices, USD per 1M tokens ----
PRICE_IN = 1.00
PRICE_OUT = 4.00
CACHE_READ_FACTOR = 0.10    # cached input billed at 10 percent of base input price
CACHE_WRITE_FACTOR = 1.25   # some providers charge a write premium; others charge none
BATCH_DISCOUNT = 0.50       # asynchronous batch endpoints are often half price


def request_cost(input_tokens, output_tokens, cached_tokens=0, cache_hit=True):
    uncached = input_tokens - cached_tokens
    cached_price = PRICE_IN * (CACHE_READ_FACTOR if cache_hit else CACHE_WRITE_FACTOR)
    cost_in = (uncached * PRICE_IN + cached_tokens * cached_price) / 1e6
    cost_out = output_tokens * PRICE_OUT / 1e6
    return cost_in, cost_out


def report(name, cin, cout, n=REQUESTS_PER_DAY):
    per = cin + cout
    print(f"{name:<34} per request ${per:.5f} (in ${cin:.5f}, out ${cout:.5f}) "
          f"| per day ${per * n:,.2f} | per 30 days ${per * n * 30:,.0f}")


def latency(prefill_tokens, output_tokens, prefill_tps=8_000, decode_tps=60, overhead_s=0.3):
    ttft = overhead_s + prefill_tokens / prefill_tps
    total = ttft + output_tokens / decode_tps
    return ttft, total


def kv_cache_bytes_per_token(layers, kv_heads, head_dim, bytes_per_value):
    # factor 2 for keys and values
    return 2 * layers * kv_heads * head_dim * bytes_per_value


def main():
    total_in = DOC_TOKENS + STATIC_TOKENS
    print(f"input tokens per request: {total_in}  output: {OUTPUT_TOKENS}")
    print("\n== Cost ==")
    report("baseline (no caching)", *request_cost(total_in, OUTPUT_TOKENS))
    report("prefix cache hit", *request_cost(total_in, OUTPUT_TOKENS, cached_tokens=STATIC_TOKENS))
    cin, cout = request_cost(total_in, OUTPUT_TOKENS, cached_tokens=STATIC_TOKENS)
    report("prefix cache + batch (50 pct)", cin * BATCH_DISCOUNT, cout * BATCH_DISCOUNT)
    report("reasoning model, same price", *request_cost(total_in, OUTPUT_TOKENS + REASONING_TOKENS))

    print("\n== Latency (illustrative speeds: prefill 8000 tok/s, decode 60 tok/s) ==")
    for name, out in (("standard", OUTPUT_TOKENS), ("reasoning", OUTPUT_TOKENS + REASONING_TOKENS)):
        ttft, total = latency(total_in, out)
        print(f"{name:<10} time to first visible token {ttft:.2f}s (reasoning adds thinking time "
              f"before visible text), total {total:.1f}s")
    # For a reasoning model the first visible token waits for the hidden tokens.
    print(f"reasoning: first visible token ~ {0.3 + total_in / 8000 + REASONING_TOKENS / 60:.1f}s")

    print("\n== Context budget (128k window example) ==")
    window, reserved_out = 128_000, 4_000
    tool_schema, system, history = 1_500, 1_000, 6_000
    left = window - reserved_out - tool_schema - system - history
    print(f"left for retrieved evidence: {left:,} tokens "
          f"(= {left / 5_000:.1f} documents of 5,000 tokens)")

    print("\n== Memory for a hypothetical 70B-parameter dense model ==")
    params = 70e9
    for fmt, b in (("FP16/BF16", 2), ("INT8/FP8", 1), ("INT4", 0.5)):
        print(f"weights {fmt:<10} {params * b / 1e9:6.0f} GB")
    per_tok = kv_cache_bytes_per_token(layers=80, kv_heads=8, head_dim=128, bytes_per_value=2)
    print(f"KV cache per token (80 layers, 8 KV heads, head_dim 128, 16-bit): "
          f"{per_tok:,} bytes = {per_tok / 1024:.0f} KiB")
    for ctx in (8_000, 32_000, 128_000):
        print(f"  context {ctx:>7,}: {per_tok * ctx / 2**30:6.2f} GiB per sequence")
    mha = kv_cache_bytes_per_token(layers=80, kv_heads=64, head_dim=128, bytes_per_value=2)
    print(f"same model with 64 KV heads (no grouping): {mha / 1024:.0f} KiB per token, "
          f"{mha * 32_000 / 2**30:.1f} GiB at 32k")

    print("\n== Rate limits: tokens per minute ==")
    per_req = total_in + OUTPUT_TOKENS
    peak_rps = 4
    tpm = peak_rps * 60 * per_req
    print(f"{peak_rps} requests/s x {per_req} tokens x 60 s = {tpm:,} tokens/minute at peak")


if __name__ == "__main__":
    main()
