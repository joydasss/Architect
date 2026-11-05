"""Minimal agent loop with a scripted mock model (standard library only).

The "model" replays a fixed script of proposals, so the run is deterministic.
The loop validates arguments against a schema, enforces step and tool-call
budgets, detects repeated calls, returns errors the model can act on, and
records a trace.

Run: python 01_agent_loop.py
"""
import json

# ---------------------------------------------------------------- tools
ORDERS = {"A-100": {"status": "shipped", "total": 42.5}, "A-200": {"status": "delivered", "total": 80.0}}

SCHEMAS = {
    "get_order": {"required": {"order_id": str}},
    "refund_order": {"required": {"order_id": str, "amount": float, "idempotency_key": str}},
}


def get_order(order_id):
    if order_id not in ORDERS:
        return {"error": "not_found", "hint": "order ids look like A-123; ask the user to confirm the id"}
    return {"order": ORDERS[order_id]}


REFUNDS = {}


def refund_order(order_id, amount, idempotency_key):
    if idempotency_key in REFUNDS:  # replay returns the stored result, no second refund
        return {"refund": REFUNDS[idempotency_key], "replayed": True}
    if order_id not in ORDERS:
        return {"error": "not_found", "hint": "call get_order first"}
    if amount > ORDERS[order_id]["total"]:
        return {"error": "amount_exceeds_total", "hint": "maximum refundable is %.2f" % ORDERS[order_id]["total"]}
    REFUNDS[idempotency_key] = {"order_id": order_id, "amount": amount}
    return {"refund": REFUNDS[idempotency_key], "replayed": False}


TOOLS = {"get_order": get_order, "refund_order": refund_order}


def validate(name, args):
    """Return None if valid, else an error dict the model can act on."""
    if name not in SCHEMAS:
        return {"error": "unknown_tool", "hint": "available: " + ", ".join(sorted(SCHEMAS))}
    spec = SCHEMAS[name]["required"]
    for key, typ in spec.items():
        if key not in args:
            return {"error": "missing_argument", "hint": "argument '%s' is required" % key}
        if not isinstance(args[key], typ):
            return {"error": "bad_type", "hint": "argument '%s' must be %s" % (key, typ.__name__)}
    extra = set(args) - set(spec)
    if extra:
        return {"error": "unexpected_argument", "hint": "remove: " + ", ".join(sorted(extra))}
    return None


# ---------------------------------------------------------------- mock model
SCRIPT = [
    {"tool": "get_order", "args": {"order_id": "A-1OO"}},          # typo: letter O
    {"tool": "get_order", "args": {"order_id": "A-100"}},          # recovers from the hint
    {"tool": "refund_order", "args": {"order_id": "A-100", "amount": "42.5", "idempotency_key": "r-1"}},  # bad type
    {"tool": "refund_order", "args": {"order_id": "A-100", "amount": 42.5, "idempotency_key": "r-1"}},
    {"tool": "refund_order", "args": {"order_id": "A-100", "amount": 42.5, "idempotency_key": "r-1"}},    # repeat
    {"final": "Refunded 42.50 for order A-100."},
]


class ScriptedModel:
    def __init__(self, script):
        self.script = list(script)
        self.i = 0

    def next(self, messages):
        proposal = self.script[min(self.i, len(self.script) - 1)]
        self.i += 1
        return proposal


# ---------------------------------------------------------------- loop
def run(model, goal, max_steps=8, max_tool_calls=6, repeat_window=3):
    messages = [{"role": "user", "content": goal}]
    trace, recent, tool_calls = [], [], 0
    for step in range(1, max_steps + 1):
        proposal = model.next(messages)
        if "final" in proposal:
            trace.append((step, "final", proposal["final"]))
            return {"status": "done", "answer": proposal["final"], "steps": step, "trace": trace}
        name, args = proposal["tool"], proposal["args"]
        key = name + json.dumps(args, sort_keys=True)
        if key in recent[-repeat_window:]:
            obs = {"error": "repeated_call", "hint": "this exact call already ran; choose a different step or finish"}
            trace.append((step, name, "BLOCKED repeat"))
        else:
            err = validate(name, args)
            if err:
                obs = err
                trace.append((step, name, "invalid: " + err["error"]))
            elif tool_calls >= max_tool_calls:
                return {"status": "budget_exhausted", "steps": step, "trace": trace}
            else:
                tool_calls += 1
                obs = TOOLS[name](**args)
                trace.append((step, name, "error: " + obs["error"] if "error" in obs else "ok"))
        recent.append(key)
        messages.append({"role": "tool", "name": name, "content": json.dumps(obs)})
    return {"status": "step_limit", "steps": max_steps, "trace": trace}


if __name__ == "__main__":
    result = run(ScriptedModel(SCRIPT), "Refund order A-100 in full")
    for row in result["trace"]:
        print("step %d  %-13s %s" % row)
    print("status:", result["status"], "| steps:", result["steps"])
    print("refunds recorded:", REFUNDS)
    tight = run(ScriptedModel(SCRIPT), "Refund order A-100 in full", max_steps=3)
    print("with max_steps=3 ->", tight["status"])
