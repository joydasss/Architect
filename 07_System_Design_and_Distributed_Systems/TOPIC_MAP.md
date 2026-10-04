# Part 07 — System Design and Distributed Systems Topic Map

This map backfills the coverage contract for Part 07's 19 chapters. The first chapters turn requirements into designs; the remaining chapters explain distributed-systems guarantees and patterns. Part 07 owns provider-neutral system design and general distributed behavior, while domain-specific implementations remain with their owning parts.

## Part-wide ownership boundaries

- Part 07 owns functional/non-functional requirements, high- and low-level system design, and general distributed-systems theory and patterns.
- Part 01 owns the Solution Architect role and general decision-thinking foundations. Part 07 applies those methods to system design.
- Part 06 owns database engine internals; Part 07 owns general distributed data, replication, and transaction semantics. Database chapters recap rather than re-derive these abstractions.
- Part 05 owns OS, network, and protocol mechanics; Part 08 owns API styles and gateway mechanics; Part 13 owns delivery pipelines; Part 14 owns observability; Part 15 owns security foundations.
- Distinguish service-level behavior from one product's implementation. State failure assumptions, timing, durability, ordering, and consistency semantics precisely.

## Cross-part stakeholders and quality scenarios

- Product and business stakeholders need a design tied to user journeys, scope, constraints, and measurable outcomes.
- Engineers need implementable boundaries, data contracts, failure behavior, and operational ownership.
- Site reliability engineering (SRE) and platform teams need explicit service-level objectives (SLOs), capacity assumptions, recovery plans, observability, and safe evolution.
- Important scenarios include a requirement change after design approval; a regional partition during writes; a leader crash during a state transition; duplicate event delivery; and a retry after an uncertain response.

## Requirements and Design

### CH01 Functional Requirements

**Reader outcome:** Convert stakeholder intent into observable behaviors, scenarios, data constraints, and acceptance evidence.
**Coverage:** Actors, use cases, user journeys, functional scope, business rules, inputs/outputs, acceptance criteria, assumptions, and traceability.
**Decision/evidence:** Resolve ambiguity, conflicting stakeholders, and scope boundaries; validate with representative scenarios and acceptance examples.
**Diagram opportunities:** (1) actor-to-system context; (2) use-case interaction; (3) requirement-to-acceptance trace; (4) happy/error path state flow; (5) scope inclusion/exclusion boundary.

### CH02 Non-Functional Requirements

**Reader outcome:** Express quality goals as measurable scenarios and trade-offs rather than vague adjectives.
**Coverage:** Availability, reliability, scalability, elasticity, latency, throughput, durability, security, cost, SLO/SLA/SLI, capacity estimation, and quality-attribute interactions.
**Decision/evidence:** Define workload, conditions, response, and measure; compare targets with cost, feasibility, and risk.
**Diagram opportunities:** (1) quality-attribute scenario template; (2) latency percentile distribution; (3) capacity estimate from demand to resources; (4) durability compounding across replicas; (5) quality-attribute trade-off matrix.

### CH03 High-Level Design (HLD)

**Reader outcome:** Communicate a system's major components, boundaries, data flows, deployment shape, and quality decisions to stakeholders.
**Coverage:** Context/container/component views, system boundaries, interfaces, critical paths, data stores, deployment and failure domains, constraints, and review evidence.
**Decision/evidence:** Match view to stakeholder concern; validate key assumptions and quality scenarios rather than treating diagrams as implementation specifications.
**Diagram opportunities:** (1) C4 context view; (2) container/component decomposition; (3) request/data flow; (4) deployment and failure domains; (5) quality scenario mapped to architecture.

### CH04 Low-Level Design (LLD)

**Reader outcome:** Specify component responsibilities, APIs, state transitions, data structures, and interactions sufficiently for implementation and review.
**Coverage:** Object-oriented design, SOLID, design patterns, domain-driven design (DDD), event modeling, interfaces, error paths, concurrency assumptions, and test seams.
**Decision/evidence:** Avoid speculative abstraction; state invariants, ownership, dependencies, and performance constraints.
**Diagram opportunities:** (1) class/component collaboration; (2) sequence for a critical operation; (3) state machine and invariants; (4) domain/event model; (5) dependency inversion boundary.

## Distributed Systems

### CH05 CAP Theorem

**Reader outcome:** Use the Consistency, Availability, and Partition tolerance (CAP) model to reason about behavior during network partitions without misusing it as a database ranking.
**Coverage:** Formal terms, partition condition, operation semantics, linearizability versus availability, Gilbert-Lynch result, recovery after partition, and the limits of Consistency, Availability, and Partition tolerance (CAP) reasoning.
**Decision/evidence:** State which operations block, reject, or return stale data during a partition; do not claim a system “chooses two” in normal operation.
**Diagram opportunities:** (1) partition between replicas; (2) consistency/availability outcome table; (3) read/write operation timeline; (4) partition recovery and reconciliation; (5) CAP versus normal-latency behavior.

