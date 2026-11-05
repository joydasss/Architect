"""Fluid simulation of retries, a circuit breaker, a fallback, and load shedding.

Standard library only. Time advances in 1-second ticks. Traffic is modelled as
expected values (no randomness), so output is deterministic.

Provider timeline (illustrative):
  ticks   0-29  healthy, capacity 150 calls/s
  ticks  30-59  outage, capacity 0
  ticks  60-89  recovering, capacity 70 calls/s (below the 100 requests/s demand)
  ticks 90-119  healthy, capacity 150

Clients send 100 requests/s. Three policies are compared:
  naive     : 3 attempts per request, no breaker, no fallback
  breaker   : 3 attempts, circuit breaker, fallback model (60 requests/s)
  protected : 2 attempts with a 10 percent retry budget, breaker, fallback
              model, and shedding of what the fallback cannot take
"""

DEMAND = 100.0
BASE_ERR = 0.01
FALLBACK_CAP = 60.0
PHASES = [("healthy", 0, 30), ("outage", 30, 60), ("recovering", 60, 90), ("healthy2", 90, 120)]


def provider_capacity(t: int) -> float:
    if 30 <= t < 60:
        return 0.0
    if 60 <= t < 90:
        return 70.0
    return 150.0


def call_success_prob(offered: float, cap: float) -> float:
    if offered <= 0:
        return 1.0
    return (1 - BASE_ERR) * min(1.0, cap / offered)


def run_closed(first: float, attempts: int, budget, cap: float):
    """Return (provider_calls, ok_requests, failed_requests, call_failure_rate)."""
    f = 0.5
    offered = first
    for _ in range(60):  # fixed point: offered load depends on f, f on offered load
        p = call_success_prob(offered, cap)
        f = 1 - p
        wanted = first * sum(f ** k for k in range(1, attempts))
        allowed = wanted if budget is None else min(wanted, budget * first)
        offered = first + allowed
    p = call_success_prob(offered, cap)
    f = 1 - p
    wanted = first * sum(f ** k for k in range(1, attempts))
    allowed = wanted if budget is None else min(wanted, budget * first)
    scale = 1.0 if wanted == 0 else allowed / wanted
    fail_all = first * f ** attempts
    failed = first * f - scale * (first * f - fail_all)
    return offered, first - failed, failed, f


class Breaker:
    def __init__(self, window=5, threshold=0.5, open_ticks=10):
        self.state = "closed"
        self.hist = []
        self.window, self.threshold, self.open_ticks = window, threshold, open_ticks
        self.opened_at = None

    def record(self, t, call_failure_rate):
        self.hist = (self.hist + [call_failure_rate])[-self.window:]
        if len(self.hist) == self.window and sum(self.hist) / self.window > self.threshold:
            self.state, self.opened_at, self.hist = "open", t, []

    def tick_open(self, t, provider_ok):
        if t - self.opened_at >= self.open_ticks:
            if provider_ok:        # one probe call decides
                self.state = "closed"
            else:
                self.opened_at = t
            return 1.0             # the probe call
        return 0.0


def simulate(name, attempts, budget, use_breaker, use_fallback, shed):
    br = Breaker()
    rows = {p[0]: dict(calls=0.0, ok=0.0, fb=0.0, shed=0.0, fail=0.0) for p in PHASES}
    transitions = []
    for t in range(120):
        phase = next(p[0] for p in PHASES if p[1] <= t < p[2])
        cap = provider_capacity(t)
        r = rows[phase]
        before = br.state
        if use_breaker and br.state == "open":
            probe = br.tick_open(t, provider_ok=cap >= DEMAND * 0.5)
            r["calls"] += probe
            overflow = DEMAND
        else:
            offered, ok, failed, f = run_closed(DEMAND, attempts, budget, cap)
            r["calls"] += offered
            r["ok"] += ok
            overflow = failed
            if use_breaker:
                br.record(t, f)
        if use_fallback:
            served = min(overflow, FALLBACK_CAP)
            r["fb"] += served
            overflow -= served
        if shed:
            r["shed"] += overflow
        else:
            r["fail"] += overflow
        if br.state != before:
            transitions.append((t, before, br.state))
    print(f"\n--- {name} ---")
    print("phase       provider_calls  ok_primary  ok_fallback   shed  failed")
    for ph, _, _ in PHASES:
        r = rows[ph]
        print(f"{ph:11s} {r['calls']:14.0f} {r['ok']:11.0f} {r['fb']:12.0f} {r['shed']:6.0f} {r['fail']:7.0f}")
    total_ok = sum(r["ok"] + r["fb"] for r in rows.values())
    total_calls = sum(r["calls"] for r in rows.values())
    print(f"usable outcomes: {total_ok / (DEMAND * 120) * 100:.1f} percent;"
          f" provider calls: {total_calls:.0f} (demand {DEMAND * 120:.0f})")
    if transitions:
        print("breaker transitions:", transitions)


if __name__ == "__main__":
    simulate("naive", 3, None, False, False, False)
    simulate("breaker", 3, None, True, True, False)
    simulate("protected", 2, 0.10, True, True, True)
