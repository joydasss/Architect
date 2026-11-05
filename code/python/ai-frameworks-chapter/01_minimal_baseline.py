"""Minimal no-framework baseline for LLM calls, standard library only.

Shows five things a thin application-owned layer needs:
1. a provider-agnostic client interface (Protocol) with normalized types,
2. retry with exponential backoff, jitter and a retry budget,
3. structured-output validation with a bounded repair loop,
4. a simple tool loop with an allow-list and argument validation,
5. tracing hooks that record one span per model call and per tool call.

A scripted FakeProvider replaces a real API so the script is deterministic and
runs offline. Run: python 01_minimal_baseline.py
"""
from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol


# ---------- normalized types (the application's own vocabulary) ----------
@dataclass
class ToolCall:
    name: str
    arguments: dict


@dataclass
class Completion:
    text: str = ""
    tool_calls: list = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""


class TransientError(Exception):
    """Timeout, 429 or 5xx. Safe to retry a pure model call."""


class PermanentError(Exception):
    """4xx other than 429, schema error, auth error. Do not retry."""


class ModelClient(Protocol):
    def complete(self, messages: list, tools: list | None = None) -> Completion: ...


# ---------- tracing hooks ----------
class Tracer:
    def __init__(self) -> None:
        self.spans: list = []

    def record(self, name: str, **attrs: Any) -> None:
        self.spans.append({"name": name, **attrs})


# ---------- retry ----------
def with_retry(fn: Callable[[], Completion], tracer: Tracer, max_attempts: int = 3,
               base_delay: float = 0.0, rng: random.Random | None = None) -> Completion:
    rng = rng or random.Random(0)
    for attempt in range(1, max_attempts + 1):
        try:
            result = fn()
            tracer.record("model_call", attempt=attempt, outcome="ok",
                          input_tokens=result.input_tokens, output_tokens=result.output_tokens)
            return result
        except TransientError:
            tracer.record("model_call", attempt=attempt, outcome="transient_error")
            if attempt == max_attempts:
                raise
            time.sleep(base_delay * (2 ** (attempt - 1)) * (0.5 + rng.random()))
    raise AssertionError("unreachable")


# ---------- structured output with bounded repair ----------
def validate_ticket(obj: Any) -> dict:
    if not isinstance(obj, dict):
        raise ValueError("top level must be an object")
    if obj.get("priority") not in {"low", "medium", "high"}:
        raise ValueError("priority must be low, medium or high")
    if not isinstance(obj.get("summary"), str) or not obj["summary"]:
        raise ValueError("summary must be a non-empty string")
    return obj


def structured(client: ModelClient, prompt: str, tracer: Tracer, max_repairs: int = 1) -> dict:
    messages = [{"role": "user", "content": prompt}]
    for repair in range(max_repairs + 1):
        out = with_retry(lambda: client.complete(messages), tracer)
        try:
            obj = validate_ticket(json.loads(out.text))
            tracer.record("validation", repair=repair, outcome="ok")
            return obj
        except (ValueError, json.JSONDecodeError) as exc:
            tracer.record("validation", repair=repair, outcome="invalid", error=str(exc))
            messages += [{"role": "assistant", "content": out.text},
                         {"role": "user", "content": f"Invalid: {exc}. Return only valid JSON."}]
    raise PermanentError("structured output failed after repairs")


# ---------- tool loop ----------
TOOLS: dict = {}


def tool(name: str, required: set):
    def deco(fn):
        TOOLS[name] = (fn, required)
        return fn
    return deco


@tool("get_order_status", {"order_id"})
def get_order_status(order_id: str) -> str:
    return {"A-1001": "shipped", "A-1002": "processing"}.get(order_id, "unknown")


def run_tool_loop(client: ModelClient, user_text: str, tracer: Tracer, max_steps: int = 4) -> str:
    messages = [{"role": "user", "content": user_text}]
    for step in range(max_steps):
        out = with_retry(lambda: client.complete(messages, tools=list(TOOLS)), tracer)
        if not out.tool_calls:
            return out.text
        for call in out.tool_calls:
            entry = TOOLS.get(call.name)
            if entry is None:                      # allow-list: unknown tools are refused
                result = "error: tool not permitted"
            elif set(call.arguments) != entry[1]:  # argument validation before side effects
                result = "error: bad arguments"
            else:
                result = entry[0](**call.arguments)
            tracer.record("tool_call", step=step, tool=call.name, result=result)
            messages.append({"role": "tool", "name": call.name, "content": result})
    raise PermanentError("tool loop exceeded max_steps")


# ---------- scripted fake provider ----------
class FakeProvider:
    def __init__(self, script: list) -> None:
        self.script = list(script)
        self.calls = 0

    def complete(self, messages: list, tools: list | None = None) -> Completion:
        self.calls += 1
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


if __name__ == "__main__":
    # Scenario 1: one transient failure, then a malformed answer, then a repaired answer.
    t1 = Tracer()
    p1 = FakeProvider([
        TransientError(),
        Completion(text='{"priority": "urgent", "summary": "x"}', input_tokens=120, output_tokens=15),
        Completion(text='{"priority": "high", "summary": "Printer down"}', input_tokens=170, output_tokens=14),
    ])
    print("structured:", structured(p1, "Triage: printer down", t1))
    print("provider calls:", p1.calls, "spans:", len(t1.spans))
    billed = sum(s.get("input_tokens", 0) + s.get("output_tokens", 0) for s in t1.spans)
    print("billed tokens seen by app:", billed)

    # Scenario 2: tool loop with an unpermitted tool request, then a permitted one.
    t2 = Tracer()
    p2 = FakeProvider([
        Completion(tool_calls=[ToolCall("delete_order", {"order_id": "A-1001"})]),
        Completion(tool_calls=[ToolCall("get_order_status", {"order_id": "A-1001"})]),
        Completion(text="Order A-1001 has shipped."),
    ])
    print("tool loop:", run_tool_loop(p2, "Where is order A-1001?", t2))
    for s in t2.spans:
        if s["name"] == "tool_call":
            print("  tool span:", s["tool"], "->", s["result"])
