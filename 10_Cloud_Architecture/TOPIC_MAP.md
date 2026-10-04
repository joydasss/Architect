# Part 10 Cloud Architecture Topic Map

This map is the scope and depth contract for Part 10's 15 planned chapters. It is comprehensive within each chapter's stated purpose, not an invitation to expand without bounds. Each chapter may organize, combine, split, and order topics in the form that best teaches them. Every mapped topic should appear substantively in the chapter or be explicitly deferred with a reason.

## Part-wide boundaries

- Part 09 owns provider and individual service mechanics. Part 10 composes those services into workload architectures and makes cross-service, cross-provider decisions.
- Part 11 owns AWS Well-Architected Framework structure, pillar questions, lenses, and AWS-specific review workflows. Part 10 may use general review practice but should link to Part 11 for AWS framework application.
- Parts 05-08 and 12-15 retain their existing protocol, database, distributed-systems, API, Kubernetes, DevOps, observability, and security mechanics. Part 10 applies those mechanics to cloud architecture and links to the owners.
- Part 20 owns general architecture patterns. Part 10 teaches cloud-specific consequences and compositions without repeating the full pattern catalog.
- Check `CORE_CONCEPTS.md` before authoring. Stage genuinely new cross-cutting concepts in the chapter proposal workflow; do not create duplicate owners for a cloud-specific application of an existing concept.

## CH01 Cloud Architecture Foundations and Shared Responsibility

**Reader outcome:** Explain the cloud operating model and make an initial, defensible placement decision for a workload without confusing provider mechanics with architecture choices.

**Topics to cover:**

- Cloud service boundaries: provider, platform, workload team, and customer; how responsibility shifts among infrastructure as a service, platform as a service, software as a service, and function-based execution.
- Shared responsibility as a service-specific control map: physical facilities, hardware, virtualization, managed runtime, identity/configuration, application code, data, and user access. Show how the boundary changes by service and why a shared-responsibility graphic is not a blanket transfer of accountability.
- Cloud operating characteristics: on-demand provisioning, elastic capacity, measured consumption, programmable control planes, geographic placement, and provider-managed failure domains. Distinguish capabilities from automatic guarantees.
- Public, private, hybrid, and community operating models at the level of ownership and control. Detailed hybrid and multi-provider architecture belongs to CH10.
- Workload-placement decision dimensions: business outcome, technical constraints, data classification, locality, latency, availability, control requirements, skills, operating model, and total cost. Distinguish constraints that rule out an option from preferences that create trade-offs.
- Provider scope vocabulary and regional/zonal concepts as concise recap-and-link to Part 09; do not re-teach each provider's infrastructure model.
- Common misconceptions: cloud is not automatically cheaper, secure, available, or portable; managed services reduce some work but change control and failure boundaries.
- A repeatable architecture decision sequence from requirements through service boundary, deployment model, placement, risk, and validation.

**Boundaries:** Provider products and control mechanics are Part 09. Cross-provider topology is CH10. Detailed AWS framework review is Part 11. General quality-attribute and decision-record mechanics link to their existing owners.

**Useful forms:** Responsibility-boundary matrix, workload-placement decision tree, and one worked example comparing two service abstractions for the same workload. No provider-product catalog.

## CH02 Organizational Hierarchy, Accounts, and Landing-Zone Architecture

**Reader outcome:** Design organizational scopes that isolate workloads, delegate ownership, enforce guardrails, and make platform onboarding repeatable.

**Topics to cover:**

