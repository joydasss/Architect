"""Latency budget by geography for a streamed LLM answer (illustrative numbers).

Standard library only. Compares placing inference in three regions for users
in three geographies. Network RTT values are illustrative round numbers, not
measurements; measure your own paths.

Time to first token (TTFT) for a streaming request is modelled as:
  connection setup (TCP + TLS 1.3 = 2 RTT for a new connection, 0 if reused)
  + request RTT (1 RTT for request and first byte back)
  + gateway/auth/retrieval overhead
  + queue wait + prefill time
"""

RTT_MS = {
    ("eu-user", "eu-region"): 25,
    ("eu-user", "us-region"): 95,
    ("eu-user", "ap-region"): 180,
    ("us-user", "eu-region"): 95,
    ("us-user", "us-region"): 30,
    ("us-user", "ap-region"): 150,
    ("ap-user", "eu-region"): 180,
    ("ap-user", "us-region"): 150,
    ("ap-user", "ap-region"): 35,
}

APP_OVERHEAD_MS = 40      # auth, policy, request validation
RETRIEVAL_MS = 60         # vector search in the same region as the model
QUEUE_MS = 80             # p95 queue wait at target utilization
PREFILL_MS = 350          # prefill for a ~3,000 token prompt (illustrative)
TOKEN_MS = 25             # per-token decode latency
OUTPUT_TOKENS = 300
TTFT_SLO_MS = 1200


def ttft(rtt, reused_connection):
    setup = 0 if reused_connection else 2 * rtt
    return setup + rtt + APP_OVERHEAD_MS + RETRIEVAL_MS + QUEUE_MS + PREFILL_MS


def total(rtt, reused_connection):
    return ttft(rtt, reused_connection) + (OUTPUT_TOKENS - 1) * TOKEN_MS


def main():
    print(f"{'user':8} {'region':10} {'RTT':>5} {'TTFT cold':>10} {'TTFT warm':>10} "
          f"{'total warm':>11} {'SLO cold':>9}")
    for (user, region), rtt in RTT_MS.items():
        cold = ttft(rtt, False)
        warm = ttft(rtt, True)
        tot = total(rtt, True)
        ok = "ok" if cold <= TTFT_SLO_MS else "MISS"
        print(f"{user:8} {region:10} {rtt:>5} {cold:>10} {warm:>10} {tot:>11} {ok:>9}")

    # Failover that respects residency: EU users may only fail over to eu regions.
    print()
    print("Penalty of serving an EU user from us-region instead of eu-region:")
    d = ttft(95, False) - ttft(25, False)
    print(f"  extra TTFT on a new connection = {d} ms (3 RTT difference x 70 ms)")
    d2 = ttft(95, True) - ttft(25, True)
    print(f"  extra TTFT on a reused connection = {d2} ms (1 RTT difference)")


if __name__ == "__main__":
    main()
