# Concept Proposals — Backlog (CH22)

Staging file for `review/concept-proposals/` per the Concept Ownership Rule
in [STYLE_GUIDE.md](../../STYLE_GUIDE.md). To be merged into
[CORE_CONCEPTS.md](../../CORE_CONCEPTS.md) by a separate batch-merge step —
not edited directly by this chapter's authoring session.

## Proposed new concepts (owned by this chapter)

| Concept | Proposed owning chapter | Notes |
|---|---|---|
| Backlog Item Taxonomy & Mechanics (Epics, Stories, Spikes, Tech Debt, Bugs, Enablers) | [Backlog](../../02_Design_Thinking_and_Product_Management/CH22_Backlog.md) | Structured item classification, behavioral payload, and estimation profiles; Section 4.1 |
| DEEP Framework (Detailed appropriately, Estimated, Emergent, Prioritized) | [Backlog](../../02_Design_Thinking_and_Product_Management/CH22_Backlog.md) | Operational quality criteria for a living product backlog (Roman Pichler / Mike Cohn); Section 4.2 |
| Definition of Ready (DoR) vs. Definition of Done (DoD) Contract Boundaries | [Backlog](../../02_Design_Thinking_and_Product_Management/CH22_Backlog.md) | Dual-gate execution contract between discovery, team execution, and production release; Section 4.3 |
| Backlog Refinement Loop Mechanics | [Backlog](../../02_Design_Thinking_and_Product_Management/CH22_Backlog.md) | Continuous intake-to-sprint-ready pipeline, cadence, and progressive elaboration; Section 4.4 |
| Backlog Debt and Entropy Decay | [Backlog](../../02_Design_Thinking_and_Product_Management/CH22_Backlog.md) | Accumulation of stale items, decay rates, triage algorithms, and backlog pruning discipline; Section 4.5 |
| Item Dependency Topology & Coupling Analysis | [Backlog](../../02_Design_Thinking_and_Product_Management/CH22_Backlog.md) | Directed Acyclic Graph (DAG) mapping of hard/soft/external dependencies and cross-team coupling; Section 4.6 |
| Backlog Tooling Synchronization Architecture | [Backlog](../../02_Design_Thinking_and_Product_Management/CH22_Backlog.md) | Bi-directional integration, event-driven outbox patterns, state reconciliation, and conflict resolution across tools (Jira, GitHub, Azure DevOps); Section 4.7 |

## Distinctions drawn against existing owned concepts (no new ownership claimed)

These sections explicitly distinguish this chapter's scope from concepts
already owned elsewhere, and recap rather than re-teach them:

- Story Mapping (CH20) — owns task-oriented narrative backbone, walking skeleton, and horizontal release slicing. Backlog owns item mechanics, refinement loops, DEEP criteria, item coupling, and sync architecture. Recapped in Section 4.8.
- Roadmaps (CH21) — owns multi-quarter initiative scheduling, audience-tiered disclosure, and Now/Next/Later horizons. Backlog owns item-level execution mechanics fed by roadmap themes. Recapped in Section 4.8.
- Product Strategy (CH15) — owns strategy stack, strategy-to-roadmap translation contract, and OKRs. Recapped in Section 1 and Section 4.8.
- Prioritization (CH25, unbuilt) — Backlog references priority ranking as part of DEEP ("P" for Prioritized), but defers formal scoring algorithms (RICE, Kano, MoSCoW) to CH25.

## Forward references to not-yet-drafted sibling chapters

Named only for scope boundary, not taught:

- **MVP (Minimum Viable Product)** — release scoping validation mechanics.
- **Metrics** / **North Star Metrics** — metric definition and goal alignment.
- **Prioritization (RICE, MoSCoW, Kano)** — priority scoring methodologies.