- Why cloud resource hierarchy is an architecture boundary: blast radius, delegated control, policy inheritance, billing, quotas, audit, residency, and lifecycle.
- Compare organizational scopes without pretending AWS accounts, Azure subscriptions, and Google Cloud projects are interchangeable. Recap their mechanics from Part 09 and focus on architectural consequences.
- Choose account/subscription/project boundaries by environment, product, team, regulatory domain, lifecycle, and shared-service dependency. Discuss the costs of excessive fragmentation and oversized shared scopes.
- Organizational-unit/folder structure, management groups, policy inheritance, delegated administration, platform teams, workload teams, and responsibility contracts.
- Landing-zone logical architecture: identity, network, security, logging, connectivity, management, shared services, and workload scopes. Part 09 CH15 owns provider foundation implementation.
- Environment isolation and promotion boundaries for development, test, staging, and production, including when isolation by account/project is warranted.
- Provisioning/vending workflow: request schema, validation, policy baseline, identity setup, network attachment, observability/billing registration, owner assignment, and readiness evidence.
- Guardrail model: preventive, detective, and corrective controls; policy inheritance, exceptions with owners/expiry, drift detection, remediation, and decommissioning.
- Shared platform service placement, tenant onboarding contract, and avoiding hidden coupling through shared network, identity, DNS, or logging services.

**Boundaries:** Provider-specific hierarchy/vending mechanics link to Part 09 CH15 and provider chapters. IAM policy evaluation links to Part 09 CH09. Cross-provider organizational patterns are owned here; generic governance/security controls link to Part 15.

**Useful forms:** Scope decision matrix, logical landing-zone diagram, and a sample onboarding contract or policy-inheritance scenario.

## CH03 Cloud Network and Connectivity Architectures

**Reader outcome:** Compose provider networking services into a workload topology with explicit trust, routing, ingress/egress, DNS, and failure boundaries.

**Topics to cover:**

- Begin with workload communication requirements: callers, destinations, protocols, direction, latency, throughput, trust, address overlap, and ownership.
- Translate requirements into address plans, network scopes, subnets, route domains, security boundaries, and IP address management. Recap CIDR/routing mechanics from Part 05 rather than re-teaching them.
- Cloud network topology choices: isolated workload networks, hub-and-spoke, transit hub, shared/host network, mesh, and segmented multi-environment designs. Compare ownership, route propagation, scale, blast radius, and failure coupling.
- North-south and east-west traffic paths; public ingress, private ingress, egress control, NAT, firewalls, load balancers, and private service endpoints as architecture roles. Link product mechanics to Part 09 CH05.
- Hybrid connectivity: VPN and dedicated circuits, route ownership, redundancy, failover, bandwidth, path symmetry, encryption, and operational responsibilities. Detailed multi-provider connectivity is CH10.
- DNS architecture: public/private zones, split-horizon resolution, forwarding, service naming, failover, TTL implications, and provider boundary crossings. DNS protocol mechanics link to Part 05.
- Segmentation and trust zones: workload tiers, environment boundaries, shared services, management paths, and least-connectivity policy. Security threat-model depth links to Part 15.
- Connectivity to managed services: private endpoints, service networks, name resolution, control/data paths, and the risks of accidental public fallback.
- Resilience and capacity: link failure domains, route convergence, throughput ceilings, quotas, packet/MTU constraints, and dependency on centralized transit.
- Operational ownership: source of truth, route change control, flow logs, path testing, incident isolation, and network drift.

**Boundaries:** Part 05 owns IP, routing, NAT, firewall, DNS, TLS, VPN, and load-balancer mechanisms. Part 09 owns cloud networking products. CH10 owns inter-provider architecture; CH12 owns cross-cutting cloud-security architecture.

**Useful forms:** Logical and packet-path diagrams, routing/ownership table, and a small route analysis or address-overlap example.

## CH04 Cloud Identity and Access Architecture

**Reader outcome:** Compose workforce and workload identities, trust relationships, authorization scopes, and credential delivery across cloud resource boundaries.

**Topics to cover:**

