"""Retry amplification, error-budget burn rate, and token-bucket arithmetic.

Standard library only. Every number printed is reproduced in the chapter.
"""


def retry_amplification(layers: int, attempts: int, failure_rate: float):
    """Worst-case and expected calls reaching the provider per user request.

    Worst case: every attempt at every layer fails, so calls = attempts ** layers.
    Expected: if each call fails independently with probability f, each layer
    makes on average (1 - f**a) / (1 - f) attempts per upstream call.
    """
    worst = attempts ** layers
    per_layer = (1 - failure_rate ** attempts) / (1 - failure_rate) if failure_rate < 1 else attempts
    expected = per_layer ** layers
    return worst, expected


def burn_rate(error_rate: float, slo: float) -> float:
    return error_rate / (1 - slo)


def combined_bad_fraction(hard_fail: float, quality_fail_given_ok: float) -> float:
    """Fraction of requests that are bad: hard failure or low quality."""
    return hard_fail + (1 - hard_fail) * quality_fail_given_ok


def token_bucket_refill_wait(capacity, refill_per_s, tokens, cost):
    if tokens >= cost:
        return 0.0
    return (cost - tokens) / refill_per_s


if __name__ == "__main__":
    print("== retry amplification (3 layers x 3 attempts) ==")
    for f in (0.1, 0.5, 1.0):
        worst, exp = retry_amplification(3, 3, f)
        print(f"failure rate {f:.1f}: worst={worst} calls, expected={exp:.2f} calls per request")

    print("\n== retry budget (10 percent of first-attempt traffic) ==")
    rps = 100
    budget = 0.10
    print(f"first attempts {rps}/s, allowed retries {rps * budget:.0f}/s, "
          f"max provider load {rps * (1 + budget):.0f}/s")

    print("\n== burn rate, 99.9 percent SLO over 30 days ==")
    slo = 0.999
    total_minutes = 30 * 24 * 60
    print(f"error budget = {(1 - slo) * 100:.1f} percent = {total_minutes * (1 - slo):.1f} minutes of full outage")
    for label, err in (("hard failures 0.4 percent", 0.004), ("hard failures 1.5 percent", 0.015)):
        br = burn_rate(err, slo)
        print(f"{label}: burn rate {br:.1f}x, budget gone in {30 / br:.1f} days")
    fast = 14.4
    print(f"fast-burn page threshold {fast}x over 1 h spends {fast * 1 / (30 * 24) * 100:.1f} percent of the monthly budget")

    print("\n== combined hard and quality failures ==")
    hard = 0.002
    q = 0.006
    bad = combined_bad_fraction(hard, q)
    print(f"hard {hard:.3f}, quality-fail-given-ok {q:.3f} -> bad fraction {bad:.5f}")
    print(f"burn rate against 99.9 percent: {burn_rate(bad, slo):.2f}x")
    print(f"availability of a usable outcome: {(1 - bad) * 100:.3f} percent")

    print("\n== token bucket (tokens per minute limit) ==")
    capacity = 60_000
    refill = 60_000 / 60.0   # tokens per second
    print(f"capacity {capacity}, refill {refill:.0f} tokens/s")
    for tokens, cost in ((60_000, 8_000), (3_000, 8_000), (0, 8_000)):
        wait = token_bucket_refill_wait(capacity, refill, tokens, cost)
        print(f"tokens={tokens:6d}, request cost={cost}: wait {wait:.1f} s")
    est_in, max_out = 3_000, 4_000
    print(f"admission estimate: input {est_in} + max_output {max_out} = {est_in + max_out} tokens reserved,"
          f" refund difference when actual output is 600: {max_out - 600} tokens")
    print("sustained request rate at 1,500 tokens each:",
          f"{refill / 1500 * 60:.0f} requests per minute")
