"""Teaching MCP-style server over stdio (standard library only).

NOT the official SDK and NOT a conformant implementation. It follows the
message SHAPES of the Model Context Protocol (JSON-RPC 2.0, newline-delimited
on stdin/stdout) so the wire format can be inspected. It serves two eras:

* legacy (2025-11-25 style): `initialize` -> result, `notifications/initialized`
* modern (2026-07-28 style): no handshake, per-request `_meta` carrying the
  protocol version, plus `server/discover`.

Run directly to act as a server: `python 01_mini_mcp_server.py`.
The client in 02_mini_mcp_client.py launches it as a subprocess.
"""
import json
import sys

LEGACY = "2025-11-25"
MODERN = "2026-07-28"
SUPPORTED = [MODERN, LEGACY]
META_VERSION = "io.modelcontextprotocol/protocolVersion"

TICKETS = {
    "T-100": {"id": "T-100", "title": "VPN drops hourly", "status": "open", "owner": "ana"},
    "T-101": {"id": "T-101", "title": "Laptop refresh", "status": "closed", "owner": "bo"},
    "T-102": {"id": "T-102", "title": "Printer jam floor 3", "status": "open", "owner": "ana"},
}
IDEMPOTENCY = {}

TOOLS = [
    {
        "name": "tickets.search",
        "title": "Search tickets",
        "description": "Find tickets by status. Returns at most `limit` tickets (default 2) "
                       "and a `nextCursor` when more exist. Read-only.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["open", "closed"]},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50},
                "cursor": {"type": "string"},
            },
            "required": ["status"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": True, "idempotentHint": True},
    },
    {
        "name": "tickets.comment",
        "title": "Comment on a ticket",
        "description": "Add a comment to a ticket. Pass the same idempotencyKey on retry to avoid duplicates.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticketId": {"type": "string", "pattern": "^T-[0-9]+$"},
                "text": {"type": "string", "maxLength": 500},
                "idempotencyKey": {"type": "string"},
            },
            "required": ["ticketId", "text", "idempotencyKey"],
            "additionalProperties": False,
        },
        "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True},
    },
]


def ok(rid, result):
    return {"jsonrpc": "2.0", "id": rid, "result": result}


def err(rid, code, message, data=None):
    e = {"code": code, "message": message}
    if data is not None:
        e["data"] = data
    return {"jsonrpc": "2.0", "id": rid, "error": e}


def validate(args, schema):
    """Tiny schema check: required, additionalProperties, type, enum, bounds, pattern."""
    import re
    problems = []
    props = schema.get("properties", {})
    for r in schema.get("required", []):
        if r not in args:
            problems.append(f"missing required '{r}'")
    for k, v in args.items():
        if k not in props:
            if schema.get("additionalProperties") is False:
                problems.append(f"unexpected '{k}'")
            continue
        p = props[k]
        t = p.get("type")
        if t == "string" and not isinstance(v, str):
            problems.append(f"'{k}' must be string")
        if t == "integer" and (not isinstance(v, int) or isinstance(v, bool)):
            problems.append(f"'{k}' must be integer")
        if "enum" in p and v not in p["enum"]:
            problems.append(f"'{k}' must be one of {p['enum']}")
        if isinstance(v, int) and not isinstance(v, bool):
            if "minimum" in p and v < p["minimum"]:
                problems.append(f"'{k}' below minimum {p['minimum']}")
            if "maximum" in p and v > p["maximum"]:
                problems.append(f"'{k}' above maximum {p['maximum']}")
        if isinstance(v, str):
            if "maxLength" in p and len(v) > p["maxLength"]:
                problems.append(f"'{k}' longer than {p['maxLength']}")
            if "pattern" in p and not re.match(p["pattern"], v):
                problems.append(f"'{k}' does not match {p['pattern']}")
    return problems


def tool_result(text, structured=None, is_error=False):
    r = {"content": [{"type": "text", "text": text}], "isError": is_error, "resultType": "complete"}
    if structured is not None:
        r["structuredContent"] = structured
    return r


def call_tool(name, args):
    tool = next((t for t in TOOLS if t["name"] == name), None)
    if tool is None:
        return None
    problems = validate(args, tool["inputSchema"])
    if problems:
        return tool_result("Invalid arguments: " + "; ".join(problems), is_error=True)
    if name == "tickets.search":
        rows = sorted((t for t in TICKETS.values() if t["status"] == args["status"]), key=lambda t: t["id"])
        start = int(args.get("cursor", "0"))
        limit = args.get("limit", 2)
        page = rows[start:start + limit]
        out = {"tickets": page}
        if start + limit < len(rows):
            out["nextCursor"] = str(start + limit)
        return tool_result(json.dumps(out), structured=out)
    if name == "tickets.comment":
        key = (args["ticketId"], args["idempotencyKey"])
        if args["ticketId"] not in TICKETS:
            return tool_result(f"Ticket {args['ticketId']} not found. Use tickets.search to list ids.", is_error=True)
        if key in IDEMPOTENCY:
            out = dict(IDEMPOTENCY[key], deduplicated=True)
        else:
            out = {"commentId": f"C-{len(IDEMPOTENCY) + 1}", "ticketId": args["ticketId"], "deduplicated": False}
            IDEMPOTENCY[key] = out
        return tool_result(json.dumps(out), structured=out)


def handle(msg, state):
    """Return a response dict, or None for notifications."""
    rid = msg.get("id")
    method = msg.get("method")
    params = msg.get("params") or {}
    if method is None:
        return err(rid, -32600, "Invalid Request")
    if rid is None:  # notification: never answered
        if method == "notifications/initialized":
            state["initialized"] = True
        return None
    meta = params.get("_meta", {})
    if method == "initialize":  # legacy era
        wanted = params.get("protocolVersion")
        chosen = wanted if wanted in SUPPORTED else LEGACY
        state["legacy"] = True
        return ok(rid, {"protocolVersion": chosen,
                        "capabilities": {"tools": {"listChanged": False}},
                        "serverInfo": {"name": "mini-tickets", "version": "0.1.0"}})
    if method == "server/discover":
        return ok(rid, {"supportedVersions": SUPPORTED,
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "mini-tickets", "version": "0.1.0"},
                        "resultType": "complete"})
    if not state.get("legacy"):  # modern era: version travels on every request
        v = meta.get(META_VERSION)
        if v not in SUPPORTED:
            return err(rid, -32022, "Unsupported protocol version", {"supported": SUPPORTED})
    elif not state.get("initialized"):
        return err(rid, -32600, "Not initialized")
    if method == "tools/list":
        return ok(rid, {"tools": TOOLS, "resultType": "complete"})
    if method == "tools/call":
        result = call_tool(params.get("name"), params.get("arguments") or {})
        if result is None:
            return err(rid, -32602, f"Unknown tool: {params.get('name')}")
        return ok(rid, result)
    return err(rid, -32601, f"Method not found: {method}")


def main():
    state = {}
    for line in sys.stdin:  # EOF on stdin is the shutdown signal
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            sys.stdout.write(json.dumps(err(None, -32700, "Parse error")) + "\n")
            sys.stdout.flush()
            continue
        print(f"[server] <- {msg.get('method')}", file=sys.stderr)  # logs go to stderr only
        resp = handle(msg, state)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
