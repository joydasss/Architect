"""Provider adapter (anti-corruption layer) with record/replay and contract tests.
Standard library only.

Two fake vendor wire formats (shaped like an OpenAI-style chat response and an
Anthropic-style messages response, simplified and ILLUSTRATIVE, not the real
schemas) are mapped by adapters into one normalized Completion. The same contract
test suite runs against both adapters. A cassette (recorded request/response
pairs keyed by a hash of the canonical request) lets tests replay without a
network and detects request drift when the hash changes.

Run: python 04_record_replay_contract.py
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field


@dataclass
class Completion:
    text: str
    tool_calls: list = field(default_factory=list)  # list of (name, arguments dict)
    input_tokens: int = 0
    output_tokens: int = 0
    finish: str = "stop"  # normalized: stop | length | tool_use | refusal


# ---- fake vendor transports (return raw vendor-shaped dicts) ----
def vendor_a_transport(req: dict) -> dict:
    last = req["messages"][-1]["content"]
    if "weather" in last:
        return {"choices": [{"finish_reason": "tool_calls", "message": {"content": None, "tool_calls": [
            {"function": {"name": "get_weather", "arguments": '{"city": "Oslo"}'}}]}}],
            "usage": {"prompt_tokens": 40, "completion_tokens": 9}}
    return {"choices": [{"finish_reason": "stop", "message": {"content": "pong", "tool_calls": []}}],
            "usage": {"prompt_tokens": 12, "completion_tokens": 1}}


def vendor_b_transport(req: dict) -> dict:
    last = req["messages"][-1]["content"]
    if "weather" in last:
        return {"stop_reason": "tool_use", "content": [
            {"type": "tool_use", "name": "get_weather", "input": {"city": "Oslo"}}],
            "usage": {"input_tokens": 44, "output_tokens": 11}}
    return {"stop_reason": "end_turn", "content": [{"type": "text", "text": "pong"}],
            "usage": {"input_tokens": 13, "output_tokens": 1}}


class AdapterA:
    name = "vendor_a"

    def __init__(self, transport):
        self.transport = transport

    def complete(self, req: dict) -> Completion:
        raw = self.transport(req)
        ch = raw["choices"][0]
        calls = [(c["function"]["name"], json.loads(c["function"]["arguments"]))
                 for c in ch["message"].get("tool_calls") or []]
        finish = {"stop": "stop", "length": "length", "tool_calls": "tool_use"}[ch["finish_reason"]]
        return Completion(ch["message"]["content"] or "", calls,
                          raw["usage"]["prompt_tokens"], raw["usage"]["completion_tokens"], finish)


class AdapterB:
    name = "vendor_b"

    def __init__(self, transport):
        self.transport = transport

    def complete(self, req: dict) -> Completion:
        raw = self.transport(req)
        text = "".join(b["text"] for b in raw["content"] if b["type"] == "text")
        calls = [(b["name"], b["input"]) for b in raw["content"] if b["type"] == "tool_use"]
        finish = {"end_turn": "stop", "max_tokens": "length", "tool_use": "tool_use"}[raw["stop_reason"]]
        return Completion(text, calls, raw["usage"]["input_tokens"], raw["usage"]["output_tokens"], finish)


# ---- cassette ----
def request_key(req: dict) -> str:
    canonical = json.dumps(req, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()[:12]


class Cassette:
    def __init__(self):
        self.store: dict = {}

    def recording(self, transport):
        def wrapped(req):
            resp = transport(req)
            self.store[request_key(req)] = resp
            return resp
        return wrapped

    def replaying(self):
        def wrapped(req):
            key = request_key(req)
            if key not in self.store:
                raise KeyError(f"request drift: no recording for key {key}")
            return self.store[key]
        return wrapped


# ---- contract tests (run against every adapter) ----
def contract_suite(adapter) -> list:
    results = []
    c = adapter.complete({"messages": [{"role": "user", "content": "ping"}]})
    results.append(("plain text", c.text == "pong" and c.finish == "stop" and not c.tool_calls))
    c = adapter.complete({"messages": [{"role": "user", "content": "weather in Oslo?"}]})
    results.append(("tool call normalized", c.tool_calls == [("get_weather", {"city": "Oslo"})] and c.finish == "tool_use"))
    results.append(("usage reported", c.input_tokens > 0 and c.output_tokens > 0))
    return results


if __name__ == "__main__":
    cassette = Cassette()
    reqs = [{"messages": [{"role": "user", "content": "ping"}]},
            {"messages": [{"role": "user", "content": "weather in Oslo?"}]}]
    # One cassette per vendor: the same canonical request maps to different raw responses.
    rec = AdapterA(cassette.recording(vendor_a_transport))
    for r in reqs:
        rec.complete(r)
    print("recorded interactions:", len(cassette.store))

    for adapter in (AdapterA(vendor_a_transport), AdapterB(vendor_b_transport)):
        res = contract_suite(adapter)
        print(adapter.name, "contract:", ", ".join(f"{n}={'pass' if ok else 'FAIL'}" for n, ok in res))

    # Replay from the cassette: the vendor transport is no longer needed.
    replay = AdapterA(cassette.replaying())
    print("replay A:", replay.complete(reqs[0]).text)
    try:
        replay.complete({"messages": [{"role": "user", "content": "ping", "name": "x"}]})
    except KeyError as exc:
        print("drift detected:", exc)
