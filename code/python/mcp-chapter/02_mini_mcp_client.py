"""Teaching MCP-style client: launches 01_mini_mcp_server.py over stdio.

Teaching implementation, not the official SDK. Demonstrates:
1. legacy handshake (initialize, notifications/initialized, tools/list)
2. modern stateless calls with per-request _meta and server/discover
3. tool execution error (isError) vs protocol error (JSON-RPC error)
4. idempotent retry and cursor pagination
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(HERE, "01_mini_mcp_server.py")


class Client:
    def __init__(self):
        self.p = subprocess.Popen([sys.executable, SERVER], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                  text=True, bufsize=1)
        self.next_id = 1

    def send(self, method, params=None, notify=False):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        if not notify:
            msg["id"] = self.next_id
            self.next_id += 1
        self.p.stdin.write(json.dumps(msg) + "\n")
        self.p.stdin.flush()
        if notify:
            return None
        return json.loads(self.p.stdout.readline())

    def close(self):
        self.p.stdin.close()  # closing stdin is the shutdown signal
        return self.p.wait(timeout=5)


def show(label, obj):
    print(f"{label}: {json.dumps(obj, sort_keys=True)}")


def legacy_session():
    print("== legacy era ==")
    c = Client()
    show("initialize", c.send("initialize", {"protocolVersion": "2025-11-25", "capabilities": {},
                                              "clientInfo": {"name": "teach-client", "version": "0.1"}}))
    c.send("notifications/initialized", notify=True)
    r = c.send("tools/list")
    print("tools:", [t["name"] for t in r["result"]["tools"]])
    print("exit code on stdin close:", c.close())


def modern_session():
    print("== modern era ==")
    c = Client()
    meta = {"io.modelcontextprotocol/protocolVersion": "2026-07-28"}
    show("discover", c.send("server/discover", {"_meta": meta}))
    bad = c.send("tools/list", {"_meta": {"io.modelcontextprotocol/protocolVersion": "1999-01-01"}})
    show("bad version", bad)
    page1 = c.send("tools/call", {"_meta": meta, "name": "tickets.search",
                                  "arguments": {"status": "open", "limit": 1}})
    out1 = page1["result"]["structuredContent"]
    show("page1", out1)
    page2 = c.send("tools/call", {"_meta": meta, "name": "tickets.search",
                                  "arguments": {"status": "open", "limit": 1, "cursor": out1["nextCursor"]}})
    show("page2", page2["result"]["structuredContent"])
    invalid = c.send("tools/call", {"_meta": meta, "name": "tickets.search",
                                    "arguments": {"status": "pending"}})
    show("tool error", {"isError": invalid["result"]["isError"], "text": invalid["result"]["content"][0]["text"]})
    unknown = c.send("tools/call", {"_meta": meta, "name": "tickets.delete", "arguments": {}})
    show("protocol error", unknown["error"])
    args = {"ticketId": "T-100", "text": "Rebooted router", "idempotencyKey": "k1"}
    first = c.send("tools/call", {"_meta": meta, "name": "tickets.comment", "arguments": args})
    retry = c.send("tools/call", {"_meta": meta, "name": "tickets.comment", "arguments": args})
    show("comment first", first["result"]["structuredContent"])
    show("comment retry", retry["result"]["structuredContent"])
    print("exit code on stdin close:", c.close())


if __name__ == "__main__":
    legacy_session()
    modern_session()
