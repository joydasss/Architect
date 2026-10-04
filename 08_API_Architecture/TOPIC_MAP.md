# Part 08 — API Architecture Topic Map

This map backfills the coverage contract for Part 08's eleven API architecture chapters. The part covers application programming interface (API) contract design, interaction styles, security, lifecycle, and gateway responsibilities. It distinguishes an API's consumer-facing contract from the underlying network protocol and implementation.

## Part-wide ownership boundaries

- Part 08 owns API contract and product architecture: resource/action shape, schema, compatibility, consumer experience, versioning, gateway policy, and API security application.
- Part 05 owns HTTP, TLS, TCP, WebSockets, and transport-level mechanics. Part 08 applies those mechanisms to API design but does not re-teach their wire protocols.
- Part 07 owns distributed-systems semantics such as idempotency, retries, ordering, and exactly-once claims. Part 08 references these when defining API behavior.
- Part 09 owns provider API gateway products; Part 13 owns delivery pipelines; Part 15 owns general security concepts.
- An API is a product contract with consumers, not merely a route or code annotation. Document behavior, compatibility, errors, limits, security, ownership, and evidence.

## Cross-part stakeholders and quality scenarios

- API consumers need stable contracts, predictable errors, discoverability, performance, and migration paths.
- API producers need change control, security, observability, rate/capacity protection, and consumer feedback.
- Platform teams need reusable gateway and authentication policy without obscuring application ownership.
- Important scenarios include adding a field without breaking old clients; a downstream outage under retry load; a credential with excessive scope; schema drift between implementation and documentation; and a version retirement with unidentified consumers.

## API Styles and Interaction Models

### CH01 REST

**Reader outcome:** Design resource-oriented HTTP APIs with consistent semantics, constraints, and consumer-friendly behavior.
**Coverage:** Resource modeling, methods, status codes, representations, caching, pagination, conditional requests, idempotency expectations, errors, hypermedia, and operational constraints.
**Boundaries:** Part 05 owns HTTP semantics; Part 07 owns distributed idempotency and retry principles.
**Diagram opportunities:** (1) resource/relationship model; (2) request method and state transition; (3) conditional request/cache validation; (4) pagination and continuation; (5) error envelope and retry decision.

### CH02 GraphQL

**Reader outcome:** Evaluate GraphQL as a client-selected query contract and manage schema, resolver, authorization, and resource-cost risks.
**Coverage:** Schema and types, query/mutation/subscription, resolvers, batching, N+1 behavior, schema evolution, authorization, depth/complexity limits, and caching.
**Boundaries:** Part 05 owns HTTP/WebSocket transport; CH01 owns general API resource concepts.
**Diagram opportunities:** (1) schema graph and type relationships; (2) query-to-resolver execution tree; (3) N+1 versus batched data access; (4) field-level authorization; (5) query-cost budget enforcement.

### CH03 gRPC

**Reader outcome:** Design gRPC service contracts and choose unary or streaming calls under explicit protocol, compatibility, and operational constraints.
**Coverage:** Protocol Buffers, service/method definitions, unary/client/server/bidirectional streaming, deadlines, status errors, metadata, reflection, load balancing, and schema evolution.
**Boundaries:** Part 05 owns HTTP/2 transport mechanics; CH07 OpenAPI owns HTTP-oriented schema description.
**Diagram opportunities:** (1) protobuf contract to generated client/server; (2) unary request lifecycle; (3) four streaming interaction shapes; (4) deadline/cancellation propagation; (5) schema compatibility across client/server versions.

### CH04 WebSocket API

**Reader outcome:** Specify persistent bidirectional API contracts for realtime interactions, including identity, events, reconnect, and backpressure.
**Coverage:** Upgrade boundary, connection/session identity, message schemas, sequencing, heartbeat, authorization refresh, reconnect, delivery guarantees, and resource limits.
**Boundaries:** Part 05 CH17 owns WebSocket transport; Part 07 owns ordering and deduplication semantics.
**Diagram opportunities:** (1) connection upgrade and authentication; (2) message/event contract lifecycle; (3) reconnect and subscription restoration; (4) slow consumer/backpressure policy; (5) multi-instance fan-out topology.

### CH05 Server-Sent Events API

