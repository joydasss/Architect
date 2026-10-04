# Part 20 — Architecture Patterns Topic Map

This map defines coverage for Part 20's eighteen architecture-pattern chapters. The part catalogs reusable structural and interaction patterns and explains their fit, consequences, failure modes, and alternatives. A pattern is a design vocabulary. It is neither an implementation recipe nor a guarantee of quality.

## Part-wide ownership boundaries

- Part 20 owns general architecture pattern definitions and decision criteria.
- Part 07 owns distributed-systems semantics and patterns such as Saga/CQRS/event sourcing at systems level; Part 06 owns database-specific implementations; Part 12 owns Kubernetes patterns; Part 10 owns cloud-specific composition.
- Apply patterns only when their motivating forces and quality goals are present. Distinguish pattern name from framework/vendor implementation.

## Cross-part stakeholders and scenarios

Architects need alternatives and consequences; teams need clear boundaries and migration implications; operators need failure/observability consequences. Scenarios include a monolith with modular boundaries, a service decomposition increasing operational overhead, a plugin failure isolating the host, and an event-driven design with duplicate delivery.

## Chapters

### CH01 Layered Architecture

**Reader outcome:** Structure responsibilities into layers while controlling dependency direction and change propagation.
**Coverage:** Presentation/application/domain/data layers, allowed dependencies, layering variants, violations, and trade-offs.
**Diagram opportunities:** (1) layer stack and responsibilities; (2) request flow through layers; (3) dependency inversion boundary; (4) cross-layer shortcut anti-pattern; (5) modular-monolith layering.

### CH02 Hexagonal Architecture

**Reader outcome:** Isolate domain logic behind ports and adapters so infrastructure changes do not dominate core behavior.
**Coverage:** Ports, primary/secondary adapters, application core, test doubles, and boundary trade-offs.
**Diagram opportunities:** (1) core-port-adapter topology; (2) inbound/outbound request paths; (3) adapter substitution; (4) test harness through a port; (5) dependency direction.

### CH03 Clean Architecture

**Reader outcome:** Apply inward dependency rules to organize policy, use cases, interfaces, and implementation details.
**Coverage:** Entities/use cases/interface adapters/frameworks, dependency rule, boundaries, data transfer, and practical limits.
**Diagram opportunities:** (1) concentric responsibility rings; (2) dependency arrows inward; (3) use-case boundary; (4) external framework adapter; (5) dependency-rule violation.

### CH04 Onion Architecture

**Reader outcome:** Keep domain model and policies independent of infrastructure through layered dependency inversion.
**Coverage:** Domain core, services, repositories, infrastructure, dependency inversion, testing, and comparison with Clean/Hexagonal.
**Diagram opportunities:** (1) onion layers; (2) repository interface/implementation; (3) dependency inversion; (4) domain test boundary; (5) pattern comparison.

### CH05 Microservices

**Reader outcome:** Decide when independently deployable services are worth distributed ownership, data, network, and operational complexity.
**Coverage:** Service boundaries, autonomy, data ownership, communication, deployment, failure isolation, decomposition, and migration.
**Boundaries:** Part 07 owns distributed transactions/replication; Part 10 owns cloud composition; Part 12 owns Kubernetes.
**Diagram opportunities:** (1) monolith-to-service decomposition; (2) service/data ownership; (3) synchronous dependency fan-out; (4) independent deployment and failure; (5) decomposition decision tree.

### CH06 SOA (Service-Oriented Architecture)

**Reader outcome:** Understand enterprise service reuse, contracts, governance, and mediation, and distinguish SOA from modern microservices claims.
**Coverage:** Service contracts, shared services, enterprise service bus, governance, integration, coupling, and migration.
**Diagram opportunities:** (1) service consumer/provider graph; (2) ESB mediation path; (3) contract and governance boundary; (4) shared-service bottleneck; (5) SOA/microservices comparison.

### CH07 Event-Driven Architecture

**Reader outcome:** Design producers, brokers, consumers, and event contracts for decoupling while preserving delivery and operability guarantees.
**Coverage:** Events versus commands, pub/sub, queues, event streams, schemas, ordering, retries, and observability.
**Boundaries:** Part 07 owns event processing semantics; Part 09 owns messaging products.
**Diagram opportunities:** (1) producer-broker-consumer topology; (2) event versus command flow; (3) fan-out subscriptions; (4) retry/dead-letter path; (5) schema evolution.

### CH08 Serverless

**Reader outcome:** Apply serverless patterns where managed execution improves delivery and scaling without hiding runtime, state, and cost constraints.
**Coverage:** Functions/events, managed scaling, cold starts, statelessness, composition, limits, and operational visibility.
**Boundaries:** Part 09 owns provider serverless services; Part 13 owns deployment methods.
**Diagram opportunities:** (1) event-triggered function; (2) cold-start lifecycle; (3) state externalization; (4) function workflow composition; (5) serverless/container/VM choice.

### CH09 CQRS (Command Query Responsibility Segregation)