- Distinguish identity, authentication, authorization, and audit responsibilities, linking protocol mechanics to Part 05 and API authorization to Part 08.
- Workforce identity architecture: authoritative directory, federation, single sign-on, lifecycle provisioning/deprovisioning, privileged access, and emergency access.
- Workload identity architecture: service principals/roles, managed identities, federation, short-lived credentials, runtime identity delivery, and avoiding embedded long-lived keys.
- Cloud authorization composition across identity, resource, session, organizational guardrail, permission boundary, and service-specific scopes. Part 09 CH09 owns provider evaluation details.
- Cross-account/subscription/project access: caller/resource sides, trust establishment, role assumption, resource policies, delegation, and external-partner access.
- Least privilege as an evolving architecture process: permission discovery, policy boundaries, separation of duties, just-in-time elevation, review cadence, and drift response.
- Identity dependencies in application topology: control-plane administration, service-to-service calls, data-plane access, deployment identities, backup/restore identities, and observability access.
- Secrets and cryptographic key boundaries: use Part 09 CH13 for secret-store mechanics and Part 15 for security depth; explain only the identity interfaces needed here.
- Failure and recovery: identity-provider outage, expired federation, missing service trust, accidental privilege escalation, lost break-glass path, and bounded degraded operation.
- Evidence and lifecycle: audit trails, owner attribution, identity inventory, credential rotation responsibilities, and deprovisioning verification.

**Boundaries:** Part 09 CH09 owns provider IAM mechanics and CH13 owns cloud secret services. Part 05 owns OAuth/OIDC/SAML/JWT protocols; Part 15 owns general security and threat modeling.

**Useful forms:** Trust-boundary diagrams, principal-to-resource access matrix, and a cross-account request walkthrough.

## CH05 Compute Placement and Runtime Architecture

**Reader outcome:** Place workload components on an appropriate cloud runtime and explain the consequences for control, operations, elasticity, portability, and failure.

**Topics to cover:**

- Workload profile: CPU/memory/network/storage shape, accelerators, startup time, duration, concurrency, state, burstiness, licensing, operating-system needs, and isolation.
- Runtime spectrum: virtual machines, managed instance fleets, containers, managed container applications/tasks, Kubernetes, application platforms, functions, batch, and specialized/accelerated compute.
- Choose the right abstraction by control requirements, operational responsibility, deployment cadence, portability, startup behavior, scale-to-zero, state, and skills. Link mechanics to Part 09 CH04/07/08/11.
- Placement across account/project, region, zone, edge, and dedicated capacity, considering data locality, latency, legal boundaries, quotas, and failure domains.
- Stateful versus stateless placement, local versus remote state, graceful drain, checkpointing, and worker replacement. Generic state and delivery semantics link to Part 07.
- Capacity models: fixed, autoscaled, scheduled, burst, reserved/committed, and interruptible; discuss warm-up, headroom, quota, scale limits, and downstream protection.
- Image, bootstrap, configuration, secrets, health checks, rollout, rollback, patching responsibility, and fleet lifecycle at architecture level.
- Runtime communication and dependency placement: service discovery, private connectivity, load balancing, sidecars/agents when relevant, and managed-service boundaries.
- Compute failure modes: zone loss, host replacement, capacity exhaustion, bad image/configuration, cold starts, noisy neighbors, and provider service limits.
- Portability and lock-in: guest-level portability versus reliance on managed runtime APIs, orchestration and data bindings, and the cost of preserving optionality.

**Boundaries:** Part 09 owns service selection mechanics; Part 05 owns virtualization/container internals and Part 12 owns Kubernetes internals. CH11 covers global/edge placement and CH13 covers cross-cutting performance/cost/sustainability decisions.

**Useful forms:** Runtime decision tree, component placement table, and a capacity/availability comparison for one representative workload.

## CH06 Cloud Storage and Data Architecture

**Reader outcome:** Place workload data across cloud storage and database services based on access patterns, consistency, locality, protection, and lifecycle requirements.

**Topics to cover:**

