# Part 22 — Architectural Thinking and Decision Practice

Supplemental module extending [Part 01 — Architecture Mindset](../01_Architecture_Mindset/PART_OVERVIEW.md) from foundational ideas into applied decision practice. This module is deliberately a practice layer: Part 01 CH03 remains the full owner of Architecture Decision Records (ADRs), Architecture Tradeoff Analysis Method (ATAM), decision reversibility, quality-attribute scenarios, and the general architecture decision loop. Chapters here recap those concepts and use them in realistic reviews, workshops, and case studies rather than re-teaching their definitions.

**Topic map:** [Part 22 topic map](TOPIC_MAP.md).

## Scope boundary

Part 01 owns the core reasoning concepts and reusable methods. Part 07 owns system-design requirements, interviews, and High-Level Design (HLD) workflow; Part 18 owns enterprise architecture governance. This module focuses on applying those tools under ambiguity, organizational constraints, and incomplete evidence, with explicit handoffs to those owners.

## Chapters

| Chapter | Focus | Status |
|---|---|---|
| [Framing Architecture Problems and Decision Boundaries](CH01_Framing_Architecture_Problems_and_Decision_Boundaries.md) | Turn broad requests into a bounded decision statement; distinguish problem, constraint, assumption, and proposed solution; recap Part 07 Functional Requirements. | Drafted |
| [Systems Thinking for Architecture](CH02_Systems_Thinking_for_Architecture.md) | Apply feedback loops, stocks/flows, delays, second-order effects, and unintended consequences to architecture changes; recap Part 01 CH03. | Drafted |
| [Decomposition, Boundaries, and Dependency Reasoning](CH03_Decomposition_Boundaries_and_Dependency_Reasoning.md) | Identify stable responsibilities, coupling, dependency direction, and change ownership without duplicating Part 07 HLD or Part 20 pattern catalogs. | Drafted |
| [Evidence, Assumptions, and Uncertainty](CH04_Evidence_Assumptions_and_Uncertainty.md) | Separate observed facts, estimates, assumptions, and unknowns; design evidence-gathering steps and decision thresholds. | Drafted |
| [Reversibility, Optionality, and Decision Timing](CH05_Reversibility_Optionality_and_Decision_Timing.md) | Apply one-way/two-way-door and last-responsible-moment reasoning to pilots, migration gates, and irreversible commitments; recap Part 01 ownership. | Drafted |
| [Facilitating Architecture Trade-off Workshops](CH06_Facilitating_Architecture_Tradeoff_Workshops.md) | Apply Part 01 ATAM and quality-attribute scenarios in a facilitated, evidence-based review; structure disagreement around facts, priorities, and risk tolerance. | Drafted |
| [Socio-Technical Architecture Reasoning](CH07_Socio_Technical_Architecture_Reasoning.md) | Apply team boundaries, cognitive load, ownership, and Conway's Law to the design and operating model; recap Part 01 and Part 18 owners. | Drafted |
| [Architecture Pre-Mortems and Challenge Reviews](CH08_Architecture_Pre_Mortems_and_Challenge_Reviews.md) | Use threat prompts, failure narratives, assumption challenges, and dissent protocols before committing to high-impact decisions. | Drafted |
| [Measuring Decision Outcomes and Reconsideration Triggers](CH09_Measuring_Decision_Outcomes_and_Reconsideration_Triggers.md) | Define observable signals, review dates, and change thresholds that tell a team when an architectural choice should be revisited; recap fitness-function ownership. | Drafted |
| [Integrated Architecture Decision Clinics](CH10_Integrated_Architecture_Decision_Clinics.md) | Case-based exercises combining requirements, options, evidence, trade-offs, stakeholder alignment, and decision records across the handbook's domains. | Drafted |
