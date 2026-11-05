"""Lineage graph queries and model retirement planning (standard library only).

Run: python 04_lineage_and_retirement.py
"""
from datetime import date, timedelta

PARENTS = {
    "train_run_311": ["data_snap_2026_07", "feat_v7", "commit_ab12"],
    "adapter_v5": ["train_run_311", "base_model_x"],
    "index_88": ["corpus_snap_09", "embed_v2"],
    "release_2026.10.3": ["adapter_v5", "prompt_14", "index_88", "tools_3", "policy_9"],
    "deployment_prod_eu": ["release_2026.10.3"],
    "prediction_p123": ["deployment_prod_eu"],
}


def upstream(node):
    seen, stack = set(), [node]
    while stack:
        for p in PARENTS.get(stack.pop(), []):
            if p not in seen:
                seen.add(p)
                stack.append(p)
    return seen


def downstream(node):
    children = {}
    for child, ps in PARENTS.items():
        for p in ps:
            children.setdefault(p, []).append(child)
    seen, stack = set(), [node]
    while stack:
        for c in children.get(stack.pop(), []):
            if c not in seen:
                seen.add(c)
                stack.append(c)
    return seen


CONSUMERS = [  # name, requests per day, migrated
    ("checkout-bot", 120_000, False),
    ("search-rerank", 80_000, True),
    ("hr-faq", 20_000, False),
    ("analytics-batch", 60_000, True),
    ("shadow-notebook", 20_000, False),
]

if __name__ == "__main__":
    up = upstream("prediction_p123")
    print("Upstream of prediction_p123:", len(up), "artifacts")
    print("Downstream of data_snap_2026_07 (revoke if rights withdrawn):", sorted(downstream("data_snap_2026_07")))
    print("Downstream of embed_v2:", sorted(downstream("embed_v2")))

    total = sum(r for _, r, _ in CONSUMERS)
    left = sum(r for _, r, m in CONSUMERS if not m)
    print(f"Retiring base_model_x: {left:,} of {total:,} requests/day not migrated ({left / total:.1%})")
    print("Blocked by:", [n for n, _, m in CONSUMERS if not m])

    announce = date(2026, 11, 2)
    sunset = announce + timedelta(days=180)
    print("Announce:", announce, "Sunset:", sunset)
    for label, days in (("T-90 reminder", 90), ("T-30 brownout 1 hour", 30), ("T-7 final notice", 7)):
        print(f"  {label}: {sunset - timedelta(days=days)}")
