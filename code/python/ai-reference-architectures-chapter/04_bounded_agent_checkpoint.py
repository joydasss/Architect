"""Bounded agent executor with budgets, idempotency keys, and checkpoint/resume.

Standard library only. The "planner" is a scripted stub standing in for a model.
Shows: allow-listed tools, step budget, idempotent side effects, and resuming
after a crash without repeating the refund-preparation action.
"""
import json

ALLOWED = {"lookup_order", "prepare_case"}          # no direct refund tool
SIDE_EFFECTS = []                                    # stands in for external system
SEEN_KEYS = set()                                    # idempotency ledger (durable in real life)


def tool(name, args, run_id, step):
    if name not in ALLOWED:
        raise PermissionError(f"tool {name} not allowed")
    key = f"{run_id}:{step}:{name}"
    if name == "prepare_case":
        if key in SEEN_KEYS:
            return {"status": "duplicate_suppressed"}
        SEEN_KEYS.add(key)
        SIDE_EFFECTS.append((key, args))
        return {"status": "case_created"}
    return {"order": args["id"], "state": "delivered", "days_since": 12}


PLAN = [("lookup_order", {"id": "o-9"}), ("prepare_case", {"id": "o-9", "reason": "late"}),
        ("finish", {})]


def run(checkpoint, crash_after=None, max_steps=5):
    state = dict(checkpoint)
    while state["step"] < max_steps:
        name, args = PLAN[state["step"]]
        if name == "finish":
            state["status"] = "completed"
            return state
        result = tool(name, args, state["run_id"], state["step"])
        state["log"].append((name, result["status"] if "status" in result else "ok"))
        state["step"] += 1
        if crash_after is not None and state["step"] == crash_after:
            raise RuntimeError("worker crashed after tool call, before checkpoint save")
    state["status"] = "budget_exhausted"
    return state


saved = {"run_id": "r1", "step": 0, "log": [], "status": "running"}
try:
    run(saved, crash_after=2)
except RuntimeError as e:
    print("crash:", e)
# Last durable checkpoint is step 1 (the crash lost the step-2 save), so resume replays prepare_case.
saved["step"] = 1
final = run(saved)
print("final status:", final["status"])
print("log:", json.dumps(final["log"]))
print("external side effects:", len(SIDE_EFFECTS))
try:
    tool("issue_refund", {}, "r1", 9)
except PermissionError as e:
    print("blocked:", e)