### CH06 PACELC

**Reader outcome:** Extend partition-time reasoning with latency/consistency trade-offs when the system is operating normally.
**Coverage:** Partition branch (availability versus consistency), Else branch (latency versus consistency), system classification, quorum/replication configuration, and workload-specific interpretation of Partition, Availability, Else, Latency, and Consistency (PACELC).
**Decision/evidence:** Tie the classification to a specific operation and consistency contract, not a product label.
**Diagram opportunities:** (1) PACELC decision quadrants; (2) normal-operation latency/consistency curve; (3) partition-mode operation outcomes; (4) configuration knobs mapped to quadrant; (5) request path under local versus remote quorum.

### CH07 Consensus

**Reader outcome:** Explain how distributed nodes agree on a value or log despite failures and distinguish safety from liveness.
**Coverage:** Consensus properties, quorum intersection, leader-based protocols, term/epoch, log replication, commit index, membership changes, safety/liveness, and failure assumptions.
**Decision/evidence:** State the failure model, quorum size, and consequences of losing a majority; avoid implying consensus solves data-model or availability problems automatically.
**Diagram opportunities:** (1) leader proposal and quorum acknowledgment; (2) log replication/commit index; (3) quorum intersection; (4) leader failure and election; (5) membership change with safety barrier.

### CH08 Leader Election

**Reader outcome:** Select and operate a leader-election mechanism with fencing and leases that prevent stale leaders from performing conflicting work.
**Coverage:** Election triggers, terms/epochs, leases, split-brain, fencing tokens, failure detection, renewal, and operational recovery.
**Decision/evidence:** Handle pauses, partitions, and clock uncertainty; a lease without downstream fencing may permit stale writes.
**Diagram opportunities:** (1) election and term transition; (2) lease renewal/expiry timeline; (3) split-brain under network partition; (4) fencing-token enforcement; (5) failover and safe recovery.

### CH09 Gossip Protocols

**Reader outcome:** Use gossip for scalable membership and state dissemination while understanding convergence, staleness, and failure-detector limits.
**Coverage:** Peer selection, rumor propagation, membership, suspicion, convergence, anti-entropy, infection-style dissemination, and operational tuning.
**Decision/evidence:** Balance convergence speed, network fan-out, false suspicion, and cluster size; gossip is not a consensus protocol.
**Diagram opportunities:** (1) peer-to-peer rumor spread; (2) convergence over rounds; (3) suspicion and refutation; (4) anti-entropy state repair; (5) fan-out versus convergence-time trade-off.

### CH10 Replication

**Reader outcome:** Compare replication topologies and data-conflict strategies for general distributed services and stateful components.
**Coverage:** Leader/follower, multi-leader, leaderless, synchronous/asynchronous replication, conflict resolution, conflict-free replicated data types (CRDTs), vector clocks, log/queue replication, and non-database state.
**Decision/evidence:** Define durability, read-your-writes, ordering, conflict, and recovery semantics; test lag and partition scenarios.
**Boundaries:** Part 06 CH07 owns database-specific replication products and mechanisms; Part 07 owns general distributed replication patterns.
**Diagram opportunities:** (1) leader/follower versus multi-leader topologies; (2) asynchronous replication lag; (3) vector-clock concurrent versions; (4) CRDT merge convergence; (5) queue/log replication and consumer recovery.

### CH11 Partitioning

**Reader outcome:** Partition distributed data and work to improve scale while preserving routing, ownership, and rebalancing behavior.
**Coverage:** Partition keys, hash/range placement, consistent hashing, routing directories, hotspots, rebalancing, locality, and cross-partition operations.
**Decision/evidence:** Choose keys from access patterns and growth; measure skew, movement cost, fan-out, and hot partitions.
**Boundaries:** Part 06 owns database partitioning and sharding implementations; this chapter owns general distributed partitioning principles.
**Diagram opportunities:** (1) key-to-partition routing; (2) range/hash/consistent-hash placement; (3) hotspot skew; (4) rebalance movement; (5) cross-partition request fan-out.

### CH12 Distributed Transactions

**Reader outcome:** Coordinate state changes across services and stores while making atomicity, blocking, retries, and recovery explicit.
**Coverage:** Dual-write problem, two-phase commit (2PC), three-phase commit (3PC), coordinator failure, transactional outbox, idempotent consumers, and boundary redesign.
**Decision/evidence:** Compare distributed coordination with asynchronous workflows; define in-doubt handling and duplicate delivery semantics.
**Boundaries:** Part 06 CH08 owns database transaction fundamentals; CH13 owns Saga design and compensation depth.
**Diagram opportunities:** (1) dual-write inconsistency window; (2) 2PC prepare/commit and coordinator crash; (3) 3PC phase transition; (4) outbox relay to broker; (5) transaction boundary redesign.

### CH13 Saga Pattern

