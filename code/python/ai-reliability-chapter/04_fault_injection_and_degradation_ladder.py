"""Fault-injection fake model API, output repair loop, and degradation ladder.

Standard library only. The fake model API injects the failures a chapter test
suite should cover: 429 with Retry-After, 503, timeout, truncation, malformed
JSON, and schema violations. A resilient call wrapper retries only retryable
errors, repairs malformed output a bounded number of times, and walks a
degradation ladder when the primary path cannot produce a valid result.
"""

import json
import random


class RateLimited(Exception):
    def __init__(self, retry_after):
        self.retry_after = retry_after


class Overloaded(Exception):
    pass


class Timeout(Exception):
    pass


class FakeModel:
    """Scripted fake: a list of behaviours consumed one per call."""

    def __init__(self, script):
        self.script = list(script)
        self.calls = 0

    def complete(self, prompt):
        self.calls += 1
        step = self.script.pop(0) if self.script else "ok"
        if step == "429":
            raise RateLimited(retry_after=2)
        if step == "503":
            raise Overloaded()
        if step == "timeout":
            raise Timeout()
        if step == "truncated":
            return '{"category": "billing", "confid'
        if step == "bad_schema":
            return json.dumps({"category": "weather", "confidence": 0.9})
        if step == "prose":
            return "Sure! The category is billing."
        return json.dumps({"category": "billing", "confidence": 0.93})


ALLOWED = {"billing", "technical", "account"}


def validate(text):
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return None, "malformed_json"
    if obj.get("category") not in ALLOWED:
        return None, "schema_violation"
    if not isinstance(obj.get("confidence"), (int, float)):
        return None, "schema_violation"
    return obj, None


def keyword_rules(prompt):
    """Deterministic fallback rung."""
    p = prompt.lower()
    for word, cat in (("invoice", "billing"), ("refund", "billing"), ("password", "account"), ("error", "technical")):
        if word in p:
            return {"category": cat, "confidence": 0.5, "source": "rules"}
    return None


def resilient_classify(model, prompt, *, max_calls=4, max_repairs=1, sleep_log=None, backoff_seed=7):
    rng = random.Random(backoff_seed)
    repairs = 0
    calls = 0
    wait_total = 0.0
    while calls < max_calls:
        calls += 1
        try:
            text = model.complete(prompt)
        except RateLimited as e:
            wait = max(e.retry_after, rng.uniform(0, 0.5 * 2 ** calls))
            wait_total += wait
            continue
        except (Overloaded, Timeout):
            wait_total += rng.uniform(0, 0.5 * 2 ** calls)   # full jitter
            continue
        obj, err = validate(text)
        if obj:
            obj["source"] = "model"
            return obj, dict(calls=calls, repairs=repairs, wait=round(wait_total, 2), rung="primary")
        if err and repairs < max_repairs:
            repairs += 1
            prompt = prompt + "\nReturn only valid JSON matching the schema."
            continue
        break
    rules = keyword_rules(prompt)
    if rules:
        return rules, dict(calls=calls, repairs=repairs, wait=round(wait_total, 2), rung="rules")
    return {"category": "unclassified", "confidence": 0.0, "source": "queue_for_human"}, dict(
        calls=calls, repairs=repairs, wait=round(wait_total, 2), rung="human_queue")


CASES = [
    ("healthy", ["ok"], "Question about my invoice"),
    ("429 then ok", ["429", "ok"], "Question about my invoice"),
    ("malformed then repaired", ["prose", "ok"], "Question about my invoice"),
    ("schema violation twice -> rules", ["bad_schema", "bad_schema"], "Need a refund please"),
    ("truncated twice, no rule match -> human", ["truncated", "truncated"], "Something odd happened"),
    ("outage: 503 x4 -> rules", ["503", "503", "503", "503"], "Wrong password error"),
]


if __name__ == "__main__":
    for name, script, prompt in CASES:
        model = FakeModel(script)
        result, info = resilient_classify(model, prompt)
        print(f"{name:42s} -> {result['category']:12s} src={result['source']:15s} {info}")
