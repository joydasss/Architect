# Part 22 — Architectural Thinking and Decision Practice Topic Map

This map defines coverage for Part 22's ten practice-focused chapters. The supplemental module applies Part 01's architecture reasoning in ambiguous, organizational, and evidence-poor settings. It uses the foundations rather than re-teaching their definitions.

## Part-wide ownership boundaries

- Part 01 CH03 remains the full owner of Architecture Decision Records (ADRs), Architecture Tradeoff Analysis Method (ATAM), reversibility, quality-attribute scenarios, and the general architecture decision loop.
- Part 07 owns system-design requirements and HLD workflow; Part 18 owns enterprise governance; Part 20 owns architecture-pattern catalogs.
- Part 22 owns applied facilitation, evidence gathering, challenge methods, decision timing, and realistic architecture decision clinics.

## Chapters

### CH01 Framing Architecture Problems and Decision Boundaries

**Reader outcome:** Turn an ambiguous request into a bounded decision statement, separating problem, constraint, assumption, and proposed solution.
**Diagram opportunities:** (1) request-to-decision boundary; (2) problem/constraint/assumption/solution map; (3) scope-in/scope-out context; (4) stakeholder goal conflict; (5) requirement change impact.

### CH02 Systems Thinking for Architecture

**Reader outcome:** Identify feedback loops, stocks/flows, delays, and second-order effects before changing a complex system.
**Diagram opportunities:** (1) reinforcing/balancing feedback loop; (2) stock-and-flow model; (3) delayed effect timeline; (4) intervention side-effect map; (5) system boundary and external influences.

### CH03 Decomposition, Boundaries, and Dependency Reasoning

**Reader outcome:** Choose responsibilities and dependency directions that fit change, ownership, and operational boundaries.
**Diagram opportunities:** (1) responsibility decomposition; (2) dependency direction graph; (3) coupling versus cohesion map; (4) change-propagation path; (5) boundary alternatives.

### CH04 Evidence, Assumptions, and Uncertainty

**Reader outcome:** Separate observed facts, estimates, assumptions, and unknowns, then design evidence-gathering steps and decision thresholds.
**Diagram opportunities:** (1) claim/evidence/assumption ledger; (2) uncertainty-to-test path; (3) confidence and impact matrix; (4) decision threshold under uncertainty; (5) evidence freshness/revalidation.

### CH05 Reversibility, Optionality, and Decision Timing

**Reader outcome:** Apply reversibility and last-responsible-moment reasoning to pilots, migrations, and irreversible commitments.
**Diagram opportunities:** (1) reversibility spectrum; (2) commitment point and option expiry; (3) pilot-to-scale gate; (4) migration rollback boundary; (5) decision timing versus information arrival.

### CH06 Facilitating Architecture Trade-off Workshops

**Reader outcome:** Facilitate evidence-based trade-off reviews using scenarios, stakeholder priorities, and explicit disagreement.
**Diagram opportunities:** (1) workshop agenda and decision flow; (2) quality-attribute scenario; (3) stakeholder concern matrix; (4) option scoring and sensitivity; (5) disagreement-to-resolution path.

### CH07 Socio-Technical Architecture Reasoning

**Reader outcome:** Relate team structure, cognitive load, ownership, and communication to system boundaries and operating outcomes.
**Diagram opportunities:** (1) team/service topology; (2) cognitive-load allocation; (3) Conway feedback loop; (4) ownership handoff map; (5) reorganization/change impact.

### CH08 Architecture Pre-Mortems and Challenge Reviews

**Reader outcome:** Surface failure paths and disconfirming evidence before committing to high-impact architecture decisions.
**Diagram opportunities:** (1) pre-mortem timeline; (2) assumption challenge tree; (3) attack/failure scenario; (4) dissent and escalation protocol; (5) mitigation-to-owner map.

### CH09 Measuring Decision Outcomes and Reconsideration Triggers

**Reader outcome:** Define observable signals, review dates, and thresholds that indicate when a decision should be revisited.
**Diagram opportunities:** (1) decision hypothesis to metric; (2) trigger threshold state machine; (3) leading/lagging evidence; (4) review cadence and owner; (5) decision outcome feedback loop.

### CH10 Integrated Architecture Decision Clinics

**Reader outcome:** Apply requirements, options, evidence, trade-offs, stakeholders, and decision records to complete case-based architecture problems.
**Diagram opportunities:** (1) clinic workflow; (2) case context and constraints; (3) alternatives/trade-off map; (4) evidence and decision record; (5) follow-up validation and reconsideration.
