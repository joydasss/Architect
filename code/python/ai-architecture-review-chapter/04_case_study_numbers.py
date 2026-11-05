"""Worked numbers for the five case studies in the chapter (all illustrative).

Standard library only. Run: python 04_case_study_numbers.py
Prices are placeholders, not any provider's price list. Replace them with
current published prices before using the arithmetic for a real decision.
"""


def case1_rag_leak():
    queries = 120_000
    hit_rate = 0.22
    hits = queries * hit_rate
    cross_tenant_share = 0.003
    leaks = hits * cross_tenant_share
    probes, probe_leaks = 2_000, 3
    print("CASE 1 support RAG")
    print(f"  cache hits/month = {queries} x {hit_rate} = {hits:.0f}")
    print(f"  at {cross_tenant_share:.1%} cross-tenant share -> {leaks:.0f} exposures/month")
    print(f"  canary probes: {probe_leaks}/{probes} = {probe_leaks / probes:.2%} leak rate")


def case2_fraud():
    tx_per_day = 2_000_000
    fraud_rate = 0.002
    fraud = tx_per_day * fraud_rate
    r_before, r_after = 0.80, 0.68
    missed_extra = fraud * (r_before - r_after)
    avg_loss = 140
    daily = missed_extra * avg_loss
    delay_days = 30
    print("CASE 2 fraud")
    print(f"  fraud/day = {tx_per_day} x {fraud_rate} = {fraud:.0f}")
    print(f"  extra missed/day = {fraud:.0f} x ({r_before} - {r_after}) = {missed_extra:.0f}")
    print(f"  extra loss/day = {missed_extra:.0f} x ${avg_loss} = ${daily:,.0f}")
    print(f"  undetected for {delay_days} days = ${daily * delay_days:,.0f}")
    alerts, reviewers_cap = 9_000, 7_500
    print(f"  alert backlog growth = {alerts} - {reviewers_cap} = {alerts - reviewers_cap}/day")


def case3_agent():
    iters = 3_000
    in_tok, out_tok = 9_000, 400
    p_in, p_out = 3.0, 15.0  # $ per million tokens, illustrative
    per_iter = in_tok / 1e6 * p_in + out_tok / 1e6 * p_out
    print("CASE 3 IT-ops agent")
    print(f"  cost/iteration = {in_tok}/1e6 x {p_in} + {out_tok}/1e6 x {p_out} = ${per_iter:.3f}")
    print(f"  runaway {iters} iterations = ${iters * per_iter:,.0f}")
    nodes, safe_fraction = 14, 0.10
    print(f"  nodes restarted at once = {nodes}; policy cap {safe_fraction:.0%} of 40 = {int(40 * safe_fraction)}")


def case4_claims():
    claims, pages_per = 30_000, 12
    pages = claims * pages_per
    ocr_per_1k = 1.50
    p_in, p_out = 1.0, 4.0
    tin, tout = 3_000, 500
    small = tin / 1e6 * p_in + tout / 1e6 * p_out
    big = 10 * small
    ocr = pages / 1000 * ocr_per_1k
    budget = ocr + pages * small
    redo_planned, redo_actual = 0.08, 0.35
    planned = budget + pages * redo_planned * big
    actual = budget + pages * redo_actual * big
    print("CASE 4 claims pipeline")
    print(f"  pages = {claims} x {pages_per} = {pages}")
    print(f"  OCR = {pages}/1000 x ${ocr_per_1k} = ${ocr:,.0f}")
    print(f"  small-model extract = {pages} x ${small:.4f} = ${pages * small:,.0f}")
    print(f"  planned total (8% escalate to big model at ${big:.3f}/page) = ${planned:,.0f}")
    print(f"  actual total (35% escalate) = ${actual:,.0f}  ratio {actual / planned:.2f}x")
    review = 0.12 * claims
    mins = 6
    print(f"  human review = {review:.0f} claims x {mins} min = {review * mins / 60:.0f} h/month")


def case5_voice():
    parts = {"endpointing": 250, "streaming ASR final": 150, "LLM first token": 450,
             "TTS first audio": 200, "network and telephony": 100}
    total = sum(parts.values())
    print("CASE 5 voice assistant")
    for k, v in parts.items():
        print(f"  {k:<24}{v:>5} ms")
    print(f"  sum = {total} ms (target 1200 ms, headroom {1200 - total} ms)")
    calls_per_hour, outage_min = 1_800, 47
    calls = calls_per_hour * outage_min / 60
    print(f"  calls during outage = {calls_per_hour} x {outage_min}/60 = {calls:.0f}")
    print(f"  if 60% fall back to menu IVR, 40% abandon-risk = {calls * 0.4:.0f} calls")


def extras():
    print("EXTRAS (cost of fixes)")
    per_q = 3500 / 1e6 * 3.0 + 350 / 1e6 * 15.0
    v1 = 120_000 * 0.78 * per_q
    v2 = 120_000 * 0.86 * per_q
    print(f"  case1 cost/query ${per_q:.5f}; v1 ${v1:,.0f}; v2 ${v2:,.0f}; delta ${v2 - v1:,.0f}")
    pages = 360_000
    small, big = 0.005, 0.05
    redo = pages * 0.15 * (0.2 * big)
    total = pages / 1000 * 1.5 + pages * small + redo
    print(f"  case4 redesign escalation ${redo:,.0f}; total ${total:,.0f}; vs plan {total / 3780:.3f}; vs incident {total / 8640:.3f}")
    call = 4.5 * 0.01 + 2 * 0.02 + (24_000 / 1e6 * 0.5 + 960 / 1e6 * 2) + 4.5 * 0.008
    month = 250_000 * call
    saved = 250_000 * 0.35 * 4.5 * 0.75
    print(f"  case5 cost/call ${call:.5f}; month ${month:,.0f}; saved ${saved:,.2f}; net ${saved - month:,.2f}")
    print(f"  case5 p95 approx (median LLM p95 900) = {700 + 900}; routine tier = {650 + 520}")


if __name__ == "__main__":
    extras()
    print()
    for f in (case1_rag_leak, case2_fraud, case3_agent, case4_claims, case5_voice):
        f()
        print()
