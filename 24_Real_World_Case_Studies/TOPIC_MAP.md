# Part 24 — Real-World Architecture Case Studies Topic Map

This map defines coverage for Part 24's twenty-five architecture case studies. Each case should frame goals and constraints, compare viable options, identify quality attributes and failure modes, and end with a justified architecture rather than a universal recipe.

## Part-wide ownership boundaries

- Part 24 owns end-to-end worked examples and the reasoning that connects requirements to system boundaries, data, interfaces, operations, and trade-offs.
- Parts 05–23 own reusable technical foundations and competency methods; cases may recap them but should not replace their dedicated chapters.
- Every case should state assumptions, scale and workload shape, security/privacy concerns, failure behavior, operational evidence, and meaningful alternatives. Avoid implying that one design fits every deployment.

## Cross-part stakeholders and scenarios

- Stakeholders include product and domain owners, users, engineering, operations, security, compliance, finance, and external partners.
- Important scenarios include rapid growth, partial dependency failure, duplicate or delayed events, data correction, regional disruption, abuse, regulatory change, and cost pressure.

## Case Studies

### CH01 URL Shortener

**Reader outcome:** Design a redirect service by balancing key generation, lookup latency, write/read scale, abuse controls, and analytics.
**Coverage:** Short-code allocation, redirect path, persistence/cache, expiration, custom aliases, abuse, and click events.
**Diagram opportunities:** (1) create-short-link flow; (2) redirect read path; (3) code allocation and collision handling; (4) cache/database consistency; (5) click-event analytics pipeline.

### CH02 Ride Sharing Platform

**Reader outcome:** Architect matching and trip lifecycle workflows under location freshness, low latency, safety, and marketplace constraints.
**Coverage:** Driver location, rider requests, geo-indexing, matching, pricing, trip state, notifications, and payments.
**Diagram opportunities:** (1) rider-to-driver matching flow; (2) geo-partitioned location index; (3) trip state machine; (4) surge pricing feedback; (5) dispatch degradation during regional failure.

### CH03 Food Delivery Platform

**Reader outcome:** Coordinate ordering, merchant preparation, courier dispatch, delivery tracking, and settlement across independent actors.
**Coverage:** Menu/catalog, order acceptance, preparation estimates, batching, dispatch, tracking, cancellation, and compensation.
**Diagram opportunities:** (1) order lifecycle; (2) merchant-courier-customer interaction; (3) dispatch and batching; (4) status-event timeline; (5) cancellation and compensation saga.

### CH04 Video Streaming Platform

**Reader outcome:** Design a video delivery path from ingest and processing to adaptive playback with availability and cost controls.
**Coverage:** Upload, transcoding, packaging, origin storage, content delivery, playback telemetry, rights, and recommendation boundaries.
**Diagram opportunities:** (1) ingest-to-playback pipeline; (2) encoding ladder and adaptive bitrate; (3) origin/CDN request path; (4) regional cache fill and failover; (5) playback QoE telemetry loop.

### CH05 OTT (Over-the-Top) Platform

**Reader outcome:** Integrate subscription, entitlement, catalog, playback, device, and billing capabilities for a multi-device media service.
**Coverage:** Identity, plans, entitlement, catalog metadata, DRM boundary, billing, device compatibility, and account lifecycle.
**Diagram opportunities:** (1) subscriber-to-entitlement flow; (2) playback authorization path; (3) subscription state transitions; (4) device and DRM trust boundary; (5) billing reconciliation workflow.

### CH06 Social Media Platform

**Reader outcome:** Balance content creation, feed generation, social graph, moderation, and privacy across diverse workloads.
**Coverage:** Graph relationships, posts, timelines, ranking, media, moderation, notifications, and user controls.
**Diagram opportunities:** (1) publish-to-feed fan-out; (2) push versus pull timeline generation; (3) social graph partition; (4) moderation and appeal workflow; (5) privacy setting propagation.

### CH07 Chat Application

**Reader outcome:** Design durable and real-time messaging with delivery semantics, presence, ordering, and multi-device synchronization.
**Coverage:** Conversation membership, message persistence, connection gateways, offline delivery, read state, attachments, and encryption boundary.
**Diagram opportunities:** (1) sender-to-recipient message path; (2) online/offline delivery state; (3) conversation partition and ordering; (4) multi-device synchronization; (5) attachment upload and access control.