- Start from data domains, owners, sensitivity, volume, growth, access patterns, write/read paths, latency, throughput, retention, and deletion obligations.
- Select object, block, managed file, relational database, key-value/document, analytics, cache, and backup services by workload contract rather than product familiarity.
- Data flow and ownership: system of record, derived data, replicas, caches, analytical copies, ingestion paths, and authority during recovery or migration.
- Durability, availability, consistency, replication scope, versioning, snapshots, backup independence, immutability, restore testing, and administrative blast radius.
- Data placement and locality: region, zone, residency, cross-region replication, data gravity, egress, latency, and service co-location.
- Lifecycle: hot/cool/archive tiers, retention transitions, retrieval delay, indexing, deletion, legal hold, and recovery windows.
- Database architecture choices and service responsibilities, recapping Part 06 engine internals rather than explaining database algorithms again.
- Caching and materialization: when derived copies improve latency or cost and what invalidation, freshness, and outage behavior they introduce.
- Data security architecture: classification, encryption/key ownership, access boundaries, masking, tokenization, and audit; general security controls link to Part 15.
- Failure and recovery: accidental deletion, corruption, ransomware, regional loss, key unavailability, replication lag, quota, and restore dependency chains.

**Boundaries:** Part 09 CH06 owns provider storage service guarantees and mechanics; Part 06 owns database/storage-engine details. CH09 owns resilience topology and recovery plans; CH13 owns cost/performance/sustainability consequences.

**Useful forms:** Data-class placement matrix, data-flow/authority diagram, and a restore dependency scenario.

## CH07 Cloud-Native Application and Integration Patterns

**Reader outcome:** Compose application components and managed dependencies into a cloud workload while making service boundaries, configuration, discovery, and failure behavior explicit.

**Topics to cover:**

- Workload decomposition into user-facing, domain, integration, background, and data components; identify which boundaries are architectural versus merely deployment units.
- Stateless request handling, externalized state, session placement, idempotent worker responsibilities, and graceful process lifecycle. Link generic patterns and delivery semantics to Parts 07 and 20.
- Managed dependencies: databases, queues, object storage, identity, telemetry, and search. Evaluate service contracts, network boundaries, credentials, limits, and failure modes without re-teaching their service chapters.
- Synchronous versus asynchronous integration based on latency, coupling, backpressure, user experience, consistency, and recovery requirements; detailed messaging architecture belongs to CH08.
- Service discovery and naming: DNS, registries, endpoint configuration, health, traffic policy, and behavior during replacement or failover.
- Configuration and secrets: immutable deployment config, runtime configuration, secret references, rotation compatibility, and avoiding credentials in artifacts. Link secret lifecycle to Part 09 CH13.
- Cloud API and service integration boundaries, private endpoints, event triggers, workload identities, and data ownership.
- Deployment topology: single service, modular deployment, distributed services, jobs/workers, and workflow orchestration. Avoid reciting general microservice patterns owned by Part 20.
- Resilience composition: timeouts, retries, bulkheads, circuit breakers, queues, and degraded modes as cloud-specific dependency policies; link pattern mechanics to Part 20/Part 07.
- End-to-end request and background-job paths, including telemetry context, ownership, support boundaries, and operational handoff.

**Boundaries:** Part 20 owns general architectural patterns; Parts 07/08 own distributed/API semantics; Part 09 owns service mechanics; CH09 covers workload resilience and CH12 security.

**Useful forms:** Workload context/container diagrams, request and event traces, and a failure-propagation walkthrough.

## CH08 Event, Queue, and Messaging Architectures in Cloud

**Reader outcome:** Select and compose cloud messaging services around delivery, ordering, retention, replay, fan-out, and operational requirements.

**Topics to cover:**

