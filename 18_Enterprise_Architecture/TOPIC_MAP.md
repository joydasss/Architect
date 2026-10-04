# Part 18 — Enterprise Architecture Topic Map

This map defines coverage for Part 18's eleven enterprise-architecture chapters. The part explains how organization-wide strategy, capabilities, information, applications, technology, governance, and reference designs are coordinated. Frameworks help describe and govern change. Outcomes and accountable decisions remain the goal.

## Part-wide ownership boundaries

- Part 18 owns enterprise-level architecture viewpoints, capability mapping, governance, review boards, and framework use.
- Part 01 owns software-architecture foundations and the Solution Architect role; Part 07 owns solution HLD/LLD; Part 21 owns architecture documentation formats; Part 22 owns applied decision workshops.
- Treat TOGAF, Zachman, and ArchiMate as distinct framework/modeling approaches with different purposes. Do not conflate a framework, ontology, notation, and governance process.

## Cross-part stakeholders and scenarios

Business leaders need strategy-to-capability traceability; portfolio owners need investment and dependency views; solution teams need guardrails without unnecessary central bottlenecks. Quality scenarios include a merger changing capabilities, a major platform replacement, conflicting standards across business units, and a review board deciding an exception.

## Chapters

### CH01 TOGAF (The Open Group Architecture Framework)

**Reader outcome:** Apply TOGAF's architecture-development and governance concepts when they improve enterprise change coordination.
**Coverage:** Architecture Development Method (ADM), phases, repository, content framework, governance, tailoring, and limits.
**Boundaries:** Part 07 owns solution HLD; Part 21 owns diagram/documentation notation.
**Diagram opportunities:** (1) ADM cycle; (2) requirement/change impact through phases; (3) architecture repository; (4) governance checkpoint; (5) tailored versus full framework path.

### CH02 Zachman Framework

**Reader outcome:** Use the Zachman classification schema to identify missing perspectives and artifacts without mistaking it for a stepwise process.
**Coverage:** Perspectives, interrogatives, cells, stakeholder views, completeness, and use alongside other methods.
**Boundaries:** CH01 owns TOGAF process; Part 21 owns documentation notations.
**Diagram opportunities:** (1) perspective/interrogative matrix; (2) one system concept across viewpoints; (3) artifact completeness map; (4) stakeholder-to-question trace; (5) Zachman versus process framework distinction.

### CH03 ArchiMate

**Reader outcome:** Model business, application, and technology relationships with ArchiMate elements and viewpoints.
**Coverage:** Layering, elements/relationships, viewpoints, motivation, implementation/migration, and model governance.
**Boundaries:** Part 21 owns general UML/C4; CH01/02 own enterprise framework contexts.
**Diagram opportunities:** (1) business-application-technology layers; (2) capability-to-application realization; (3) value stream/service relationship; (4) implementation/migration plateau; (5) viewpoint selection by stakeholder.

### CH04 Business Architecture

**Reader outcome:** Relate strategy to capabilities, value streams, organization, information, and investment decisions.
**Coverage:** Business capability maps, value streams, organization, information concepts, outcomes, and change impact.
**Boundaries:** Part 02 owns product strategy/discovery; CH10 owns capability-map mechanics.
**Diagram opportunities:** (1) strategy-to-capability chain; (2) capability heat map; (3) value-stream stages and outcomes; (4) org-to-capability ownership; (5) change impact across capabilities.

### CH05 Application Architecture

**Reader outcome:** Inventory and evolve application boundaries, dependencies, lifecycle, and portfolio roles.
**Coverage:** Application portfolio, ownership, interfaces, lifecycle, duplication, modernization, and dependency risk.
**Boundaries:** Part 07 owns solution design; Part 20 owns architecture patterns; Part 09 owns cloud service detail.
**Diagram opportunities:** (1) application portfolio map; (2) dependency graph and centrality; (3) lifecycle/technology risk matrix; (4) modernization disposition options; (5) application-to-capability trace.

### CH06 Data Architecture

**Reader outcome:** Govern enterprise data domains, ownership, flows, quality, lineage, and access across applications.
**Coverage:** Data domains, master/reference data, lifecycle, lineage, integration, stewardship, governance, and analytics boundaries.
**Boundaries:** Part 06 owns database mechanics; Part 16 owns AI data/model techniques; Part 17 owns AI solution composition.
**Diagram opportunities:** (1) domain/data-owner map; (2) system-of-record flow; (3) lineage from source to use; (4) master-data synchronization; (5) governance/access lifecycle.

### CH07 Technology Architecture

**Reader outcome:** Govern platforms, standards, technology lifecycle, and shared capabilities across an enterprise.
**Coverage:** Technology portfolio, standards, platform services, lifecycle, exceptions, technical debt, sourcing, and operational responsibility.
**Boundaries:** Part 09 owns cloud products; Part 13 owns delivery tooling; Part 19 owns performance engineering.
**Diagram opportunities:** (1) technology portfolio layers; (2) standard/exception decision path; (3) lifecycle support matrix; (4) platform capability dependency; (5) technology debt and risk map.

### CH08 Architecture Governance

**Reader outcome:** Establish proportionate decision rights, principles, standards, exceptions, and assurance without making governance a paperwork gate.
**Coverage:** Governance bodies, delegated authority, principles, standards, waivers, compliance evidence, escalation, and feedback.
**Boundaries:** Part 22 owns decision facilitation; CH09 owns review board operation.
**Diagram opportunities:** (1) decision rights and escalation; (2) standard-to-exception lifecycle; (3) governance evidence path; (4) risk-based review gate; (5) feedback from delivery to standards.

### CH09 Architecture Review Boards

**Reader outcome:** Run architecture review boards that make timely, evidence-based decisions with clear scope, authority, and follow-up.
**Coverage:** Charter, membership, intake, evidence, decision records, exceptions, meeting design, conflict handling, and effectiveness measures.
**Boundaries:** Part 01 CH03 owns ADRs; Part 22 owns facilitated trade-off workshops.
**Diagram opportunities:** (1) review intake-to-decision workflow; (2) board authority versus delivery ownership; (3) evidence packet and questions; (4) exception approval/expiry; (5) action follow-up and effectiveness loop.

### CH10 Reference Architectures

**Reader outcome:** Create reusable, bounded reference designs that guide teams while preserving context-specific choice.
**Coverage:** Reference architecture purpose, principles, views, implementation variants, constraints, evolution, and adoption evidence.
**Boundaries:** Part 09 owns provider service guidance; Part 20 owns general patterns; this chapter owns enterprise-scoped reusable designs.
**Diagram opportunities:** (1) reference architecture layers; (2) variant points and constraints; (3) reference design to solution instance; (4) adoption and exception path; (5) reference architecture evolution.

### CH11 Capability Mapping

**Reader outcome:** Map business capabilities to value, ownership, applications, data, and investment priorities.
**Coverage:** Capability taxonomy, decomposition, heat maps, maturity, ownership, value-stream linkage, portfolio planning, and validation.
**Boundaries:** CH04 owns broader business architecture; Part 02 owns product/market strategy.
**Diagram opportunities:** (1) capability hierarchy; (2) capability heat map; (3) capability-to-application/data mapping; (4) investment priority view; (5) capability change impact.
