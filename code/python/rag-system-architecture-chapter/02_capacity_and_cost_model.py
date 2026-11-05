"""Capacity and cost model for a RAG system (ingestion and query).

Standard library only. Every input is an illustrative assumption; replace
with measurements and current provider prices before using.
"""
import math

# ---------------- Corpus and ingestion ----------------
docs = 2_000_000
avg_tokens_per_doc = 3_000
chunk_tokens = 400
overlap = 50
stride = chunk_tokens - overlap
chunks_per_doc = math.ceil(max(avg_tokens_per_doc - overlap, 1) / stride)
chunks = docs * chunks_per_doc
dim = 1024
bytes_per_float = 4
raw_vec_gb = chunks * dim * bytes_per_float / 1e9
hnsw_overhead = 1.5  # graph links and metadata multiplier (assumption)
index_gb = raw_vec_gb * hnsw_overhead
print(f"chunks/doc {chunks_per_doc}, chunks {chunks:,}")
print(f"raw vectors {raw_vec_gb:,.1f} GB, index with overhead {index_gb:,.1f} GB")

embed_tps = 40_000  # tokens/s per embedding worker (assumption)
total_tokens = chunks * chunk_tokens
workers = 8
full_hours = total_tokens / (embed_tps * workers) / 3600
print(f"full rebuild tokens {total_tokens/1e9:.2f} B, {workers} workers: {full_hours:.1f} h")

daily_change = 0.02
delta_tokens = total_tokens * daily_change
delta_minutes = delta_tokens / (embed_tps * workers) / 60
print(f"daily delta {daily_change:.0%}: {delta_tokens/1e6:.0f} M tokens, {delta_minutes:.1f} min on {workers} workers")

embed_price_per_m = 0.02  # USD per million tokens (assumption)
rebuild_cost = total_tokens / 1e6 * embed_price_per_m
delta_cost_month = delta_tokens / 1e6 * embed_price_per_m * 30
print(f"embedding cost: full rebuild ${rebuild_cost:,.0f}, monthly deltas ${delta_cost_month:,.0f}")

# ---------------- Query path ----------------
qps_peak = 60
retrieval_p50_ms = 80
rerank_ms = 120
gen_ms = 2500
# Little's law: concurrency L = lambda * W
L_gen = qps_peak * gen_ms / 1000
print(f"\npeak {qps_peak} qps, generation concurrency (Little) {L_gen:.0f} in flight")
per_replica_conc = 12
replicas = math.ceil(L_gen / per_replica_conc / 0.7)  # 70 percent target utilization
print(f"app replicas at {per_replica_conc} concurrent each, 70% target: {replicas}")

# ---------------- Cost per query ----------------
ctx_tokens = 6_000
sys_tokens = 500
q_tokens = 100
out_tokens = 400
in_price = 1.00  # USD per million input tokens (assumption)
out_price = 4.00  # USD per million output tokens (assumption)
rerank_price_per_1k = 0.002  # USD per 1k reranked docs (assumption)
rerank_docs = 50
gen_cost = (ctx_tokens + sys_tokens + q_tokens) / 1e6 * in_price + out_tokens / 1e6 * out_price
rr_cost = rerank_docs / 1000 * rerank_price_per_1k
embed_q = q_tokens / 1e6 * embed_price_per_m
per_query = gen_cost + rr_cost + embed_q
print(f"\nper query: generation ${gen_cost:.5f}, rerank ${rr_cost:.5f}, query embed ${embed_q:.7f}")
print(f"per query total ${per_query:.5f}")
hit = 0.20
monthly_q = 3_000_000
print(f"monthly {monthly_q:,} queries: ${monthly_q*per_query:,.0f}; "
      f"with {hit:.0%} exact-cache hit on answers: ${monthly_q*per_query*(1-hit):,.0f}")
print(f"cost if context grows 6,000 -> 12,000 tokens: "
      f"${((12_000 + sys_tokens + q_tokens)/1e6*in_price + out_tokens/1e6*out_price + rr_cost + embed_q):.5f} per query")
