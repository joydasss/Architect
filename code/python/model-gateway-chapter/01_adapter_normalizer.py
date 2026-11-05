"""Anti-corruption layer: two fake provider payload shapes -> one gateway contract.

Standard library only. The provider shapes are illustrative, not real vendor
schemas. Run: python 01_adapter_normalizer.py
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass
class GatewayRequest:
    logical_model: str
    messages: list          # [{"role": "user", "content": "..."}]
    max_output_tokens: int = 256
    tools: list = field(default_factory=list)
    json_schema: dict | None = None
    stream: bool = False


@dataclass
class GatewayResponse:
    text: str
    tool_calls: list
    finish_reason: str      # stop | length | tool_call | content_filter
    input_tokens: int
    output_tokens: int
    provider: str
    pinned_model: str
    error_class: str | None = None
    provider_extras: dict = field(default_factory=dict)  # not abstracted away


CAPS = {
    "provider_a": {"tools": True, "json_schema": True, "max_context": 128_000},
    "provider_b": {"tools": False, "json_schema": False, "max_context": 32_000},
}


def negotiate(req: GatewayRequest, provider: str, est_input_tokens: int) -> list:
    """Return a list of reasons the provider cannot serve this request."""
    caps, problems = CAPS[provider], []
    if req.tools and not caps["tools"]:
        problems.append("tools_unsupported")
    if req.json_schema and not caps["json_schema"]:
        problems.append("structured_output_unsupported")
    if est_input_tokens + req.max_output_tokens > caps["max_context"]:
        problems.append("context_too_long")
    return problems


def to_provider_a(req: GatewayRequest) -> dict:
    body = {"model": "a-large-2026-03", "messages": req.messages,
            "max_tokens": req.max_output_tokens}
    if req.tools:
        body["tools"] = [{"type": "function", "function": t} for t in req.tools]
    if req.json_schema:
        body["response_format"] = {"type": "json_schema", "schema": req.json_schema}
    return body


def from_provider_a(raw: dict) -> GatewayResponse:
    choice = raw["choices"][0]
    fr = {"stop": "stop", "length": "length", "tool_calls": "tool_call",
          "content_filter": "content_filter"}.get(choice["finish_reason"], "stop")
    calls = [{"name": c["function"]["name"],
              "arguments": json.loads(c["function"]["arguments"])}
             for c in choice["message"].get("tool_calls", [])]
    return GatewayResponse(choice["message"].get("content") or "", calls, fr,
                           raw["usage"]["prompt_tokens"],
                           raw["usage"]["completion_tokens"],
                           "provider_a", raw["model"],
                           provider_extras={"logprobs": choice.get("logprobs")})


def to_provider_b(req: GatewayRequest) -> dict:
    system = [m["content"] for m in req.messages if m["role"] == "system"]
    rest = [m for m in req.messages if m["role"] != "system"]
    return {"model": "b-medium-v7", "system": "\n".join(system),
            "turns": rest, "max_output": req.max_output_tokens}


def from_provider_b(raw: dict) -> GatewayResponse:
    fr = {"end_turn": "stop", "max_tokens": "length",
          "refusal": "content_filter"}.get(raw["stop"], "stop")
    return GatewayResponse("".join(p["text"] for p in raw["parts"]), [], fr,
                           raw["usage"]["in"], raw["usage"]["out"],
                           "provider_b", raw["model"])


def normalize_error(provider: str, status: int, code: str = "") -> str:
    """Map provider-specific HTTP status/code pairs to a gateway taxonomy."""
    if status == 429:
        return "rate_limited"
    if status in (500, 502, 503):
        return "provider_unavailable"
    if status == 504 or code == "timeout":
        return "timeout"
    if status == 400 and code in ("context_length_exceeded", "too_long"):
        return "context_too_long"
    if status in (401, 403):
        return "credential_error"      # never retry, page the platform team
    if status == 400:
        return "invalid_request"
    return "unknown"


RETRYABLE = {"rate_limited", "provider_unavailable", "timeout"}

if __name__ == "__main__":
    req = GatewayRequest("summarize-v1",
                         [{"role": "system", "content": "Be brief."},
                          {"role": "user", "content": "Summarize the case."}],
                         json_schema={"type": "object"})
    print("negotiate provider_a:", negotiate(req, "provider_a", 2_000) or "ok")
    print("negotiate provider_b:", negotiate(req, "provider_b", 2_000) or "ok")
    print("a request keys:", sorted(to_provider_a(req)))
    print("b request keys:", sorted(to_provider_b(req)))
    raw_a = {"model": "a-large-2026-03",
             "choices": [{"finish_reason": "tool_calls",
                          "message": {"content": None, "tool_calls": [
                              {"function": {"name": "lookup",
                                            "arguments": "{\"id\": 7}"}}]}}],
             "usage": {"prompt_tokens": 120, "completion_tokens": 18}}
    raw_b = {"model": "b-medium-v7", "stop": "refusal",
             "parts": [{"text": "I cannot help"}, {"text": " with that."}],
             "usage": {"in": 110, "out": 6}}
    for r in (from_provider_a(raw_a), from_provider_b(raw_b)):
        print(r.provider, r.finish_reason, r.tool_calls, r.input_tokens,
              r.output_tokens, repr(r.text))
    for s, c in [(429, ""), (503, ""), (400, "context_length_exceeded"),
                 (400, "bad_json"), (401, ""), (504, "")]:
        e = normalize_error("any", s, c)
        print(s, c or "-", "->", e, "retryable" if e in RETRYABLE else "no-retry")
