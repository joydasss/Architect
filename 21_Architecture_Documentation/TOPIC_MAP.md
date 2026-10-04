# Part 21 — Architecture Documentation Topic Map

This map defines coverage for Part 21's eleven documentation chapters. The part teaches how to make architecture visible, reviewable, and maintainable using complementary models, diagrams, decision records, and operating documents. Documentation supports decisions and execution; it does not replace architecture reasoning or current operational truth.

## Part-wide ownership boundaries

- Part 21 owns architecture documentation models and artifacts: C4, UML, ADRs, RFCs, diagrams, runbooks, playbooks, threat models, decision logs, and reviews.
- Part 01 CH03 owns general architecture decision reasoning and ADR intent; Part 07 owns HLD/LLD design workflow; Part 15 owns security threat-model fundamentals; Part 18 owns enterprise governance.
- Keep documentation proportional to risk and change. Establish owner, audience, update trigger, source of truth, and validation for each artifact.

## Chapters

### CH01 C4 Model

**Reader outcome:** Select context, container, component, and code-level views that answer stakeholder questions without implying false precision.
**Coverage:** C4 levels, scope, notation, boundaries, dynamic views, deployment context, and evolution.
**Diagram opportunities:** (1) context view; (2) container view; (3) component view; (4) zoom-level consistency; (5) dynamic interaction paired with static view.

### CH02 UML (Unified Modeling Language)

**Reader outcome:** Use appropriate UML diagrams and notation to communicate structure and behavior where precision matters.
**Coverage:** Use case, class, sequence, state, activity, component, deployment diagrams, semantics, and common misuse.
**Diagram opportunities:** (1) diagram-type selection; (2) class relationships; (3) sequence lifelines; (4) state transition; (5) deployment node mapping.

### CH03 ADR (Architecture Decision Record)

**Reader outcome:** Record context, decision, alternatives, consequences, and status so future teams can understand and revisit architectural choices.
**Coverage:** ADR structure, lifecycle, decision IDs, linking, supersession, scope, ownership, and repository organization.
**Boundaries:** Part 01 CH03 owns decision reasoning; this chapter owns ADR artifact and practice.
**Diagram opportunities:** (1) proposal-to-accepted lifecycle; (2) alternatives and criteria; (3) ADR dependency links; (4) superseding decision chain; (5) decision trigger to review.

### CH04 RFC (Request for Comments)

**Reader outcome:** Use an RFC process for changes requiring broad technical review before implementation.
**Coverage:** Problem statement, proposal, alternatives, review window, feedback disposition, decision authority, and relationship to ADRs.
**Diagram opportunities:** (1) RFC review workflow; (2) comment-to-resolution trace; (3) RFC-to-ADR transition; (4) stakeholder review matrix; (5) unresolved objection escalation.

### CH05 Sequence Diagrams

**Reader outcome:** Document time-ordered interactions, synchronous/asynchronous boundaries, errors, and ownership across components.
**Coverage:** Lifelines, messages, activation, fragments, async signals, timeouts, retries, and maintenance.
**Diagram opportunities:** (1) request/response flow; (2) async publish/consume; (3) retry/timeout fragment; (4) failure path; (5) sequence plus state invariant.

### CH06 Deployment Diagrams

**Reader outcome:** Communicate runtime placement, network zones, nodes, artifacts, and deployment dependencies.
**Coverage:** Nodes, environments, trust zones, network links, scaling, failure domains, and consistency with code/container views.
**Diagram opportunities:** (1) workload-to-node placement; (2) network trust zones; (3) multi-region deployment; (4) dependency and port map; (5) deployment view correlated with service topology.

### CH07 Runbooks

**Reader outcome:** Write executable operational procedures with trigger, prerequisites, safe actions, verification, escalation, and rollback.
**Coverage:** Incident context, command safety, permissions, expected output, decision branches, recovery, ownership, and maintenance.
**Diagram opportunities:** (1) symptom-to-diagnosis decision tree; (2) command/verification loop; (3) escalation path; (4) rollback gate; (5) runbook lifecycle/ownership.

### CH08 Playbooks

**Reader outcome:** Coordinate multi-role response and decision-making for scenarios that cannot be reduced to a fixed command sequence.
**Coverage:** Roles, objectives, injects, communications, decision points, exercise execution, evidence, and improvement actions.
**Diagram opportunities:** (1) incident role map; (2) scenario timeline; (3) decision and communication path; (4) exercise inject-to-response; (5) after-action improvement loop.

### CH09 Threat Models

**Reader outcome:** Document system assets, trust boundaries, threats, assumptions, mitigations, residual risks, and ownership.
**Coverage:** Data-flow diagrams, attacker goals, threat categories, risk, controls, validation, and model updates.
**Boundaries:** Part 15 owns threat-modeling method; this chapter owns the durable architecture artifact.
**Diagram opportunities:** (1) data-flow trust boundary; (2) threat-to-component matrix; (3) attack tree; (4) mitigation/evidence mapping; (5) architecture-change update trigger.

### CH10 Decision Logs

**Reader outcome:** Preserve lightweight records of decisions and rationale when a full ADR is unnecessary but traceability matters.
**Coverage:** Decision entry, owner, date, alternatives, rationale, evidence, status, and distinction from ADR/RFC.
**Diagram opportunities:** (1) decision entry lifecycle; (2) log-to-ADR escalation; (3) decision index by system; (4) change/supersession trace; (5) retrieval by stakeholder question.

### CH11 Architecture Reviews

**Reader outcome:** Prepare and conduct reviews that assess architecture against explicit goals, risks, constraints, and evidence.
**Coverage:** Review charter, participants, artifacts, scenarios, findings, actions, decision rights, and follow-up.
**Boundaries:** Part 18 owns enterprise review-board governance; Part 22 owns applied decision workshops.
**Diagram opportunities:** (1) review preparation-to-follow-up; (2) architecture view-to-quality scenario; (3) finding severity/owner matrix; (4) decision authority and escalation; (5) action closure evidence.
