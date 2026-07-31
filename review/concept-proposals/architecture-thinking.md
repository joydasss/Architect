# Concept Proposals — Architecture Thinking chapter

Staged for merge into [CORE_CONCEPTS.md](../../CORE_CONCEPTS.md). Do not edit
CORE_CONCEPTS.md directly from this chapter's session.

| Concept | Proposed Owner | Scope note |
|---|---|---|
| Essential vs. accidental complexity (Brooks) | Architecture Thinking chapter | The distinction as a general reasoning tool for scoping any redesign/decision, not tied to one technology |
| Reversible vs. irreversible decisions ("one-way door" / "two-way door") | Architecture Thinking chapter | General decision-classification heuristic used to calibrate process rigor |
| Architecture Decision Records (ADR) | Architecture Thinking chapter | Template, process, and review checklist for capturing individual decisions |
| Trade-off analysis method / ATAM (Architecture Tradeoff Analysis Method) | Architecture Thinking chapter | Quality-attribute-scenario-driven method for comparing options; general-purpose, applied throughout the book |
| Quality attributes as trade-off drivers | Architecture Thinking chapter | Framing non-functional requirements as named, concrete, competing scenarios rather than generic labels |
| Conway's Law / inverse Conway maneuver | Architecture Thinking chapter | General org-structure-to-architecture mapping; likely referenced again by Part 15 (Enterprise Architecture) and Part 17 (Architecture Patterns, team-topologies-adjacent patterns) — flagging for merge-step overlap check since this session has no visibility into those drafts |
| Fitness functions (evolutionary architecture) | Architecture Thinking chapter | General concept of automated, objective guardrails validating an architectural property continuously; may also be relevant to Part 17 (Architecture Patterns) if an "Evolutionary Architecture" pattern chapter exists there — flagging for merge-step overlap check |

Note: this chapter deliberately did not define "what is software
architecture" or the Solution Architect role, per this part's sibling
chapters ("What is Software Architecture?", "Role of a Solution Architect"),
which were not visible to this session. If either sibling chapter also
introduces overlapping framing for any concept above (e.g. quality
attributes, or the reversibility heuristic), the merge step should reconcile
ownership between the three Part 01 chapters.
