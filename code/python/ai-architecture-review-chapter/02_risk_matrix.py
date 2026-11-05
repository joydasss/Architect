"""Risk register scorer and 5x5 risk-matrix generator for an AI architecture review.

Standard library only. Run: python 02_risk_matrix.py

Score = likelihood (1-5) x impact (1-5). Bands: 1-5 low, 6-11 medium,
12-19 high, 20-25 critical. A risk without an owner or a due gate is flagged,
because an unowned risk is an unmanaged risk.
"""

RISKS = [
    # id, title, likelihood, impact, owner, gate, mitigation
    ("R1", "Cross-tenant chunk returned from shared cache", 3, 5, "platform-lead", "pre-launch", "tenant-scoped cache keys, canary probes"),
    ("R2", "Retrieval corpus contains documents without usage rights", 3, 4, "data-owner", "pre-launch", "rights flag at ingestion, quarantine"),
    ("R3", "Provider outage with no tested fallback", 4, 3, "sre-lead", "pre-launch", "secondary provider, extractive fallback"),
    ("R4", "Silent quality drift after a provider model update", 4, 3, "ml-lead", "post-launch 30d", "pinned versions, golden-set canary"),
    ("R5", "Cost grows faster than usage", 3, 3, "finance-partner", "post-launch 30d", "per-tenant budgets, alerts"),
    ("R6", "Reviewers rubber-stamp suggestions", 4, 4, "product-owner", "pre-launch", "seeded errors, override-rate monitor"),
    ("R7", "Runbook for AI incidents does not exist", 3, 3, "", "", "write runbook"),
]


def band(score):
    if score >= 20:
        return "critical"
    if score >= 12:
        return "high"
    if score >= 6:
        return "medium"
    return "low"


def matrix(risks):
    grid = {(l, i): [] for l in range(1, 6) for i in range(1, 6)}
    for rid, _, l, i, *_ in risks:
        grid[(l, i)].append(rid)
    lines = ["impact ->   1       2       3       4       5"]
    for l in range(5, 0, -1):
        cells = ["+".join(grid[(l, i)]) or "." for i in range(1, 6)]
        lines.append(f"L={l}      " + "".join(f"{c:<8}" for c in cells))
    return "\n".join(lines)


if __name__ == "__main__":
    scored = sorted(RISKS, key=lambda r: -(r[2] * r[3]))
    print("id  score band      owner            gate             title")
    for rid, title, l, i, owner, gate, _ in scored:
        flag = "" if owner and gate else "  <-- UNOWNED OR NO GATE"
        print(f"{rid:<3} {l * i:>5} {band(l * i):<9} {owner or '-':<16} {gate or '-':<16} {title}{flag}")
    print()
    print(matrix(RISKS))
    total = sum(r[2] * r[3] for r in RISKS)
    print(f"\nTotal exposure points: {total}")
    print("Open critical/high risks:", sum(1 for r in RISKS if r[2] * r[3] >= 12))
