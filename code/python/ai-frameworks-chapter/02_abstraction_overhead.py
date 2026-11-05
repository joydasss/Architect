"""Abstraction overhead: tokens, calls, and in-process CPU time. Standard library only.

Part A (deterministic): token and call amplification when a layered chain adds a
hidden system prompt, a query-rewrite call, a format-instruction block and a
retry policy. All sizes are ILLUSTRATIVE assumptions, set in the CONFIG dict.
Part B (measured): in-process cost of wrapper layers (callbacks, message objects,
copying) around a no-op provider. Absolute numbers depend on your machine; the
point is the order of magnitude versus a network call of tens to thousands of ms.

Run: python 02_abstraction_overhead.py
"""
from __future__ import annotations

import copy
import statistics
import time

CONFIG = {
    "user_tokens": 200,          # the user's question plus app context
    "app_system_tokens": 300,    # system prompt the team wrote and can see
    "hidden_system_tokens": 150, # framework default instructions the team did not write
    "format_instr_tokens": 120,  # framework-injected output-format instructions
    "rewrite_in_tokens": 250,    # hidden query-rewrite call: input
    "rewrite_out_tokens": 30,    # hidden query-rewrite call: output
    "answer_out_tokens": 250,
    "transient_fail_rate": 0.10, # fraction of attempts failing after billing starts
    "max_attempts": 3,
    "price_in_per_mtok": 3.00,   # USD per million input tokens (illustrative)
    "price_out_per_mtok": 15.00, # USD per million output tokens (illustrative)
}


def expected_attempts(p: float, n: int) -> float:
    """Expected attempts with success prob (1-p) per attempt, capped at n attempts.
    E = sum_{k=0}^{n-1} p^k = (1 - p^n) / (1 - p)."""
    return (1 - p ** n) / (1 - p)


def cost(in_tok: float, out_tok: float) -> float:
    return in_tok * CONFIG["price_in_per_mtok"] / 1e6 + out_tok * CONFIG["price_out_per_mtok"] / 1e6


def part_a() -> None:
    c = CONFIG
    direct_in = c["user_tokens"] + c["app_system_tokens"]
    direct_out = c["answer_out_tokens"]
    # Direct path: the app retries only on a pre-response transient failure, billed as 0 tokens.
    direct_cost = cost(direct_in, direct_out)

    # Layered path: hidden prompt + format block + rewrite call, and retries that re-bill
    # the full input when the failure happens after the request was accepted.
    layered_in_main = direct_in + c["hidden_system_tokens"] + c["format_instr_tokens"]
    attempts = expected_attempts(c["transient_fail_rate"], c["max_attempts"])
    layered_in = layered_in_main * attempts + c["rewrite_in_tokens"]
    layered_out = c["answer_out_tokens"] + c["rewrite_out_tokens"]
    layered_cost = cost(layered_in, layered_out)

    print("Part A: token and cost amplification (illustrative)")
    print(f"  direct   : in={direct_in} out={direct_out} calls=1.00 cost=${direct_cost:.6f}")
    print(f"  layered  : in={layered_in:.1f} out={layered_out} calls={attempts + 1:.2f} cost=${layered_cost:.6f}")
    print(f"  input-token ratio: {layered_in / direct_in:.2f}x   cost ratio: {layered_cost / direct_cost:.2f}x")
    print(f"  expected attempts at p={c['transient_fail_rate']}: {attempts:.3f}")


class NoopProvider:
    def complete(self, messages):
        return {"text": "ok", "input_tokens": 10, "output_tokens": 2}


class Msg:
    def __init__(self, role, content, meta=None):
        self.role, self.content, self.meta = role, content, meta or {}

    def to_dict(self):
        return {"role": self.role, "content": self.content, "meta": dict(self.meta)}


class LayeredClient:
    """Imitates typical framework overhead: message objects, deep copies, 3 callbacks."""

    def __init__(self, provider, callbacks):
        self.provider, self.callbacks = provider, callbacks

    def invoke(self, text):
        msgs = [Msg("system", "You are helpful."), Msg("user", text)]
        payload = copy.deepcopy([m.to_dict() for m in msgs])
        for cb in self.callbacks:
            cb("start", payload)
        out = self.provider.complete(payload)
        result = copy.deepcopy(out)
        for cb in self.callbacks:
            cb("end", result)
        return result


def part_b(n: int = 20000) -> None:
    prov = NoopProvider()
    events = []
    layered = LayeredClient(prov, [lambda k, p: events.append(k)] * 3)
    msgs = [{"role": "user", "content": "hello"}]
    # warm-up
    for _ in range(1000):
        prov.complete(msgs)
        layered.invoke("hello")
    events.clear()
    d, l = [], []
    for _ in range(5):
        t = time.perf_counter()
        for _ in range(n):
            prov.complete(msgs)
        d.append((time.perf_counter() - t) / n * 1e6)
        t = time.perf_counter()
        for _ in range(n):
            layered.invoke("hello")
        l.append((time.perf_counter() - t) / n * 1e6)
        events.clear()
    print("Part B: in-process wrapper cost per call (microseconds, median of 5 runs)")
    print(f"  direct  : {statistics.median(d):.2f} us")
    print(f"  layered : {statistics.median(l):.2f} us")
    extra_ms = (statistics.median(l) - statistics.median(d)) / 1000
    print(f"  added   : {extra_ms:.4f} ms per call, versus a 800 ms model call = {extra_ms / 800 * 100:.4f} percent")


if __name__ == "__main__":
    part_a()
    part_b()
