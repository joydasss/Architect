"""Capacity and cost arithmetic for the four styles. Standard library only.

All inputs are ILLUSTRATIVE assumptions, not vendor prices. Replace them with
your own measured values. The point is what each cost scales with.
"""
import math

# 1. Batch: cost scales with rows x time per row.
rows = 50_000_000
rows_per_sec_per_worker = 2_000
window_hours = 4
workers = math.ceil(rows / (rows_per_sec_per_worker * window_hours * 3600))
worker_hour_usd = 0.40
batch_cost = workers * window_hours * worker_hour_usd
print(f"batch: workers={workers}, cost/run=${batch_cost:.2f}, per 1k rows=${batch_cost/rows*1000:.5f}")

# 2. Online: cost scales with peak QPS (Little's law for concurrency).
peak_qps = 1_200
mean_latency_s = 0.060
target_util = 0.5
concurrency = peak_qps * mean_latency_s
slots_per_replica = 8
replicas = math.ceil(concurrency / (slots_per_replica * target_util))
replica_hour_usd = 0.90
online_month = replicas * replica_hour_usd * 730
print(f"online: in-flight={concurrency:.0f}, replicas={replicas}, month=${online_month:,.0f}")

# 3. RAG: cost scales with tokens per request (retrieved context dominates).
requests_day = 40_000
prompt_tokens = 300 + 6 * 400     # question + system + 6 chunks of ~400 tokens
output_tokens = 350
in_usd_per_m, out_usd_per_m = 1.00, 4.00   # illustrative per million tokens
per_req = prompt_tokens / 1e6 * in_usd_per_m + output_tokens / 1e6 * out_usd_per_m
print(f"rag: prompt={prompt_tokens} tok, per request=${per_req:.4f}, month=${per_req*requests_day*30:,.0f}")

# 4. Agent: cost scales with steps, and context grows each step.
steps = 6
base_ctx = 2_000
growth = 900            # tokens added per step (tool results + reasoning)
in_tok = sum(base_ctx + i * growth for i in range(steps))
out_tok = steps * 200
agent_req = in_tok / 1e6 * in_usd_per_m + out_tok / 1e6 * out_usd_per_m
print(f"agent: input tokens over {steps} steps={in_tok}, per run=${agent_req:.4f}, "
      f"x{agent_req/per_req:.1f} the RAG request")
retry_mult = 1 + 0.15   # 15 percent of runs retry a step
print(f"agent with retries: ${agent_req*retry_mult:.4f}")