- Classify command, event, task, notification, and stream contracts; distinguish queue, pub/sub topic, event bus, and partitioned stream.
- Derive service choice from producer/consumer coupling, ordering key, throughput, retention, replay, fan-out, consumer independence, and latency.
- Compose producers, brokers, subscriptions, filters, consumers, retries, dead-letter paths, replay, and archival.
- Ordering scope, duplicate delivery, acknowledgement, visibility/lease, delivery attempts, consumer offsets/checkpoints, and idempotency as concise applications of Part 07 ownership.
- Event routing and integration with functions, containers, SaaS endpoints, APIs, and cross-account/project consumers; link service-specific mechanics to Part 09 CH12.
- Schema and contract evolution, version compatibility, ownership, and privacy; API/schema owners retain their detailed mechanics.
- Cross-region messaging, disaster recovery, replication, ordering boundaries, duplicate windows, replay strategy, and data residency.
- Backpressure and flow control: producer quotas, consumer concurrency, partition distribution, poison messages, slow consumers, and downstream protection.
- Security and isolation: producer/consumer identities, broker access, tenant separation, encryption, and audit.
- Operations and economics: lag, age, throughput, retries, dead-letter growth, retention cost, quotas, and alert response.

**Boundaries:** Part 07 owns generic delivery, ordering, idempotency, and stream-processing concepts. Part 09 CH12 owns provider messaging products/configuration. CH07 covers broader application composition.

**Useful forms:** Service selection matrix, event path and replay diagram, and a worked poison-message recovery design.

## CH09 Resilience, Availability, and Disaster-Recovery Architectures

**Reader outcome:** Design and validate cloud workload resilience across failure domains, including explicit recovery objectives, dependency behavior, failover, and restoration.

**Topics to cover:**

- Translate business impact and service dependencies into availability targets, recovery time objective (RTO), and recovery point objective (RPO), recapping Part 07 definitions.
- Failure-domain hierarchy: process, host, zone, region, provider service, identity, network, control plane, operator, and supply chain; distinguish correlated from independent failures.
- Availability composition across dependencies and shared services; identify critical paths, quorum assumptions, capacity constraints, and weakest-link behavior.
- Zonal patterns: single-zone, zone-redundant, active/active replicas, state placement, health-based routing, and zonal dependency behavior.
- Regional patterns: backup/restore, pilot light, warm standby, active/active, selective multi-region, and provider-managed regional redundancy. Explain cost, data consistency, operational, and failover trade-offs.
- Data recovery: backup isolation, immutable copies, replication lag, point-in-time restore, key dependencies, restore order, and data authority after failover.
- Dependency-aware degraded modes: prioritize essential transactions, shed optional work, queue work, cache safe reads, and protect downstream systems.
- Failover and failback: detection signals, decision authority, automation guardrails, fencing/single-writer behavior, DNS/traffic convergence, reconciliation, and return-to-primary criteria.
- Disaster-recovery runbooks, testing cadence, game days, chaos experiments, evidence, and recovery capability drift.
- Resilience economics: reserve capacity, replicated data, standby infrastructure, staff readiness, and the cost of untested complexity.

**Boundaries:** Part 07 owns general reliability objectives and distributed-systems failure semantics; Part 09 owns provider backup/replication features. CH10 handles hybrid/multi-cloud resilience. Part 11 applies AWS WAF reliability questions.

**Useful forms:** Failure-domain map, recovery-mode comparison, dependency restoration sequence, and a timed recovery exercise.

## CH10 Hybrid Cloud and Multi-Cloud Architecture

**Reader outcome:** Decide whether hybrid or multi-cloud is justified and design its identity, network, data, operations, and failure boundaries without assuming portability is free.

**Topics to cover:**

