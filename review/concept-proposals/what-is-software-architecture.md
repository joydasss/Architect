# Concept Proposals — What is Software Architecture? chapter

Staged for merge into [CORE_CONCEPTS.md](../../CORE_CONCEPTS.md). Do not edit
CORE_CONCEPTS.md directly from this chapter's session.

| Concept | Proposed Owner | Scope note |
|---|---|---|
| Software Architecture (definition: elements/form/rationale; structure + rationale; expensive-to-reverse decisions) | What is Software Architecture? chapter | Foundational definition (Perry & Wolf, Bass/Clements/Kazman, ISO/IEC/IEEE 42010) all other chapters should assume, not restate |
| Architecture vs. Design vs. Code (granularity/reversibility distinction) | What is Software Architecture? chapter | The scale-dependent boundary between the three, incl. Fowler's "hard to change later" heuristic |
| Components, connectors, and configuration | What is Software Architecture? chapter | Shaw & Garlan vocabulary; used wherever a chapter describes a system's structural elements |
| Coupling and cohesion | What is Software Architecture? chapter | Yourdon/Constantine definitions; the general low-coupling/high-cohesion principle applied at any granularity |
| Quality attributes / non-functional requirements (taxonomy) | What is Software Architecture? chapter | The umbrella list and framing only ("what architecture optimizes for"); per-attribute deep technique already owned elsewhere (Performance Engineering, System Design, Security, Observability) |
| Architecturally Significant Requirements (ASRs) | What is Software Architecture? chapter | The concept of identifying which requirements materially shape structure vs. which don't |
| Conway's Law / Inverse Conway Maneuver | What is Software Architecture? chapter | Organizational-structure-to-system-structure relationship; recap only where other chapters (e.g. Microservices, Enterprise Architecture) touch team topology |
| Technical debt | What is Software Architecture? chapter | Cunningham's metaphor; deliberate vs. accidental, and interest-accrual framing |
| Architecture fitness functions | What is Software Architecture? chapter | Automated, executable checks enforcing a structural constraint in CI; concrete tool examples referenced in Section 10/16 |
| 4+1 architectural view model (Kruchten) | What is Software Architecture? chapter | Conceptual view/stakeholder framing only — **possible overlap**: concrete modeling notations (C4, UML) are almost certainly owned by the Architecture Documentation part (Part 21); flagging for merge-step reconciliation rather than assuming a boundary |
| ATAM (Architecture Tradeoff Analysis Method) — mentioned, not taught | Architecture Thinking chapter (sibling, not yet drafted) | Only named in passing here as an example of a decision framework; **flagging possible overlap** — this chapter deliberately did not teach it, on the assumption the sibling "Architecture Thinking" chapter (same part) owns decision/trade-off methods; needs reconciliation once that chapter exists |

No other new concepts introduced beyond those listed above.
