"""Executor with a policy decision point, risk tiers, and digest-bound approval.

Standard library only. The "planner" is a fixed list of proposals standing in
for model output. The executor never trusts a proposal: it validates the tool
name and arguments, evaluates policy (deny by default), and for consequential
tiers requires an approval bound to the SHA-256 digest of the canonical call.
"""

import hashlib
import json
import time
from dataclasses import dataclass

# Tool registry: owner, risk tier, argument schema (name -> type).
REGISTRY = {
    "get_order": {"tier": "read", "schema": {"order_id": str}},
    "add_note": {"tier": "write_reversible", "schema": {"order_id": str, "text": str}},
    "refund": {"tier": "financial", "schema": {"order_id": str, "amount_cents": int}},
    "send_email": {"tier": "external_comm", "schema": {"to": str, "body": str}},
}

# Policy as data: which tiers a role may use, and which need approval.
ROLE_TIERS = {
    "agent_support": {"read", "write_reversible", "financial"},
}
APPROVAL_TIERS = {"financial", "external_comm", "write_irreversible"}
AUTO_REFUND_LIMIT_CENTS = 5_000  # refunds up to $50.00 skip approval


@dataclass
class Context:
    user: str
    tenant: str
    role: str
    order_tenant: dict  # order_id -> tenant that owns it


def digest(tool, args):
    canonical = json.dumps({"tool": tool, "args": args}, sort_keys=True,
                           separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def validate(tool, args):
    spec = REGISTRY.get(tool)
    if spec is None:
        return "unknown tool"
    if set(args) != set(spec["schema"]):
        return "argument names do not match schema"
    for k, t in spec["schema"].items():
        if not isinstance(args[k], t) or isinstance(args[k], bool):
            return f"argument {k} has wrong type"
    return None


def decide(ctx, tool, args):
    """Policy decision point. Returns (decision, reason)."""
    err = validate(tool, args)
    if err:
        return "deny", err
    tier = REGISTRY[tool]["tier"]
    if tier not in ROLE_TIERS.get(ctx.role, set()):
        return "deny", f"role {ctx.role} lacks tier {tier}"
    oid = args.get("order_id")
    if oid is not None and ctx.order_tenant.get(oid) != ctx.tenant:
        return "deny", "resource outside caller tenant"
    if tool == "refund":
        if args["amount_cents"] <= 0:
            return "deny", "non-positive amount"
        if args["amount_cents"] > AUTO_REFUND_LIMIT_CENTS:
            return "needs_approval", "refund above auto limit"
        return "allow", "refund within auto limit"
    if tier in APPROVAL_TIERS:
        return "needs_approval", f"tier {tier} requires approval"
    return "allow", f"tier {tier} permitted"


class Approvals:
    def __init__(self):
        self.grants = {}  # digest -> (approver, expires_at)

    def grant(self, tool, args, approver, ttl_s, now):
        self.grants[digest(tool, args)] = (approver, now + ttl_s)

    def check(self, tool, args, now):
        g = self.grants.get(digest(tool, args))
        if g is None:
            return False
        return now <= g[1]


def execute(ctx, tool, args, approvals, now):
    decision, reason = decide(ctx, tool, args)
    if decision == "needs_approval":
        if approvals.check(tool, args, now):
            return "executed", "approved digest " + digest(tool, args)
        return "pending", f"{reason}; digest {digest(tool, args)}"
    if decision == "allow":
        return "executed", reason
    return "denied", reason


if __name__ == "__main__":
    ctx = Context("alice", "t1", "agent_support",
                  {"o-1": "t1", "o-2": "t1", "o-9": "t2"})
    ap = Approvals()
    now = 1_000.0
    proposals = [
        ("get_order", {"order_id": "o-1"}),
        ("get_order", {"order_id": "o-9"}),
        ("refund", {"order_id": "o-1", "amount_cents": 4000}),
        ("refund", {"order_id": "o-1", "amount_cents": 12000}),
        ("send_email", {"to": "x@example.com", "body": "hi"}),
        ("run_shell", {"cmd": "ls"}),
        ("refund", {"order_id": "o-1", "amount_cents": "12000"}),
    ]
    for tool, args in proposals:
        print(f"{tool:11s} {json.dumps(args):52s} -> {execute(ctx, tool, args, ap, now)}")

    print("--- approval bound to digest ---")
    ap.grant("refund", {"order_id": "o-1", "amount_cents": 12000}, "mgr_bob", 300, now)
    print("same args, inside expiry   :",
          execute(ctx, "refund", {"order_id": "o-1", "amount_cents": 12000}, ap, now + 100))
    print("changed amount             :",
          execute(ctx, "refund", {"order_id": "o-1", "amount_cents": 12001}, ap, now + 100))
    print("same args, after expiry    :",
          execute(ctx, "refund", {"order_id": "o-1", "amount_cents": 12000}, ap, now + 400))
