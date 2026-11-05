"""Checkpoint, crash, and recovery with idempotency keys.

Standard library only. A fake payment service records side effects. A worker
crashes AFTER the service applied the refund but BEFORE the result was
checkpointed. Naive retry duplicates the refund. Recovery that reuses the
idempotency key (or reconciles first) applies it exactly once.
"""


class PaymentService:
    def __init__(self):
        self.applied = {}   # idempotency_key -> amount
        self.ledger = []    # every real money movement

    def refund(self, key, amount_cents, honor_key=True):
        if honor_key and key in self.applied:
            return {"status": "ok", "replayed": True}
        self.applied[key] = amount_cents
        self.ledger.append(amount_cents)
        return {"status": "ok", "replayed": False}

    def lookup(self, key):
        return self.applied.get(key)


class Crash(Exception):
    pass


def run_step(store, svc, run_id, step, amount, crash_after_effect, naive):
    """One executor step. store is the durable checkpoint table."""
    ck = store.get((run_id, step))
    if ck and ck["state"] == "done":
        return ck["result"]                      # replay-safe: skip finished step
    # Idempotency key is derived from run and step, persisted BEFORE the call.
    key = f"{run_id}:{step}" if not naive else f"attempt-{len(svc.ledger)}-{id(object())}"
    store[(run_id, step)] = {"state": "intent", "key": key}
    result = svc.refund(key, amount, honor_key=not naive)
    if crash_after_effect:
        raise Crash("worker lost after side effect")
    store[(run_id, step)] = {"state": "done", "key": key, "result": result}
    return result


def recover(store, svc, run_id, step, amount):
    ck = store.get((run_id, step))
    if ck and ck["state"] == "intent":
        known = svc.lookup(ck["key"])
        if known is not None:                   # reconcile: effect already happened
            store[(run_id, step)] = {"state": "done", "key": ck["key"],
                                     "result": {"status": "ok", "reconciled": True}}
            return "reconciled, no retry"
    return run_step(store, svc, run_id, step, amount, False, naive=False)


if __name__ == "__main__":
    # Case A: naive retry with a fresh key each time.
    svc, store = PaymentService(), {}
    try:
        run_step(store, svc, "run-1", 3, 4000, crash_after_effect=True, naive=True)
    except Crash:
        pass
    run_step(store, svc, "run-1", 3, 4000, crash_after_effect=False, naive=True)
    print("A naive retry         ledger:", svc.ledger, "total", sum(svc.ledger))

    # Case B: stable key, plain retry.
    svc, store = PaymentService(), {}
    try:
        run_step(store, svc, "run-2", 3, 4000, crash_after_effect=True, naive=False)
    except Crash:
        pass
    run_step(store, svc, "run-2", 3, 4000, crash_after_effect=False, naive=False)
    print("B stable key retry    ledger:", svc.ledger, "total", sum(svc.ledger))

    # Case C: recovery reconciles before retrying.
    svc, store = PaymentService(), {}
    try:
        run_step(store, svc, "run-3", 3, 4000, crash_after_effect=True, naive=False)
    except Crash:
        pass
    print("C recovery outcome    :", recover(store, svc, "run-3", 3, 4000))
    print("C reconcile ledger    :", svc.ledger, "total", sum(svc.ledger))

    # Case D: replay of a finished run performs no new effects.
    before = len(svc.ledger)
    run_step(store, svc, "run-3", 3, 4000, crash_after_effect=False, naive=False)
    print("D replay adds effects :", len(svc.ledger) - before)
