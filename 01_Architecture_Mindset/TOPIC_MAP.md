# Part 01 — Architecture Mindset Topic Map

This map backfills the coverage contract for Part 01's three completed chapters. The part establishes what software architecture is, who is accountable for it, and how significant design decisions are reasoned about. Later technical parts apply these foundations in their domains; they should recap and link core concepts rather than redefine them.

## Part-wide ownership boundaries

- Part 01 owns the foundational definition and vocabulary of software architecture, the Solution Architect role, and general architecture decision reasoning.
- Part 22 owns applied decision clinics and workshops. It uses Part 01 CH03's architecture decision records (ADRs), Architecture Tradeoff Analysis Method (ATAM), reversibility, quality-attribute scenarios, and general decision loop without re-teaching them.
- Part 18 owns enterprise architecture structures and governance; Part 20 owns architecture patterns; Part 21 owns architecture documentation notations. These parts apply Part 01 foundations to their own scope.
- Domain-specific architecture chapters own their technical decisions and mechanisms. Part 01 supplies the reusable reasoning vocabulary but does not prescribe one technology or topology.

## Cross-part stakeholders and assumptions

- Engineers need a precise model of architecture that connects structural decisions to quality attributes, constraints, and delivery consequences.
- Solution Architects need clear responsibility boundaries with product, engineering, security, operations, and enterprise architecture roles.
- Engineering leaders need decision records and review practices that preserve rationale without creating process for its own sake.
- Assume the reader can follow a software system and its stakeholders but may not have formal architecture training. Distinguish architecture from code-level design, job title from accountability, and a decision outcome from the reasoning that produced it.
- Important quality scenarios include a team changing a foundational choice after new evidence, an architect handing a decision to a successor, an organization separating architecture accountability from implementation authority, and a review identifying a costly irreversible decision before implementation.

## CH01 What Is Software Architecture?

**Reader outcome:** Define software architecture as consequential system structure and design decisions, and explain why those decisions matter beyond individual classes or code changes.

**Coverage and mechanisms:** Historical evolution of the discipline; architecture versus detailed design and implementation; components, connectors, boundaries, and system structure; quality attributes and architecturally significant requirements; coupling and cohesion; technical debt as a consequence of deferred structural choices; Conway's Law and organizational influence; architecture as an evolving set of decisions rather than one diagram.

**Decision concerns and evidence:** Which decisions are difficult or expensive to change; how a structural choice affects quality attributes; what context makes an architecture description useful; and how organizational structure can reinforce or undermine system boundaries. Evidence includes dependency maps, deployment topology, change history, failure modes, and measurable quality scenarios.

**Boundaries:** CH02 owns the Solution Architect's role and accountability. CH03 owns decision methods and ADR practice. Part 20 owns pattern catalogs; Part 21 owns documentation models; domain parts own their technical mechanisms.

**Diagram opportunities:** (1) architecture decisions from stakeholder need to system structure; (2) component/connector boundary with runtime and ownership views; (3) quality-attribute scenario mapped to architectural response; (4) coupling/cohesion trade-off across module boundaries; (5) organization-to-system Conway influence loop.

## CH02 Role of a Solution Architect

**Reader outcome:** Describe the Solution Architect's responsibilities across a solution lifecycle and distinguish accountable architecture work from adjacent job titles and organizational structures.

**Coverage and mechanisms:** Historical evolution of the role; responsibility for end-to-end technical coherence; translation between business/product needs and technical constraints; decision facilitation and documentation; collaboration with engineering, product, operations, security, and enterprise architecture; role variants across organizations; authority, influence, and accountability; lifecycle involvement from discovery through operation; common failure modes such as ivory-tower design or unowned decisions.

**Decision concerns and evidence:** When the role is a dedicated position versus a responsibility distributed across senior engineers; how decision rights align with delivery ownership; how architects remain engaged after approval; and how to measure useful outcomes rather than diagram volume. Evidence includes decision turnaround, unresolved constraints, implementation feedback, operational outcomes, and stakeholder alignment.

**Boundaries:** CH01 owns the definition of software architecture. CH03 owns the reasoning frameworks used to evaluate trade-offs. Part 18 owns enterprise-level role and governance structures; Part 22 applies decision practice in workshops.

**Diagram opportunities:** (1) stakeholder and responsibility map for a solution architect; (2) lifecycle swimlane from discovery to operations; (3) decision-rights boundary between architect, product, engineering, and operations; (4) communication translation between business outcome and technical design; (5) role variants mapped by organizational context and authority.

## CH03 Architecture Thinking

**Reader outcome:** Reason about significant architecture choices under uncertainty, surface trade-offs explicitly, and preserve rationale so decisions can be revisited with new evidence.

**Coverage and mechanisms:** Decision classification and reversibility; essential versus accidental complexity; systems thinking and second-order effects; quality-attribute-driven analysis; stakeholder concerns and constraints; cognitive bias and uncertainty; alternatives and trade-off records; ADR structure and lifecycle; ATAM-style scenario analysis; decision review and reconsideration triggers.

**Decision concerns and evidence:** Avoid false certainty, technology-first framing, and decisions without an owner or revisit condition. Compare options against measurable scenarios, explicit assumptions, costs of change, and failure consequences. Evidence includes ADRs, quality-attribute scenarios, prototypes, operational data, and changed assumptions.

**Boundaries:** CH01 owns architecture vocabulary; CH02 owns role accountability. Part 22 owns applied workshops and decision clinics. Technical chapters own domain-specific trade-offs and should use CH03's method without re-teaching it.

**Diagram opportunities:** (1) decision loop from trigger through evidence, choice, and revisit; (2) reversibility-cost spectrum with commitment points; (3) ATAM scenario flow from stimulus to response measure; (4) alternative comparison against quality attributes and constraints; (5) ADR lifecycle from proposed through accepted, superseded, or deprecated.
