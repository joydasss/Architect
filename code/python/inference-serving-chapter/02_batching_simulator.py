"""Discrete-event comparison of static, dynamic, continuous, and chunked batching.

Standard library only. The cost model is illustrative, shaped like a 70B-class
model on a 4-GPU tensor-parallel group (see 01_roofline_decode.py):

    iteration time = C0 + C1 * (decoding sequences) + C2 * (prefill tokens)

C0 is the weight-read floor, C1 the per-sequence KV read cost, C2 the
compute-bound prefill cost per token. Request-level policies run a whole batch
to completion; continuous policies admit work at every iteration.
"""
import random
import statistics

C0, C1, C2 = 0.0185, 0.00022, 0.00007   # seconds
MAX_SEQS = 32
TTFT_SLO, TPOT_SLO = 2.0, 0.060          # goodput SLO (seconds)


def make_requests(n, rate, seed, long_frac=0.0):
    rng = random.Random(seed)
    t, reqs = 0.0, []
    for i in range(n):
        t += rng.expovariate(rate)
        prompt = int(min(6000, max(50, rng.lognormvariate(6.5, 0.9))))   # median ~665
        if rng.random() < long_frac:
            prompt = 24000                                               # rare very long prompt
        out = int(min(800, max(10, rng.lognormvariate(5.0, 0.8))))      # median ~148
        reqs.append({"id": i, "arr": t, "prompt": prompt, "out": out,
                     "first": None, "done": None})
    return reqs


def run_request_level(reqs, batch_size, max_wait):
    """Static (max_wait=inf) and dynamic (max_wait finite) request-level batching."""
    pending, clock, i, n = [], 0.0, 0, len(reqs)
    completed = 0
    while completed < n:
        while i < n and reqs[i]["arr"] <= clock:
            pending.append(reqs[i]); i += 1
        if not pending:
            clock = max(clock, reqs[i]["arr"]); continue
        oldest = pending[0]["arr"]
        ready = len(pending) >= batch_size or (i >= n) or (clock - oldest >= max_wait - 1e-9)
        if not ready:
            nxt = reqs[i]["arr"] if i < n else float("inf")
            clock = min(nxt, oldest + max_wait); continue
        batch, pending = pending[:batch_size], pending[batch_size:]
        clock += C0 + C2 * sum(r["prompt"] for r in batch)       # one prefill pass
        for r in batch:
            r["first"] = clock
        steps = max(r["out"] for r in batch)
        for s in range(1, steps):
            alive = sum(1 for r in batch if r["out"] > s)
            clock += C0 + C1 * alive                              # finished slots stay padded
            for r in batch:
                if r["out"] == s + 1:
                    r["done"] = clock
        for r in batch:
            if r["done"] is None:
                r["done"] = r["first"]
        completed += len(batch)


def run_continuous(reqs, chunk_budget=None):
    """Iteration-level scheduling. chunk_budget=None prefills a whole prompt in
    one iteration; otherwise at most chunk_budget prefill tokens join each decode step."""
    waiting, running, clock, i, n, finished = [], [], 0.0, 0, len(reqs), 0
    while finished < n:
        while i < n and reqs[i]["arr"] <= clock:
            waiting.append(reqs[i]); i += 1
        if not waiting and not running:
            clock = max(clock, reqs[i]["arr"]); continue
        # admit
        budget = chunk_budget if chunk_budget else 10**9
        pf_tokens = 0
        for r in list(running):
            if r.get("pf_left", 0) > 0 and budget > 0:
                take = min(r["pf_left"], budget); r["pf_left"] -= take
                budget -= take; pf_tokens += take
        while waiting and len(running) < MAX_SEQS and budget > 0:
            r = waiting.pop(0); r["pf_left"] = r["prompt"]; r["gen"] = 0
            take = min(r["pf_left"], budget); r["pf_left"] -= take
            budget -= take; pf_tokens += take
            running.append(r)
        decoding = [r for r in running if r["pf_left"] == 0 and r["first"] is not None]
        starting = [r for r in running if r["pf_left"] == 0 and r["first"] is None]
        clock += C0 + C1 * len(decoding) + C2 * pf_tokens
        for r in starting:
            r["first"] = clock; r["gen"] = 1
        for r in decoding:
            r["gen"] += 1
        for r in list(running):
            if r["pf_left"] == 0 and r["gen"] >= r["out"]:
                r["done"] = clock; running.remove(r); finished += 1


def summarize(name, reqs):
    ttft = [r["first"] - r["arr"] for r in reqs]
    tpot = [(r["done"] - r["first"]) / max(1, r["out"] - 1) for r in reqs]
    e2e = [r["done"] - r["arr"] for r in reqs]
    horizon = max(r["done"] for r in reqs)
    toks = sum(r["out"] for r in reqs)
    good = sum(1 for a, b in zip(ttft, tpot) if a <= TTFT_SLO and b <= TPOT_SLO)
    q = lambda xs, p: sorted(xs)[min(len(xs) - 1, int(p * len(xs)))]
    print(f"{name:<22} TTFT p50 {q(ttft,.5):6.2f} p99 {q(ttft,.99):7.2f} | "
          f"TPOT p50 {q(tpot,.5)*1e3:5.1f} p99 {q(tpot,.99)*1e3:6.1f} ms | "
          f"E2E p99 {q(e2e,.99):7.1f} s | {toks/horizon:6.0f} tok/s | goodput {good/len(reqs):5.1%}")


def main():
    for rate in (1.0, 2.0, 3.0, 4.0):
        print(f"\n=== arrival rate {rate} req/s, 1,500 requests, max {MAX_SEQS} sequences ===")
        base = make_requests(1500, rate, seed=7)
        pols = [
            ("static B=32", lambda r: run_request_level(r, 32, float("inf"))),
            ("dynamic B=32 w=50ms", lambda r: run_request_level(r, 32, 0.05)),
            ("continuous", lambda r: run_continuous(r)),
            ("continuous+chunk 512", lambda r: run_continuous(r, 512)),
        ]
        for name, fn in pols:
            reqs = [dict(r) for r in base]
            fn(reqs)
            summarize(name, reqs)
    print("\n=== 2.0 req/s with 5% of prompts at 24,000 tokens (head-of-line blocking) ===")
    base = make_requests(1500, 2.0, seed=7, long_frac=0.05)
    for name, fn in [("continuous", lambda r: run_continuous(r)),
                     ("continuous+chunk 512", lambda r: run_continuous(r, 512)),
                     ("continuous+chunk 2048", lambda r: run_continuous(r, 2048))]:
        reqs = [dict(r) for r in base]
        fn(reqs)
        summarize(name, reqs)
    lens = make_requests(20000, 1.0, seed=1)
    print("\nworkload: mean prompt %.0f, mean output %.0f, max output %d" % (
        statistics.mean(r["prompt"] for r in lens), statistics.mean(r["out"] for r in lens),
        max(r["out"] for r in lens)))


if __name__ == "__main__":
    main()
