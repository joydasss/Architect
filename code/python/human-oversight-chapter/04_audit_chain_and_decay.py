"""Hash-chained review audit log and an oversight-decay detector.

Standard library only. The audit chain shows tamper evidence. The detector runs
an EWMA (exponentially weighted moving average) on override rate and flags a
sustained fall that coincides with shorter review times.
"""
import hashlib
import json
import random


def append(log, record):
    prev = log[-1]["hash"] if log else "0" * 64
    body = json.dumps(record, sort_keys=True)
    h = hashlib.sha256((prev + body).encode()).hexdigest()
    log.append({"record": record, "prev": prev, "hash": h})


def verify(log):
    prev = "0" * 64
    for i, e in enumerate(log):
        body = json.dumps(e["record"], sort_keys=True)
        if e["prev"] != prev or hashlib.sha256((prev + body).encode()).hexdigest() != e["hash"]:
            return i
        prev = e["hash"]
    return -1


def ewma_alerts(series, alpha=0.2, drop=0.4):
    """Flag days where the smoothed value falls below (1 - drop) x baseline."""
    base = sum(series[:14]) / 14
    s = base
    out = []
    for day, x in enumerate(series):
        s = alpha * x + (1 - alpha) * s
        if day >= 14 and s < (1 - drop) * base:
            out.append(day)
    return base, out


def main() -> None:
    log = []
    for i in range(3):
        append(log, {"case": f"C-{i}", "model": "m-2026-09", "prompt": "p-14",
                     "proposal": "approve", "reviewer": f"r{i}", "decision": "approve",
                     "reason": "evidence_ok", "ts": f"2026-10-01T09:0{i}:00Z"})
    print("Chain intact, first bad index:", verify(log))
    log[1]["record"]["decision"] = "reject"          # tamper with history
    print("After editing entry 1, first bad index:", verify(log))

    rng = random.Random(11)
    override, seconds = [], []
    for day in range(60):
        decay = 0.0 if day < 30 else min(1.0, (day - 30) / 20)
        override.append(max(0.0, rng.gauss(0.12 * (1 - 0.7 * decay), 0.015)))
        seconds.append(max(5.0, rng.gauss(80 - 45 * decay, 6)))
    base, alerts = ewma_alerts(override)
    print(f"\nBaseline override rate {base:.3f}")
    if alerts:
        d = alerts[0]
        print(f"First EWMA alert on day {d}; median review time days 0-29 "
              f"{sorted(seconds[:30])[15]:.0f}s, days {d - 9}-{d} "
              f"{sorted(seconds[d - 9:d + 1])[5]:.0f}s")
    else:
        print("No alert")


if __name__ == "__main__":
    main()