- Distinguish hybrid cloud (cloud plus retained/on-premises environment) from multi-cloud (multiple providers) and from SaaS dependency diversity.
- Drivers and constraints: regulatory/locality, latency, acquisition, capacity, resilience, service capability, bargaining, existing investment, and exit requirements. Separate business need from vendor preference.
- Decision economics: incremental operating burden, duplicated skills/tooling, integration and egress costs, control-plane fragmentation, and concentration risk.
- Workload placement and boundary strategy: whole workload, components, shared data, control plane, regional slices, and transitional coexistence.
- Network architecture: address overlap, shared routing, transit, private links, DNS, egress, firewall ownership, path symmetry, failure isolation, and throughput.
- Identity and trust: workforce federation, workload identity across providers, credential exchange, authorization boundaries, emergency access, and revocation.
- Data architecture: system of record, replication, consistency, data gravity, residency, synchronization, conflict, egress, and provider exit.
- Portability layers: source portability, container/runtime portability, orchestration, APIs, infrastructure definitions, data formats, and operational process. Model abstraction cost versus actual avoided migration cost.
- Operations and governance: asset inventory, policy translation, telemetry, incident command, cost allocation, configuration drift, and service ownership across teams/providers.
- Failure boundaries and recovery: provider outage versus shared identity/network failure, correlated control-plane dependencies, split brain, and realistic cross-provider DR.
- Exit and reversibility: data extraction, dependency replacement, contract/skills, migration proof, and recurring portability tests.

**Boundaries:** Part 09 owns each provider's products; CH03/04 cover cloud-network and identity architecture generally. Part 10 owns cross-provider composition and its costs. Avoid re-teaching migration waves from CH14.

**Useful forms:** Justification decision record, cross-provider boundary diagram, identity/network/data flow, and an exit-cost model.

## CH11 Edge, Regional, and Global Workload Placement

**Reader outcome:** Place computation and data near users, devices, and systems while balancing latency, availability, sovereignty, operational control, and synchronization.

**Topics to cover:**

- Placement vocabulary: region, zone, local zone/metro, edge location, customer site, device, and disconnected operation; provider examples link to Part 09.
- Latency decomposition: propagation, network path, DNS/TLS setup, queueing, compute, storage, and dependency calls; identify what geographic placement can and cannot improve.
- Global request routing: DNS, anycast/CDN, global load balancing, health checks, affinity, traffic steering, failover, and client behavior.
- Data placement and locality: authoritative region, read replicas, edge cache, local state, residency constraints, synchronization, invalidation, and stale/offline behavior.
- Edge processing choices: data filtering, inference, protocol translation, local control loops, privacy, intermittent links, and cloud synchronization.
- Device/fleet architecture: enrollment, device identity, secure update, rollout rings, version compatibility, telemetry, remote configuration, and recovery from partial updates.
- Regional architecture patterns: active/passive, active/active, cell/shard placement, tenant affinity, regional isolation, and blast-radius control.
- Global consistency and user/session routing: write authority, locality trade-offs, conflict, failover semantics, and user experience under regional partition.
- Operational constraints: physical access, power, bandwidth, support, constrained hardware, fleet heterogeneity, and remote observability.
- Economics and sustainability: edge-resource utilization, data transfer, hardware refresh, carbon intensity, and the cost of locality.

**Boundaries:** Part 09 owns provider edge products and CDN mechanics; Part 05 owns protocol/network details; CH09 owns recovery architectures. CH13 owns cost and sustainability framework.

**Useful forms:** Latency budget, global placement map, edge/cloud data flow, and a disconnected-device recovery sequence.

## CH12 Cloud Security, Governance, and Compliance Architecture

**Reader outcome:** Translate security and compliance obligations into cloud architecture boundaries, controls, evidence, and accountable operating processes.

**Topics to cover:**

