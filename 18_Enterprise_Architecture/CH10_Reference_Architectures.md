# Reference Architectures

Part: [18 — Enterprise Architecture](PART_OVERVIEW.md)

A reference architecture is a reusable, bounded description of a class of solutions. It captures stable principles, responsibilities, interfaces, constraints, and proven variants while leaving context-specific decisions to solution teams. It is not a product catalog or a mandatory blueprint for every workload. Part 09 owns provider service guidance, Part 20 owns general architecture patterns, and Part 07 owns solution-specific design.

## Define Purpose and Boundaries

Start with a recurring decision or class of systems that would benefit from common guidance. Name intended users, goals, constraints, non-goals, required controls, and evidence that validates adoption. State what can vary, what must remain invariant, and who owns the reference architecture. Without these boundaries, a reference design becomes either too generic to help or so prescriptive that teams work around it.

```mermaid
flowchart TB
    Need[Recurring enterprise need] --> Scope[Define use cases and non-goals]
    Scope --> Principles[Set principles and invariants]
    Principles --> Layers[Describe capabilities and responsibilities]
    Layers --> Variants[Document supported variants]
    Variants --> Constraints[Record constraints and decision points]
    Constraints --> Evidence[Attach implementation and operation evidence]
    Evidence --> Audience[Publish for named consumers]
```

The reference architecture should answer which decisions it resolves and which remain open. Include assumptions such as scale, criticality, data classification, geographic needs, and operating maturity. If those assumptions do not hold, the consumer should know to select another variant or request a scoped exception.

## Describe Layers and Responsibilities

Organize the design by responsibility: user or channel, business capability, application services, data, integration, platform, security, and operations. Show ownership and interfaces, not just boxes. A layer is useful when it separates concerns and clarifies change boundaries; it should not imply a fixed technology product or deployment unit.

```mermaid
flowchart TB
    Channel[User and channel experience]
    Business[Business capabilities and workflow]
    Application[Application services and contracts]
    Data[Data products and ownership]
    Integration[Integration and event boundaries]
    Platform[Runtime and shared platform]
    Controls[Identity, security, observability, and operations]
    Channel --> Business
    Business --> Application
    Application --> Data
    Application --> Integration
    Application --> Platform
    Controls -. applies across .-> Channel
    Controls -. applies across .-> Business
    Controls -. applies across .-> Application
    Controls -. applies across .-> Data
    Controls -. applies across .-> Platform
```

For each boundary, specify the contract owner, failure behavior, and evidence required for implementation. Point to detailed security, data, cloud, and delivery standards rather than copying them into a second source that can drift.

## Make Variants and Constraints Explicit

A single reference design rarely fits every quality or regulatory profile. Define variation points such as synchronous versus asynchronous integration, regional versus centralized data, or managed versus self-operated runtime. State the trigger for each variant and its trade-offs. Do not present variants as interchangeable when they differ in recovery, cost, privacy, or support requirements.

```mermaid
flowchart LR
    Workload[Workload requirements] --> Criticality{Criticality and recovery need}
    Criticality -->|Standard| Shared[Shared platform variant]
    Criticality -->|High isolation| Dedicated[Dedicated runtime variant]
    Data[Data locality constraint] --> Locality{Can data cross region?}
    Locality -->|Yes| Central[Centralized data path]
    Locality -->|No| Regional[Regional processing path]
    Shared --> Decision[Record chosen variant and rationale]
    Dedicated --> Decision
    Central --> Decision
    Regional --> Decision
```

This decision view should point to measurable constraints such as recovery time, residency, capacity, or support ownership. A selection matrix without evidence turns into preference matching. Validate variants under realistic traffic and failure conditions before making them supported defaults.

## Instantiate and Govern Adoption

Consumers adapt a reference architecture into a solution architecture. The mapping should identify reused components, selected variants, local decisions, deviations, and validation plans. Adoption evidence can include conformance tests, threat review, operational readiness, and successful workload outcomes. Avoid requiring teams to recreate reference diagrams when a linked decision and test evidence are enough.

```mermaid
sequenceDiagram
    participant Ref as Reference architecture owner
    participant Team as Solution team
    participant Review as Domain or governance reviewer
    participant Ops as Operations owner
    Ref-->>Team: Publish constraints, variants, and evidence
    Team->>Team: Map workload requirements to reference
    Team->>Review: Submit selected variant and deviations
    Review-->>Team: Accept, request evidence, or grant scoped exception
    Team->>Ops: Validate support, monitoring, and recovery
    Ops-->>Team: Operational readiness evidence
    Team->>Ref: Report adoption gaps and outcomes
```

Governance should focus on invariants and material deviations. A reference architecture does not transfer responsibility for a solution's data, risk, or operations to its author. The consuming team owns implementation and evidence; the reference owner maintains the shared guidance and responds to recurring friction.

## Evolve the Reference Architecture

Review references when standards, regulatory obligations, incidents, costs, technology support, or workload characteristics change. Track version, owner, supported variants, deprecation date, and active consumers. A breaking change needs migration guidance and a compatibility window; otherwise consumers may remain on undocumented forks.

```mermaid
flowchart LR
    Signal[Incident, new constraint, support change, or adoption evidence] --> Assess[Assess affected variants and consumers]
    Assess --> Change{Material change required?}
    Change -->|No| Clarify[Clarify guidance or examples]
    Change -->|Yes| Draft[Create versioned revision]
    Draft --> Validate[Validate with representative consumers]
    Validate --> Publish[Publish change and migration window]
    Publish --> Migrate[Consumers adopt or request exception]
    Migrate --> Retire[Retire obsolete variant and track residual consumers]
    Clarify --> Monitor[Continue outcome review]
    Retire --> Monitor
```

Measure adoption, exception themes, implementation effort, incidents, and user outcomes. High adoption alone does not prove value; it can reflect mandate. Repeated exceptions may indicate a missing variant, poor usability, or a constraint that should be revisited.

## Worked Case: Enterprise Event-Driven Integration

An enterprise sees repeated use of point-to-point integrations with inconsistent security and recovery. A reference architecture defines event ownership, schema and compatibility expectations, identity, delivery guarantees, observability, and operational responsibility. It supports variants for low-volume notifications and high-criticality business events. The variants differ in replay expectations and recovery requirements.

A solution team maps an order-status workflow to the reference, chooses the high-criticality variant, and documents a regional data constraint. A conformance test verifies schema compatibility and identity; an operations review verifies replay ownership and incident procedures. Multiple teams later request a supported private-network variant, so the reference owner evaluates it, tests with representative consumers, and publishes a versioned update rather than approving unrelated exceptions indefinitely.

## Review Questions

1. Which decisions should a reference architecture resolve, and which remain local?
2. What assumptions make a variant valid?
3. What evidence demonstrates adoption beyond diagram similarity?
4. Who owns solution risk versus shared-reference maintenance?
5. Which signals trigger a breaking revision or retirement?

Reference architectures create leverage when they encode tested choices without erasing workload context. Bound their scope, name supported variants and assumptions, require evidence at adoption, and evolve them from real outcomes and consumer friction.