### CH08 Banking System

**Reader outcome:** Architect core banking workflows around ledger correctness, access control, auditability, availability, and regulatory obligations.
**Coverage:** Accounts, postings, balances, transaction lifecycle, reconciliation, fraud controls, audit, and legacy integration.
**Diagram opportunities:** (1) transaction posting and ledger entries; (2) authorization and fraud decision path; (3) ledger-to-balance projection; (4) reconciliation and exception queue; (5) recovery with audit continuity.

### CH09 UPI (Unified Payments Interface) Payment Gateway

**Reader outcome:** Model payment initiation and callbacks with idempotency, timeouts, reconciliation, and secure participant boundaries.
**Coverage:** Payment intents, payer/payee participants, routing, authentication, status callbacks, refunds, settlement, and dispute handling.
**Diagram opportunities:** (1) payment authorization sequence; (2) participant trust and credential boundary; (3) timeout, retry, and idempotency states; (4) settlement and reconciliation; (5) refund and dispute lifecycle.

### CH10 Mutual Fund Platform

**Reader outcome:** Design investment order and portfolio services with market cutoffs, valuation correctness, compliance, and traceable money movement.
**Coverage:** Investor identity, suitability, order capture, NAV timing, units, payment, statements, corporate actions, and audit.
**Diagram opportunities:** (1) investor-to-order lifecycle; (2) order cutoff and NAV processing; (3) units and cash reconciliation; (4) suitability and compliance controls; (5) portfolio statement data lineage.

### CH11 E-commerce Marketplace

**Reader outcome:** Coordinate discovery, seller offers, checkout, inventory, payment, fulfillment, and post-purchase workflows across merchants.
**Coverage:** Catalog, search, offers, cart, pricing, inventory reservation, order orchestration, seller isolation, and returns.
**Diagram opportunities:** (1) browse-to-purchase journey; (2) offer and catalog relationship; (3) inventory reservation during checkout; (4) order orchestration saga; (5) seller onboarding and isolation boundary.

### CH12 Inventory Management

**Reader outcome:** Maintain usable inventory availability across locations and channels while handling reservations, movements, and corrections.
**Coverage:** Stock ledger, availability projection, reservations, transfers, adjustments, replenishment, concurrency, and reconciliation.
**Diagram opportunities:** (1) stock movement ledger; (2) available-to-promise calculation; (3) reservation lifecycle; (4) warehouse transfer workflow; (5) discrepancy detection and correction.

### CH13 Logistics Platform

**Reader outcome:** Plan and track shipments across carriers, facilities, routes, and exceptions with timely operational visibility.
**Coverage:** Shipment creation, label/rate, routing, tracking events, carrier adapters, proof of delivery, and exception handling.
**Diagram opportunities:** (1) shipment lifecycle; (2) carrier integration boundary; (3) route and facility network; (4) tracking-event normalization; (5) lost/delayed shipment escalation.

### CH14 Airline Reservation System

**Reader outcome:** Handle search, itinerary pricing, seat inventory, booking, ticketing, and disruption under strict concurrency and partner constraints.
**Coverage:** Schedule/search, availability, fare rules, holds, booking, payment, ticketing, partner distribution, and re-accommodation.
**Diagram opportunities:** (1) search-to-ticket sequence; (2) seat inventory hold and expiry; (3) booking state machine; (4) partner distribution boundary; (5) disruption and rebooking flow.

### CH15 Healthcare EMR (Electronic Medical Record) System

**Reader outcome:** Design clinical record workflows that protect privacy and safety while enabling interoperability and reliable access.
**Coverage:** Patient identity, encounters, records, clinician workflows, consent, audit, interoperability, availability, and retention.
**Diagram opportunities:** (1) encounter documentation flow; (2) patient identity matching; (3) consent-aware record access; (4) clinical interoperability exchange; (5) downtime access and reconciliation.

### CH16 CRM (Customer Relationship Management) Platform

**Reader outcome:** Organize customer, account, interaction, and opportunity data to support workflows, integrations, and governed access.
**Coverage:** Customer identity, interaction timeline, sales/service workflows, assignment, search, integrations, and data quality.
**Diagram opportunities:** (1) lead-to-customer lifecycle; (2) customer 360 data composition; (3) assignment and escalation workflow; (4) integration/event boundary; (5) consent and field-level access.

### CH17 ERP (Enterprise Resource Planning) System

