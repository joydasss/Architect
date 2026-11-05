"""Release manifest validator (standard library only).

A release manifest pins every behavior-changing artifact as one versioned unit.
This script validates a good manifest and a deliberately broken one.
Run: python 01_release_manifest_validator.py
"""
import re

SHA = re.compile(r"^sha256:[0-9a-f]{64}$")
REQUIRED = ["model", "prompt", "index", "tools", "guardrails", "eval_suite", "config"]


def d(ch):
    return "sha256:" + ch * 64


GOOD = {
    "release": "support-assistant@2026.10.3",
    "risk_tier": 2,
    "artifacts": {
        "model": {"id": "provider-model-x", "version": "2026-08-01", "digest": d("a"), "kind": "hosted"},
        "prompt": {"id": "support-prompt", "version": "14", "digest": d("b"), "tools_schema": "3"},
        "index": {"id": "kb-index", "version": "88", "digest": d("c"), "embedding_model": "embed-v2"},
        "embedder": {"id": "embed-v2", "version": "2", "digest": d("d")},
        "tools": {"id": "support-tools", "version": "3", "digest": d("e")},
        "guardrails": {"id": "policy-bundle", "version": "9", "digest": d("f")},
        "eval_suite": {"id": "support-evals", "version": "21", "digest": d("1")},
        "config": {"id": "runtime-config", "version": "5", "digest": d("2")},
    },
    "signature": {"signer": "release-pipeline", "verified": True},
    "eval_report": {"suite_version": "21", "passed": True},
    "rollback_to": "support-assistant@2026.09.7",
}

BAD = {
    "release": "support-assistant@2026.10.4",
    "risk_tier": 3,
    "artifacts": {
        "model": {"id": "provider-model-x", "version": "latest", "digest": "sha256:abc", "kind": "hosted"},
        "prompt": {"id": "support-prompt", "version": "15", "digest": d("b"), "tools_schema": "4"},
        "index": {"id": "kb-index", "version": "89", "digest": d("c"), "embedding_model": "embed-v3"},
        "embedder": {"id": "embed-v2", "version": "2", "digest": d("d")},
        "tools": {"id": "support-tools", "version": "3", "digest": d("e")},
        "eval_suite": {"id": "support-evals", "version": "21", "digest": d("1")},
        "config": {"id": "runtime-config", "version": "5", "digest": d("2")},
    },
    "signature": {"signer": "release-pipeline", "verified": False},
    "eval_report": {"suite_version": "20", "passed": True},
}


def validate(m):
    errs = []
    a = m.get("artifacts", {})
    for name in REQUIRED:
        if name not in a:
            errs.append(f"missing artifact: {name}")
    for name, art in a.items():
        if art.get("version") in (None, "", "latest"):
            errs.append(f"{name}: unpinned version '{art.get('version')}'")
        if not SHA.match(art.get("digest", "")):
            errs.append(f"{name}: invalid digest '{art.get('digest')}'")
    if "prompt" in a and "tools" in a:
        if a["prompt"].get("tools_schema") != a["tools"].get("version"):
            errs.append("prompt expects tool schema %s but manifest pins %s"
                        % (a["prompt"].get("tools_schema"), a["tools"].get("version")))
    if "index" in a and "embedder" in a:
        if a["index"].get("embedding_model") != a["embedder"].get("id"):
            errs.append("index built with %s but query embedder is %s"
                        % (a["index"].get("embedding_model"), a["embedder"].get("id")))
    if not m.get("signature", {}).get("verified"):
        errs.append("signature not verified")
    rep = m.get("eval_report", {})
    if "eval_suite" in a and rep.get("suite_version") != a["eval_suite"].get("version"):
        errs.append("eval report ran suite %s but manifest pins %s"
                    % (rep.get("suite_version"), a["eval_suite"].get("version")))
    if m.get("risk_tier", 0) >= 2 and not m.get("rollback_to"):
        errs.append("tier >= 2 requires rollback_to")
    return errs


if __name__ == "__main__":
    for label, m in (("GOOD", GOOD), ("BAD", BAD)):
        errs = validate(m)
        print(f"{label} {m['release']}: {'PASS' if not errs else 'FAIL (%d errors)' % len(errs)}")
        for e in errs:
            print("  -", e)
