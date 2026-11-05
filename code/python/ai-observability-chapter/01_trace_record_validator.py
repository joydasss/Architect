"""Validate AI trace records against the attribution schema in Chapter 11.

Standard library only. Run: python 01_trace_record_validator.py

A trace record is a flat list of spans for one request. The validator checks
that every output is attributable to a release manifest, that spans form a
single tree, that required attributes exist per span kind, that token and
latency fields are consistent, and that no raw content leaked into a record
whose capture policy forbids it.
"""
from __future__ import annotations

import re

REQUIRED_BY_KIND = {
    "request": ["release_manifest_id", "tenant_id", "authz_scope_id", "config_hash"],
    "retrieval": ["index_version", "top_k", "returned_count"],
    "rerank": ["reranker_version"],
    "prompt_assembly": ["prompt_template_version", "input_tokens_estimate"],
    "model_call": [
        "provider", "request_model", "response_model", "input_tokens",
        "output_tokens", "queue_ms", "ttft_ms", "decode_ms", "cost_usd",
    ],
    "tool_call": ["tool_name", "tool_schema_version", "authz_scope_id"],
    "validation": ["schema_valid", "safety_verdict"],
    "post_processing": [],
}
MANIFEST_RE = re.compile(r"^rm-\d{4}-\d{2}-\d{2}-\d{3}$")
CONTENT_KEYS = {"prompt_text", "output_text", "retrieved_text", "tool_input", "tool_output"}


def validate(spans: list[dict], content_capture: bool = False) -> list[str]:
    errors: list[str] = []
    ids = {s["span_id"] for s in spans}
    roots = [s for s in spans if s.get("parent_id") is None]
    if len(roots) != 1:
        errors.append(f"expected 1 root span, found {len(roots)}")
    traces = {s["trace_id"] for s in spans}
    if len(traces) != 1:
        errors.append(f"spans span {len(traces)} trace ids")
    for s in spans:
        sid, kind, a = s["span_id"], s["kind"], s.get("attrs", {})
        if kind not in REQUIRED_BY_KIND:
            errors.append(f"{sid}: unknown span kind {kind!r}")
            continue
        if s.get("parent_id") is not None and s["parent_id"] not in ids:
            errors.append(f"{sid}: parent {s['parent_id']} missing (orphan)")
        for key in REQUIRED_BY_KIND[kind]:
            if key not in a:
                errors.append(f"{sid} ({kind}): missing attribute {key}")
        if kind == "request" and "release_manifest_id" in a:
            if not MANIFEST_RE.match(a["release_manifest_id"]):
                errors.append(f"{sid}: bad manifest id {a['release_manifest_id']!r}")
        if kind == "model_call" and all(k in a for k in ("queue_ms", "ttft_ms", "decode_ms")):
            phases = a["queue_ms"] + a["ttft_ms"] + a["decode_ms"]
            dur = s["end_ms"] - s["start_ms"]
            if abs(phases - dur) > 5:
                errors.append(f"{sid}: phases sum {phases} ms but span lasts {dur} ms")
        if kind == "model_call" and a.get("input_tokens", 0) < 0:
            errors.append(f"{sid}: negative token count")
        if not content_capture:
            leaked = CONTENT_KEYS & set(a)
            if leaked:
                errors.append(f"{sid}: content attributes {sorted(leaked)} present while capture is off")
        if s["end_ms"] < s["start_ms"]:
            errors.append(f"{sid}: ends before it starts")
    return errors


def good_trace() -> list[dict]:
    t = "t-001"
    return [
        {"trace_id": t, "span_id": "s1", "parent_id": None, "kind": "request",
         "start_ms": 0, "end_ms": 1900,
         "attrs": {"release_manifest_id": "rm-2026-10-02-001", "tenant_id": "acme",
                   "authz_scope_id": "scope-77", "config_hash": "9f2c1ab4"}},
        {"trace_id": t, "span_id": "s2", "parent_id": "s1", "kind": "retrieval",
         "start_ms": 20, "end_ms": 180,
         "attrs": {"index_version": "idx-2026-09-28", "top_k": 20, "returned_count": 20}},
        {"trace_id": t, "span_id": "s3", "parent_id": "s1", "kind": "rerank",
         "start_ms": 180, "end_ms": 300, "attrs": {"reranker_version": "rr-4"}},
        {"trace_id": t, "span_id": "s4", "parent_id": "s1", "kind": "prompt_assembly",
         "start_ms": 300, "end_ms": 320,
         "attrs": {"prompt_template_version": "pt-v12", "input_tokens_estimate": 3100}},
        {"trace_id": t, "span_id": "s5", "parent_id": "s1", "kind": "model_call",
         "start_ms": 320, "end_ms": 1800,
         "attrs": {"provider": "provider-a", "request_model": "model-x",
                   "response_model": "model-x-2026-09-15", "input_tokens": 3120,
                   "output_tokens": 410, "queue_ms": 40, "ttft_ms": 480,
                   "decode_ms": 960, "cost_usd": 0.0112}},
        {"trace_id": t, "span_id": "s6", "parent_id": "s1", "kind": "validation",
         "start_ms": 1800, "end_ms": 1850,
         "attrs": {"schema_valid": True, "safety_verdict": "pass"}},
    ]


def bad_trace() -> list[dict]:
    spans = good_trace()
    spans[0]["attrs"]["release_manifest_id"] = "latest"            # not immutable
    del spans[1]["attrs"]["index_version"]                         # unattributable retrieval
    spans[4]["attrs"]["decode_ms"] = 300                           # phases do not add up
    spans[4]["attrs"]["output_text"] = "Dear Ms. Rivera, ..."      # leaked content
    spans[5]["parent_id"] = "s99"                                  # orphan
    return spans


if __name__ == "__main__":
    for name, spans in (("good", good_trace()), ("bad", bad_trace())):
        errs = validate(spans)
        print(f"{name} trace: {len(errs)} error(s)")
        for e in errs:
            print("  -", e)