**Reader outcome:** Design long-running distributed workflows with durable orchestration/choreography, compensations, retries, and operator visibility.
**Coverage:** Saga structure, state persistence, compensation semantics, pivot transactions, retry classification, dead-letter/escalation, recovery, and observability.
**Decision/evidence:** Compensation is a new business action, not time reversal. Define which actions are reversible, retryable, or require human escalation.
**Boundaries:** Part 06 CH08 and CH12 cover transaction mechanics; CH16 owns idempotency.
**Diagram opportunities:** (1) orchestration state machine; (2) choreography event chain; (3) forward action and compensation; (4) pivot and irreversible boundary; (5) timeout/retry/escalation state.

### CH14 CQRS (Command Query Responsibility Segregation)

**Reader outcome:** Separate command/write and query/read models when their scaling, shape, or ownership requirements materially differ.
**Coverage:** Command validation, event/state updates, projections, read models, synchronization lag, adoption spectrum, and CQRS versus event sourcing.
**Decision/evidence:** Avoid separation without independent needs; define read-your-own-writes, projection rebuild, and failure handling.
**Boundaries:** Part 06 owns database views and caches; CH15 owns event-sourced source-of-truth mechanisms.
**Diagram opportunities:** (1) command/read path separation; (2) projection update from event/log; (3) read-model lag; (4) projection rebuild; (5) CQRS adoption spectrum.

### CH15 Event Sourcing

**Reader outcome:** Store domain changes as an append-only event history and derive current state through replay and projections.
**Coverage:** Event store, aggregate/version checks, replay, snapshots, upcasting/schema evolution, projections, retention, and relation to CQRS.
**Decision/evidence:** Treat event schema as a long-lived contract; validate replay correctness, projection recovery, and event retention costs.
**Boundaries:** Part 06 owns write-ahead logs and engine transaction logs; CH14 owns CQRS separation; CH13 owns Saga workflow design.
**Diagram opportunities:** (1) command to event append; (2) replay from history; (3) snapshot plus event tail; (4) schema upcast chain; (5) event log to projection rebuild.

### CH16 Idempotency

**Reader outcome:** Make retried operations safe by defining stable operation identity, deduplication scope, and replay behavior.
**Coverage:** At-least-once delivery, idempotency keys, request/result persistence, duplicate windows, concurrent duplicates, retention, and external side effects.
**Decision/evidence:** Specify key scope and lifetime; test timeout after commit, concurrent retry, and key reuse with changed payload.
**Boundaries:** Part 08 owns HTTP idempotent method semantics; CH12/13 own distributed transaction and Saga applications.
**Diagram opportunities:** (1) retry with idempotency-key lookup; (2) concurrent duplicate request race; (3) key/result state lifecycle; (4) downstream side-effect boundary; (5) retention-window failure case.

### CH17 Exactly Once Processing

**Reader outcome:** Explain what exactly once processing can guarantee within a defined system boundary and why end-to-end claims require idempotency and atomicity.
**Coverage:** Delivery semantics, producer/consumer acknowledgments, offsets, transactions, deduplication, replay, and end-to-end side effects.
**Decision/evidence:** Name the atomic boundary and external side effects; test crash points before/after commit and acknowledgment.
**Boundaries:** CH16 owns idempotency; Part 06 owns database transaction behavior; broker-specific implementation belongs to the relevant product part.
**Diagram opportunities:** (1) at most once, at least once, and exactly once delivery comparison; (2) consume-process-commit sequence; (3) crash between side effect and offset; (4) transactional outbox/inbox boundary; (5) deduplication state lifecycle.

### CH18 Ordering Guarantees

**Reader outcome:** Define required event/request ordering and choose the scope, sequencing mechanism, and failure behavior that enforce it.
**Coverage:** Total/partial/per-key order, sequence numbers, partitions, causal order, reordering buffers, late events, and head-of-line costs.
**Decision/evidence:** State the key or scope over which order matters; measure throughput and latency costs of stronger ordering.
**Boundaries:** Part 08 owns API request ordering expectations; Part 06 owns engine-specific transaction ordering; CH09 owns gossip dissemination.
**Diagram opportunities:** (1) total versus per-key ordering; (2) sequence-number gap and buffer; (3) partition-local order; (4) causal event dependencies; (5) head-of-line blocking trade-off.

### CH19 Deduplication

**Reader outcome:** Detect and suppress repeated messages or effects within a declared identity and time window.
**Coverage:** Duplicate sources, fingerprints, idempotency keys, inbox tables, retention windows, out-of-order events, storage cost, and false-positive risk.
**Decision/evidence:** Choose deduplication identity and TTL from delivery/replay behavior; test legitimate repeats and delayed duplicates.
**Boundaries:** CH16 owns general idempotency contracts; Part 06 owns unique constraints and database storage details.
**Diagram opportunities:** (1) duplicate delivery and inbox check; (2) key/fingerprint decision; (3) time-window retention; (4) out-of-order replay; (5) storage-cost versus duplicate-risk trade-off.