- Scope the protected workload, assets, identities, data flows, trust boundaries, threats, and regulatory obligations; distinguish compliance evidence from security assurance.
- Apply shared responsibility at component/control level, linking to provider and security owners rather than assuming a provider certification makes the workload compliant.
- Organizational guardrails: policy inheritance, prevention/detection/correction, deny controls, configuration baselines, exception lifecycle, and separation of platform versus workload authority.
- Workload isolation: accounts/projects, networks, clusters, tenants, data stores, management plane, and blast radius; select boundaries based on threat and operations.
- Identity architecture, privileged paths, workload identity, least privilege, and emergency access as recap links to CH04/Part09 IAM.
- Data protection architecture: classification, encryption in transit/at rest, key ownership, secrets, tokenization, residency, backup, retention, deletion, and evidence.
- Network and service exposure: private service access, ingress/egress policy, egress inspection, control-plane access, and service-to-service trust.
- Detection and response architecture: audit sources, centralized evidence, tamper resistance, alert routing, forensic access, incident containment, and provider support boundaries.
- Compliance mapping: obligations to architecture controls, owners, evidence sources, test cadence, and gaps; avoid mapping standards as a substitute for risk analysis.
- Policy as code and drift management: source control, testing, staged rollout, exception expiry, change ownership, and safe remediation.
- Third-party and supply-chain dependencies: provider regions/services, marketplace/SaaS, managed runtime, deployment pipeline, and shared responsibility limits.

**Boundaries:** Part 15 Security owns general threat modeling, control families, cryptography, and compliance depth. Part 09 CH09/13 own provider IAM/secrets. CH02 owns landing-zone guardrails and CH03 network architecture.

**Useful forms:** Trust-boundary diagram, control-to-evidence matrix, and an exception workflow with expiry and residual-risk owner.

## CH13 Cloud Cost, Performance, and Sustainability Architecture

**Reader outcome:** Evaluate cloud workload architecture across cost, performance, and environmental impact using workload evidence and explicit trade-offs.

**Topics to cover:**

- Workload demand and outcome model: transaction/job unit, demand shape, user experience, service objective, data volume, and growth assumptions.
- Cost drivers: compute time/capacity, storage footprint/requests, database throughput, messaging, observability, licensing, support, public IP, and network/egress. Link provider billing tools and commitments to Part 09 CH14.
- Unit economics and allocation: cost per successful outcome, shared platform allocation, idle/peak capacity, showback/chargeback, tagging dimensions, and cost ownership.
- Architecture cost estimation: baseline, sensitivity analysis, scale curves, uncertainty, regional variance, multi-environment overhead, and price-versus-cost distinctions.
- Performance budgets: latency/throughput, percentiles, concurrency, queueing, data locality, cold start, network transfer, storage I/O, and saturation. Link general measurement and tuning to Part 19.
- Cost/performance trade-offs: overprovisioned headroom, autoscaling, caching, managed service abstraction, commitments, spot/interruptible work, data tiering, and egress avoidance.
- Sustainability dimensions: operational energy/carbon, hardware lifecycle, regional grid intensity, utilization, data retention, duplicate copies, efficient algorithms, and embodied impacts where evidence is available.
- Measure responsibly: define boundaries, workload attribution, normalized outcomes, time windows, carbon-data uncertainty, and avoid false precision or unverified provider claims.
- Joint optimization loop: establish baseline, identify bottleneck/waste, model alternatives, test, observe, document trade-off, and monitor regression.
- Governance: budgets, anomaly detection, performance/cost owners, sustainability goals, and approval thresholds integrated with operational workflows.

**Boundaries:** Part 09 CH14 owns provider cost systems and product mechanics. Part 07 owns SLI/SLO and reliability objectives; Part 19 owns performance engineering. Part 11 applies AWS cost/sustainability pillar questions.

**Useful forms:** Cost stack, latency budget, cost/performance frontier, sensitivity model, and a normalized carbon/energy comparison with stated assumptions.

## CH14 Cloud Migration and Modernization Architecture

**Reader outcome:** Choose a workload transition strategy and design migration waves, coexistence, data movement, cutover, rollback, and modernization sequencing across providers.

**Topics to cover:**

