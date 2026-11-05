"""Tenant-isolation tests, hash-chained audit log, and exception state machine.

Standard library only. Run: python 03_tenant_isolation_audit_and_exceptions.py
"""
from __future__ import annotations

import hashlib
import json
from datetime import date, timedelta

# ---------- 1. Tenant-scoped retrieval and cache ----------
DOCS = [
    {"id": 1, "tenant": "a", "text": "refund policy for tenant a"},
    {"id": 2, "tenant": "b", "text": "refund policy for tenant b secret pricing"},
]


def search(query: str, tenant: str, filter_at_store: bool):
    words = set(query.lower().split())
    hits = [d for d in DOCS if words & set(d["text"].split())]
    if filter_at_store:
        hits = [d for d in hits if d["tenant"] == tenant]
    return hits


CACHE: dict = {}


def cached_answer(query: str, tenant: str, key_includes_tenant: bool):
    key = (tenant, query) if key_includes_tenant else query
    if key not in CACHE:
        CACHE[key] = [d["id"] for d in search(query, tenant, True)]
    return CACHE[key]


def isolation_tests():
    results = {}
    results["unfiltered search leaks"] = any(d["tenant"] != "a" for d in search("refund policy", "a", False))
    results["filtered search clean"] = all(d["tenant"] == "a" for d in search("refund policy", "a", True))
    CACHE.clear()
    cached_answer("secret pricing", "b", False)
    results["shared-key cache leaks to a"] = cached_answer("secret pricing", "a", False) == [2]
    CACHE.clear()
    cached_answer("secret pricing", "b", True)
    results["tenant-keyed cache clean"] = cached_answer("secret pricing", "a", True) == []
    return results


# ---------- 2. Hash-chained audit log ----------
class AuditLog:
    def __init__(self):
        self.entries = []

    def append(self, event: dict):
        prev = self.entries[-1]["hash"] if self.entries else "0" * 64
        body = json.dumps(event, sort_keys=True)
        h = hashlib.sha256((prev + body).encode()).hexdigest()
        self.entries.append({"event": event, "prev": prev, "hash": h})

    def verify(self) -> int:
        """Return index of first bad entry, or -1 if chain is intact."""
        prev = "0" * 64
        for i, e in enumerate(self.entries):
            body = json.dumps(e["event"], sort_keys=True)
            if e["prev"] != prev or hashlib.sha256((prev + body).encode()).hexdigest() != e["hash"]:
                return i
            prev = e["hash"]
        return -1


# ---------- 3. Exception lifecycle state machine ----------
TRANSITIONS = {
    ("requested", "approve"): "active",
    ("requested", "reject"): "rejected",
    ("active", "expire"): "expired",
    ("active", "revoke"): "revoked",
    ("active", "review_renew"): "active",
}


class PolicyException:
    def __init__(self, control: str, granted: date, days: int):
        self.control, self.state = control, "requested"
        self.expires = granted + timedelta(days=days)

    def fire(self, event: str, today: date):
        nxt = TRANSITIONS.get((self.state, event))
        if nxt is None:
            raise ValueError(f"illegal {event} from {self.state}")
        if event == "review_renew":
            self.expires = today + timedelta(days=30)
        self.state = nxt

    def tick(self, today: date):
        if self.state == "active" and today > self.expires:
            self.fire("expire", today)


if __name__ == "__main__":
    for name, ok in isolation_tests().items():
        print(f"{name:32} {ok}")

    log = AuditLog()
    for i in range(4):
        log.append({"seq": i, "actor": "svc-agent", "tool": "search_kb", "decision": "allow"})
    print("chain verify (intact):", log.verify())
    log.entries[2]["event"]["decision"] = "deny"
    print("chain verify (tampered):", log.verify())

    d0 = date(2026, 10, 1)
    ex = PolicyException("egress-allowlist-bypass", d0, 14)
    ex.fire("approve", d0)
    ex.tick(d0 + timedelta(days=10))
    print("day 10:", ex.state)
    ex.tick(d0 + timedelta(days=15))
    print("day 15:", ex.state)
    try:
        ex.fire("approve", d0)
    except ValueError as e:
        print("error:", e)