**Reader outcome:** Use Server-Sent Events (SSE) for server-to-client event streams when HTTP's one-way model and reconnect behavior fit the product contract.
**Coverage:** Event framing, event IDs, retry hints, reconnect/Last-Event-ID, proxy buffering, heartbeat, authentication, and alternatives to bidirectional protocols.
**Boundaries:** Part 05 owns HTTP transport; CH04 owns WebSocket API contracts.
**Diagram opportunities:** (1) event stream framing; (2) reconnect from last event ID; (3) proxy buffering and heartbeat; (4) event retention versus client cursor; (5) SSE/WebSocket/polling decision tree.

### CH06 Async APIs

**Reader outcome:** Design asynchronous request/response APIs around durable acceptance, operation status, callbacks or event delivery, and retry-safe completion.
**Coverage:** Job/operation resources, accepted response, polling, callbacks/webhooks, event delivery, correlation IDs, idempotency, retry/backoff, cancellation, and terminal states.
**Boundaries:** Part 07 owns distributed transaction, Saga, and exactly once mechanics; Part 13 owns pipeline/event delivery products.
**Diagram opportunities:** (1) submit/accepted/operation-status lifecycle; (2) callback and polling alternatives; (3) retry/idempotency interaction; (4) cancellation and terminal state; (5) correlation across asynchronous stages.

## Contracts, Governance, and Protection

### CH07 OpenAPI

**Reader outcome:** Define machine-readable HTTP API contracts and keep schemas, generated artifacts, documentation, validation, and implementation behavior aligned.
**Coverage:** OpenAPI document structure, paths/operations, schemas, reusable components, security schemes, examples, code generation, linting, compatibility, and contract tests.
**Boundaries:** Part 05 owns HTTP protocol semantics; CH01 owns REST design decisions.
**Diagram opportunities:** (1) source contract to docs/SDK/server stubs; (2) schema reuse and reference graph; (3) request/response validation path; (4) breaking-change detection; (5) contract-test feedback loop.

### CH08 API Gateway

**Reader outcome:** Place and govern API gateways as policy and traffic boundaries without hiding service ownership or creating a bottleneck.
**Coverage:** Routing, authentication integration, transformation, quotas, rate limits, caching, version routing, aggregation, observability, high availability, and gateway-versus-reverse-proxy distinction.
**Boundaries:** Part 09 owns managed gateway products; Part 05 CH11 owns reverse proxy mechanics; CH10 owns rate-limiting algorithms and API-level policy.
**Diagram opportunities:** (1) client/gateway/service trust boundary; (2) policy and routing pipeline; (3) gateway aggregation fan-out; (4) rate-limit and quota decision; (5) gateway failure and bypass/health strategy.

### CH09 API Security

**Reader outcome:** Protect API identity, authorization, inputs, data exposure, and abuse paths with controls aligned to the API contract.
**Coverage:** Authentication versus authorization, OAuth/OIDC application, object/function/property authorization, validation, injection, secrets, transport protection, abuse, audit, and security testing.
**Boundaries:** Part 15 owns threat modeling and security foundations; Part 05 owns TLS; CH19 OAuth/OIDC owns protocol flows.
**Diagram opportunities:** (1) request authentication-to-authorization chain; (2) object-level authorization boundary; (3) token audience/scope/expiry validation; (4) input validation and service boundary; (5) abuse detection and containment path.

### CH10 Versioning

**Reader outcome:** Evolve API contracts without surprising consumers and retire old behavior through evidence-backed compatibility policy.
**Coverage:** Additive and breaking changes, URL/header/media-type strategies, deprecation, consumer inventory, compatibility testing, parallel versions, migration windows, and sunset.
**Boundaries:** Part 07 owns distributed compatibility concepts; CH07 owns OpenAPI schema compatibility checks.
**Diagram opportunities:** (1) compatible versus breaking schema evolution; (2) consumer migration timeline; (3) version negotiation path; (4) deprecation/sunset state machine; (5) compatibility test matrix.

### CH11 Rate Limiting

**Reader outcome:** Protect API capacity and fairness with rate-limit algorithms, quotas, client feedback, and distributed enforcement.
**Coverage:** Fixed/sliding windows, token/leaky buckets, concurrency limits, per-identity/client/resource keys, burst handling, distributed counters, HTTP response semantics, and bypass prevention.
**Boundaries:** Part 07 owns retry/idempotency and backpressure; Part 09 owns provider gateway rate-limit products.
**Diagram opportunities:** (1) token bucket refill and burst; (2) fixed versus sliding window; (3) distributed counter race; (4) tenant fairness and quota allocation; (5) 429/retry-after client feedback loop.