- Migration drivers, constraints, success measures, current-state evidence, application ownership, dependency discovery, data classification, and business calendar.
- Strategy choices: retain, retire, rehost, relocate, replatform, refactor/re-architect, repurchase/replace, and defer; distinguish strategy label from target design and verify naming variants.
- Portfolio decision criteria: business value, technical risk, coupling, modernization opportunity, time, skills, licensing, data gravity, compliance, and target operating model.
- Target architecture and landing-zone readiness; link provider foundation mechanics to Part 09 CH15 and cross-provider design to earlier Part 10 chapters.
- Migration-wave construction: dependency graph, shared service sequencing, application cohorts, wave size, entry/exit gates, pilot learning, risk balancing, and throughput constraints.
- Coexistence architecture: identity, DNS/routing, API/event integration, data ownership, single writer, synchronization, compatibility, and support ownership during transition.
- Data transition: bulk seed, change capture, validation, consistency boundary, freeze, reconciliation, data residency, and rollback implications. Link engine mechanics to Part 06 and provider tools to Part 09 CH16.
- Cutover and rollback: readiness evidence, decision authority, traffic/endpoint change, write boundary, observability, business acceptance, rollback safety, and post-cutover source disposition.
- Modernization sequencing: separate move risk from redesign risk, use incremental replacement where justified, test target operational maturity, and avoid preserving temporary architecture indefinitely.
- Program governance and learning: cost/benefit case, migration factory, reusable automation, knowledge transfer, risk register, stakeholder communications, and success measures.
- Post-migration optimization and decommissioning: validate service, security, reliability, cost, performance, ownership, licenses, data retention, and source cleanup.

**Boundaries:** Part 09 CH16 owns provider migration tools and operational mechanics. Part 10 owns strategy, portfolio waves, coexistence topology, and target architecture. Part 07 owns generic delivery/idempotency/RPO/RTO; Part 06 owns database mechanics.

**Useful forms:** Strategy decision matrix, dependency/wave graph, coexistence topology, and rehearsed cutover/rollback timeline.

## CH15 Cloud Architecture Reviews and Reference Designs

**Reader outcome:** Review a complete cloud workload consistently, expose consequential risks and assumptions, and communicate reusable reference architectures without duplicating specialist frameworks.

**Topics to cover:**

- Review purpose, scope, stakeholders, decision authority, evidence expectations, lifecycle timing, and outcome types (approve, condition, investigate, accept risk, redesign).
- Workload framing: context, users, interfaces, data classification, dependencies, constraints, objectives, owners, and operating model.
- Review evidence: context/container/deployment/data-flow diagrams, threat boundaries, capacity and cost assumptions, operational runbooks, recovery tests, and decision records.
- Cross-provider review lenses: organization/landing zone, network, identity, compute, data, integration, reliability, operations, security, cost, performance, sustainability, and portability.
- Quality-attribute scenarios and trade-off reasoning; link terminology and formal review techniques to existing Part 01/07/15/19 owners.
- Review facilitation: pre-read, question framing, challenge assumptions, distinguish evidence from opinion, resolve disagreement, timebox, and record decisions/actions.
- Risk and action tracking: impact/likelihood/confidence, owner, due date, mitigation, acceptance authority, evidence of closure, and residual-risk review.
- Reference design quality: explicit context and assumptions, variants, decision record, trust boundaries, failure behavior, operational ownership, known limitations, and versioning.
- Reusable cloud workload archetypes: web/API, event-driven, batch/analytics, data-intensive, internal platform, edge-connected, and regulated workload; choose a bounded set with clear trade-offs instead of a catalog of vendor services.
- Case studies: trace requirements through topology, decisions, failure scenarios, operations, and cost; include at least one rejected alternative and why.
- Continuous review: architecture drift, trigger events, production feedback, incidents, cost/performance changes, and reference-design retirement.
- AWS Well-Architected relationship: use Part 11 for six-pillar mechanics, lenses, tool, and AWS-specific review questions; do not re-teach its framework.

**Boundaries:** Part 11 owns AWS WAF. Part 21 owns architecture documentation notations and broader documentation mechanics. Part 01 owns ADR and architecture review foundations; Part 15/19/07 own specialist security/performance/reliability concepts.

**Useful forms:** Review agenda and evidence checklist, reusable reference-design template, risk-to-action ledger, and two end-to-end workload case studies.
