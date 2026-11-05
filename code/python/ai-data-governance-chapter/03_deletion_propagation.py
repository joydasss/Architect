"""Lineage graph, deletion impact query, tombstones, and backup replay.

Standard library only. Models one customer record fanning out into derived
artifacts, answers "what must be deleted?", shows the gap between "not
retrievable" and "purged", and shows why a backup restore must replay the
deletion ledger before serving traffic.
"""
from collections import deque

# edge: parent artifact -> derived artifacts
LINEAGE = {
    "src:ticket-4412": ["snap:raw-2026-09-01", "chunk:4412-v1", "chunk:4412-v2"],
    "snap:raw-2026-09-01": ["feat:cust-17-a", "feat:cust-17-b", "feat:cust-17-c", "ds:train-v7"],
    "chunk:4412-v1": ["vec:4412-v1"],
    "chunk:4412-v2": ["vec:4412-v2"],
    "vec:4412-v2": ["cache:q-9f3a"],
    "ds:train-v7": ["run:ft-0412"],
    "run:ft-0412": ["model:support-lora-3"],
}

STORE_OWNER = {
    "src": ("support-platform", 1),
    "snap": ("data-platform", 7),
    "chunk": ("rag-team", 1),
    "vec": ("rag-team", 1),
    "feat": ("ml-platform", 2),
    "cache": ("rag-team", 1),
    "ds": ("ml-platform", 30),
    "run": ("ml-platform", 0),
    "model": ("ml-platform", 90),
}
# (owner, maximum propagation delay in days) is illustrative.


def downstream(root):
    seen, order, q = {root}, [], deque([root])
    while q:
        node = q.popleft()
        order.append(node)
        for nxt in LINEAGE.get(node, []):
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return order


def main():
    impacted = downstream("src:ticket-4412")
    print(f"Impacted artifacts: {len(impacted)}")
    for a in impacted:
        kind = a.split(":")[0]
        owner, delay = STORE_OWNER[kind]
        print(f"  {a:24} owner={owner:17} max delay={delay:>3} d")
    worst = max(STORE_OWNER[a.split(':')[0]][1] for a in impacted)
    print(f"Completion deadline driven by slowest store: {worst} days")

    # Tombstone vs purge.
    tombstones = {a for a in impacted if a.split(":")[0] in {"src", "chunk", "vec", "cache"}}
    purged = {a for a in impacted if a.split(":")[0] in {"src", "cache"}}
    print("\nServing blocked by tombstone:", len(tombstones))
    print("Physically purged so far:", len(purged))
    print("Still stored but not retrievable:", sorted(tombstones - purged))
    needs_model_decision = [a for a in impacted if a.startswith("model:")]
    print("Needs explicit model decision (retrain / adapter / document):", needs_model_decision)

    # Backup replay.
    ledger = {"src:ticket-4412"}  # deletion ledger
    backup = ["src:ticket-4412", "src:ticket-5000", "chunk:4412-v1", "src:ticket-5001"]

    def restore(backup_items, ledger_ids, replay):
        live = list(backup_items)
        if replay:
            blocked = {a for root in ledger_ids for a in downstream(root)}
            live = [a for a in live if a not in blocked]
        return live

    print("\nRestore without replay serves:", restore(backup, ledger, replay=False))
    print("Restore with replay serves:   ", restore(backup, ledger, replay=True))


if __name__ == "__main__":
    main()