**Reader outcome:** Separate read/write models only when their differing workloads, scale, or ownership justify synchronization and consistency costs.
**Coverage:** Command/query split, projections, lag, updates, consistency, and adoption spectrum.
**Boundaries:** Part 07 CH14 owns distributed CQRS mechanics; Part 06 owns database materialized views.
**Diagram opportunities:** (1) command/read model paths; (2) projection update; (3) read lag; (4) partial adoption spectrum; (5) operational rebuild.

### CH10 Saga Pattern

**Reader outcome:** Coordinate long-running multi-service workflows with durable progress and business compensations.
**Coverage:** Orchestration/choreography, steps, compensation, retries, pivot, idempotency, and observability.
**Boundaries:** Part 07 CH13 owns Saga system design; Part 06 CH08 owns transaction mechanisms.
**Diagram opportunities:** (1) orchestrated saga; (2) choreographed event flow; (3) forward/compensation path; (4) pivot and irreversible action; (5) failure/retry state.

### CH11 Event Sourcing

**Reader outcome:** Use append-only domain events as the source of truth when replay, audit, or temporal reconstruction justifies lifecycle costs.
**Coverage:** Event store, aggregates, replay, snapshots, schema evolution, projections, and retention.
**Boundaries:** Part 07 CH15 owns event sourcing mechanics; Part 06 owns database engine storage.
**Diagram opportunities:** (1) command-to-event write; (2) state replay; (3) snapshot plus tail; (4) upcasting; (5) projection rebuild.

### CH12 Actor Model

**Reader outcome:** Model isolated stateful actors communicating by messages and understand mailbox, supervision, and distribution trade-offs.
**Coverage:** Actor identity/state, mailbox, message delivery, supervision, scheduling, location transparency, and failure.
**Boundaries:** Part 05 owns OS threads/processes; Part 07 owns distributed delivery semantics.
**Diagram opportunities:** (1) actor/mailbox topology; (2) message-driven state transition; (3) supervision tree; (4) mailbox overload; (5) actor placement/failure recovery.

### CH13 Pipeline Pattern

**Reader outcome:** Compose stages that transform data with explicit ordering, backpressure, concurrency, and recovery.
**Coverage:** Stages, queues, parallelism, backpressure, retries, ordering, and observability.
**Boundaries:** Part 07 owns stream processing semantics; Part 13 owns CI/CD pipelines.
**Diagram opportunities:** (1) pipeline stages; (2) bounded queue and backpressure; (3) parallel stage ordering; (4) retry/dead-letter; (5) throughput bottleneck migration.

### CH14 Plugin Architecture

**Reader outcome:** Extend a host through stable plugin contracts while constraining compatibility, trust, versioning, and failure isolation.
**Coverage:** Extension points, discovery, loading, API contracts, sandboxing, lifecycle, and compatibility.
**Diagram opportunities:** (1) host/plugin boundary; (2) plugin discovery/load lifecycle; (3) contract/version compatibility; (4) isolation and permissions; (5) plugin failure containment.

### CH15 Microkernel Architecture

**Reader outcome:** Keep a minimal core stable while moving optional capabilities into replaceable services or plug-ins.
**Coverage:** Core services, extension modules, communication contracts, deployment, and trade-offs.
**Diagram opportunities:** (1) microkernel core/extensions; (2) extension loading; (3) core-to-plugin API; (4) optional feature failure; (5) microkernel versus layered design.

### CH16 Space-Based Architecture

**Reader outcome:** Scale high-volume stateful workloads by partitioning processing and in-memory data while understanding consistency and persistence trade-offs.
**Coverage:** Processing units, data grid, messaging, scaling, replication, persistence, and failure handling.
**Boundaries:** Part 06 owns database sharding; Part 07 owns replication/consistency theory.
**Diagram opportunities:** (1) processing units and data grid; (2) scale-out partition placement; (3) write replication; (4) failover and recovery; (5) persistence boundary.

### CH17 Blackboard Pattern

**Reader outcome:** Coordinate independent knowledge sources through shared evolving state when the solution process is incremental or heuristic.
**Coverage:** Blackboard state, knowledge sources, control component, activation, conflict, and observability.
**Diagram opportunities:** (1) blackboard/knowledge-source topology; (2) state update and activation; (3) control strategy; (4) conflicting hypotheses; (5) blackboard versus pipeline decision.

### CH18 Cell-Based Architecture

**Reader outcome:** Partition a service into independent cells to limit blast radius and scale operations while preserving routing and data ownership.
**Coverage:** Cell boundaries, tenant placement, cell routing, control plane, isolation, cell lifecycle, and migration.
**Boundaries:** Part 09 owns provider fleet products; Part 12 owns Kubernetes mechanics; Part 07 owns data consistency.
**Diagram opportunities:** (1) cell/fleet topology; (2) tenant-to-cell placement; (3) cell-local dependency boundary; (4) cell failure and reroute; (5) cell migration/rebalance.
