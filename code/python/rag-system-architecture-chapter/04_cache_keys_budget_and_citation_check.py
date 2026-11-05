"""Authorization-aware cache keys, deadline budget allocation, citation verification.

Standard library only.
"""
import hashlib
import re


def cache_key(query, tenant, scope_hash, index_version, acl_version, prompt_version, model):
    raw = "|".join([query.strip().lower(), tenant, scope_hash, index_version,
                    str(acl_version), prompt_version, model])
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


k1 = cache_key("Travel limit?", "acme", "scopeA", "idx-42", 7, "p3", "m1")
k2 = cache_key("Travel limit?", "acme", "scopeB", "idx-42", 7, "p3", "m1")
k3 = cache_key("Travel limit?", "acme", "scopeA", "idx-42", 8, "p3", "m1")
print("same query, different scope  ->", k1 != k2)
print("same scope, ACL version bump ->", k1 != k3)

# ---- Deadline budget (ms) ----
deadline = 8000
fixed = {"auth+scope": 150, "retrieval (parallel)": 400, "rerank": 250,
         "context assembly": 50, "validation": 300, "response": 100}
reserved = sum(fixed.values())
gen_budget = deadline - reserved
print(f"\ndeadline {deadline} ms, fixed stages {reserved} ms, generation budget {gen_budget} ms")
tps = 60  # output tokens per second (assumption)
ttft = 700  # time to first token ms (assumption)
max_out = int((gen_budget - ttft) / 1000 * tps)
print(f"with TTFT {ttft} ms at {tps} tok/s, max output tokens ~ {max_out}")

# ---- Citation verification ----
retrieved = {
    "pol-12@v3#p4": "Employees may claim economy airfare for flights under 6 hours.",
    "pol-12@v3#p5": "Business class requires VP approval for flights over 6 hours.",
}
answer = ("Economy airfare is reimbursable [pol-12@v3#p4]. "
          "Meals are capped at 60 dollars [pol-99@v1#p1].")


def verify(answer, retrieved):
    cites = re.findall(r"\[([^\]]+)\]", answer)
    sentences = [s.strip() for s in re.split(r"(?<=\.)\s+", answer) if s.strip()]
    results = []
    for s in sentences:
        ids = re.findall(r"\[([^\]]+)\]", s)
        if not ids:
            results.append((s, "uncited"))
        elif all(i in retrieved for i in ids):
            results.append((s, "citation resolves"))
        else:
            bad = [i for i in ids if i not in retrieved]
            results.append((s, f"INVALID citation {bad}"))
    return results


print()
for s, r in verify(answer, retrieved):
    print(f"{r:32s} | {s}")
