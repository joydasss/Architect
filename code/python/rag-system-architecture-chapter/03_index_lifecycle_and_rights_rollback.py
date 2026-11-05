"""Index lifecycle: candidate, gate, alias promotion, rollback, rights-safe rollback.

Standard library only. An index version is a set of (doc_id, doc_version).
A rights ledger records withdrawn documents. Rolling back the alias to an
older index version is safe only if the withdrawn documents are suppressed.
"""
from dataclasses import dataclass, field


@dataclass
class Index:
    version: str
    docs: dict  # doc_id -> doc_version


@dataclass
class Registry:
    versions: dict = field(default_factory=dict)
    alias: str = ""
    history: list = field(default_factory=list)
    withdrawn: set = field(default_factory=set)  # rights ledger

    def promote(self, version):
        self.history.append(self.alias)
        self.alias = version

    def rollback(self):
        self.alias = self.history.pop()

    def visible_docs(self):
        """Docs served: the aliased index minus the rights ledger (a serve-time suppress list)."""
        idx = self.versions[self.alias]
        return {d: v for d, v in idx.docs.items() if d not in self.withdrawn}


def gate(candidate, source_count, prior, min_ratio=0.98, max_drop=0.05):
    """Completeness and regression gate."""
    ratio = len(candidate.docs) / source_count
    drop = 1 - len(candidate.docs) / max(len(prior.docs), 1)
    return ratio >= min_ratio and drop <= max_drop, ratio, drop


reg = Registry()
v1 = Index("v1", {f"d{i}": 1 for i in range(100)})
reg.versions["v1"] = v1
reg.alias = "v1"

# v2 built from 100 sources + 1 new doc, d7 updated
v2_docs = {f"d{i}": 1 for i in range(100)}
v2_docs["d7"] = 2
v2_docs["d100"] = 1
v2 = Index("v2", v2_docs)
ok, ratio, drop = gate(v2, source_count=101, prior=v1)
print(f"gate v2: ok={ok} completeness={ratio:.2%} drop={drop:.2%}")
reg.versions["v2"] = v2
reg.promote("v2")

# v3 build lost most documents because a connector failed
v3 = Index("v3", {f"d{i}": 1 for i in range(60)})
ok, ratio, drop = gate(v3, source_count=101, prior=v2)
print(f"gate v3: ok={ok} completeness={ratio:.2%} drop={drop:.2%} -> not promoted")

# Rights withdrawal of d5 after v2 is live (ledger suppresses at serve time)
reg.withdrawn.add("d5")
print("d5 visible on v2 after withdrawal:", "d5" in reg.visible_docs())

# Naive rollback re-exposes nothing here only because the ledger is applied at serve time
reg.rollback()
print("alias after rollback:", reg.alias, "| d5 visible:", "d5" in reg.visible_docs())

# Counter-example: a rollback path that ignores the ledger
naive = reg.versions[reg.alias].docs
print("naive rollback (no ledger) exposes d5:", "d5" in naive)