**Reader outcome:** Explain how an ERP coordinates shared enterprise records and transactions while managing customization and integration boundaries.
**Coverage:** Finance, procurement, orders, inventory, master data, workflows, extensions, reporting, and migration.
**Diagram opportunities:** (1) cross-functional transaction flow; (2) shared master-data ownership; (3) ERP integration landscape; (4) extension versus core boundary; (5) phased migration and reconciliation.

### CH18 IoT (Internet of Things) Telemetry Platform

**Reader outcome:** Ingest, process, retain, and query device telemetry under intermittent connectivity, scale, and device-security constraints.
**Coverage:** Provisioning, identity, protocols, ingestion, buffering, stream processing, time-series storage, commands, and fleet operations.
**Diagram opportunities:** (1) device-to-cloud telemetry path; (2) offline buffering and replay; (3) fleet identity and provisioning; (4) stream-to-storage tiers; (5) command channel trust boundary.

### CH19 Real-time Analytics Platform

**Reader outcome:** Combine event ingestion, stream computation, serving, and historical analysis with explicit freshness and correctness semantics.
**Coverage:** Event contracts, ingestion, windows, state, late data, sinks, dashboards, replay, and batch/stream integration.
**Diagram opportunities:** (1) event-to-dashboard latency path; (2) event-time window and late arrival; (3) stream state and checkpoint; (4) replay and deduplication; (5) serving store and historical lake boundary.

### CH20 AI-powered Enterprise Knowledge Assistant

**Reader outcome:** Design a grounded knowledge assistant with authorized retrieval, citations, feedback, safe tool limits, and measurable quality.
**Coverage:** Source ingestion, permissions, retrieval, generation, citations, identity, evaluation, human escalation, and cost controls; Part 17 owns AI system architecture.
**Diagram opportunities:** (1) source-to-index lifecycle; (2) identity-filtered retrieval path; (3) question-to-citation flow; (4) answer escalation and feedback; (5) prompt-injection and tool trust boundary.

### CH21 Multi-tenant SaaS (Software as a Service) Platform

**Reader outcome:** Choose tenant isolation, data partitioning, onboarding, metering, and noisy-neighbor controls for a SaaS product.
**Coverage:** Tenant identity, isolation models, configuration, provisioning, quotas, billing, migrations, and tenant lifecycle.
**Diagram opportunities:** (1) tenant request routing; (2) shared versus siloed isolation; (3) onboarding and provisioning workflow; (4) per-tenant metering and quotas; (5) tenant migration and offboarding.

### CH22 API Gateway and Developer Portal

**Reader outcome:** Expose governed APIs with discoverability, authentication, lifecycle management, and reliable consumer onboarding.
**Coverage:** Gateway routing, policies, identity, quotas, API catalog, developer experience, versioning, analytics, and support.
**Diagram opportunities:** (1) consumer-to-service gateway path; (2) authentication and policy enforcement; (3) API publication lifecycle; (4) developer onboarding journey; (5) version retirement and consumer migration.

### CH23 Event Streaming Platform

**Reader outcome:** Operate a shared event-streaming capability with clear topic ownership, delivery semantics, access, and replay controls.
**Coverage:** Producers, brokers, partitions, retention, consumer groups, schemas, security, governance, and operations.
**Diagram opportunities:** (1) producer-broker-consumer topology; (2) partition and consumer assignment; (3) schema evolution path; (4) replay and retention boundary; (5) lag monitoring and recovery.

### CH24 Enterprise Document Management System

**Reader outcome:** Manage document capture, metadata, versioning, access, retention, search, and audit across enterprise workflows.
**Coverage:** Ingestion, classification, metadata, content storage, version history, permissions, legal hold, search, and disposal.
**Diagram opportunities:** (1) capture-to-archive lifecycle; (2) metadata and content storage split; (3) version and approval workflow; (4) authorization and legal-hold boundary; (5) retention and disposition states.

### CH25 Workflow and BPM (Business Process Management) Engine

**Reader outcome:** Model long-running business processes with durable state, human tasks, integrations, timers, and safe version changes.
**Coverage:** Process definitions, execution state, task assignment, events, retries, compensation, observability, and migration.
**Diagram opportunities:** (1) process definition and execution separation; (2) human task lifecycle; (3) timer, retry, and compensation path; (4) process version migration; (5) workflow monitoring and exception handling.
