# Part 09 — Cloud Computing Topic Map

This map is the coverage contract for Part 09's 16 provider and service chapters. The part teaches how major cloud platforms expose compute, networking, storage, identity, operations, and governance services. It is the source for provider-specific mechanics; architecture modules compose those services into workloads.

## Part-wide ownership boundaries

- Part 09 owns AWS, Azure, Google Cloud Platform (GCP), and provider-specific service behavior, account/region models, integration details, and managed-service operating boundaries.
- Part 10 owns cross-provider cloud workload architecture and service composition; Part 11 applies the AWS Well-Architected Framework; Part 12 owns Kubernetes-native semantics; Part 13 owns general DevOps practice; Part 15 owns security foundations.
- Compare services by control, availability, failure domains, API/limits, operating responsibility, data location, pricing, migration cost, and support model. Do not imply that similar product names provide identical guarantees.
- Identify provider-specific defaults, regional limits, quotas, version/feature maturity, and shared-responsibility boundaries. Distinguish an API surface from a guarantee about resilience or security.

## Cross-part stakeholders and quality scenarios

- Platform architects need service selection and operating-boundary evidence that aligns with workload requirements.
- Application teams need to understand service limits, identity, networking, failure behavior, and integration contracts.
- Finance and governance owners need cost attribution, resource lifecycle, policy inheritance, and audit evidence.
- Important scenarios include an account compromise contained by organizational boundaries; a zonal service failure; a quota or capacity limit during scale-out; an identity or key rotation; and a migration with reversible cutover.

### CH01 AWS

**Reader outcome:** Navigate AWS's account, region, availability-zone, identity, networking, compute, storage, and service operating model.
**Coverage and evidence:** Global/regional scope, accounts and Organizations, shared responsibility, IAM, VPC, EC2, storage, managed-service patterns, quotas, pricing dimensions, and service selection evidence.
**Boundaries:** Part 10 owns workload architecture; Part 11 owns AWS Well-Architected review; CH09 owns provider IAM in comparative detail.
**Diagram opportunities:** (1) organization/account/region/availability-zone hierarchy; (2) shared-responsibility boundary by service type; (3) VPC subnet and route path; (4) identity role assumption path; (5) workload service selection decision.

### CH02 Azure

**Reader outcome:** Navigate Azure's tenant, management-group, subscription, region, identity, network, compute, and managed-service model.
**Coverage and evidence:** Microsoft Entra tenant identity, management groups/subscriptions/resource groups, policy inheritance, regions/zones, virtual networks, compute/storage services, quotas, and support responsibility.
**Boundaries:** Part 10 owns cross-provider architecture; Part 15 owns general security; product-level IAM patterns are compared in CH09.
**Diagram opportunities:** (1) tenant-to-subscription resource hierarchy; (2) policy inheritance and scope; (3) virtual-network/subnet connectivity; (4) managed identity access path; (5) Azure service responsibility matrix.

### CH03 GCP

**Reader outcome:** Navigate GCP's organization, folder, project, region/zone, IAM, network, compute, and managed-service model.
**Coverage and evidence:** Resource hierarchy, project boundaries, IAM policy inheritance, organization policy, VPC design, compute/storage services, quotas, billing, and shared responsibility.
**Boundaries:** Part 10 owns cross-provider architecture; provider-neutral identity/security choices remain with Part 15.
**Diagram opportunities:** (1) organization/folder/project hierarchy; (2) IAM inheritance path; (3) global VPC/subnet topology; (4) project boundary and billing attribution; (5) service responsibility and placement decision.

### CH04 Compute

**Reader outcome:** Select provider compute abstractions by workload, control requirement, scaling, isolation, and operating burden.
**Coverage and evidence:** Virtual machines, autoscaling groups, managed container compute, serverless functions, accelerators, images, placement, quotas, patching, and pricing dimensions across providers.
**Boundaries:** Part 05 owns virtualization/container internals; Part 10 owns composed runtime architecture; CH11 owns serverless service mechanics.
**Diagram opportunities:** (1) compute abstraction spectrum; (2) image-to-instance bootstrap; (3) autoscaling signal-to-capacity flow; (4) placement and failure-domain mapping; (5) workload-to-compute decision tree.

### CH05 Networking

**Reader outcome:** Build cloud network topologies and understand provider-specific routing, connectivity, exposure, and policy controls.
**Coverage and evidence:** VPC/VNet concepts, subnets, route tables, NAT, load balancers, private service access, peering/transit, DNS, hybrid connectivity, network ACL/security-group distinctions, and quotas.
**Boundaries:** Part 05 owns protocol and network fundamentals; Part 10 owns cross-service network architecture; Part 12 owns Kubernetes networking.
**Diagram opportunities:** (1) segmented VPC/VNet topology; (2) packet path through route/NAT/firewall; (3) peering versus transit topology; (4) private service endpoint path; (5) hybrid connectivity failure domain.

### CH06 Storage

**Reader outcome:** Choose provider block, file, object, and backup services from access pattern, consistency, durability, locality, and recovery requirements.
**Coverage and evidence:** Volume/object/file abstractions, lifecycle tiers, replication, encryption, snapshots, backup, restore, throughput/IOPS, regional scope, and provider quotas/cost.
**Boundaries:** Part 06 owns database storage engines; Part 12 CH07 owns Kubernetes storage abstractions; Part 10 owns workload data architecture.
**Diagram opportunities:** (1) block/file/object service comparison; (2) durability and replication scope; (3) snapshot/backup/restore flow; (4) storage lifecycle/tiering; (5) workload I/O pattern to service selection.

### CH07 Containers

**Reader outcome:** Compare provider container registries, runtimes, orchestration services, and task platforms without confusing them with container primitives.
**Coverage and evidence:** Image registries, managed container instances, orchestration services, build/push/pull path, identity, networking, storage, scaling, and operational responsibility.
**Boundaries:** Part 05 CH28 owns container runtime and OS isolation; Part 12 owns Kubernetes APIs; Part 13 owns deployment tooling.
**Diagram opportunities:** (1) image build-to-registry-to-runtime path; (2) managed container execution spectrum; (3) task/pod networking and identity; (4) autoscale and placement flow; (5) responsibility boundary across provider and application team.

### CH08 Kubernetes (cloud-managed)

**Reader outcome:** Compare managed Kubernetes control-plane and node responsibilities, integrations, upgrades, and fleet/cluster operating modes.
**Coverage and evidence:** Managed control plane, node pools, network/storage/IAM integrations, version lifecycle, autoscaling, private clusters, add-ons, upgrades, quotas, and provider support boundaries.
**Boundaries:** Part 12 owns Kubernetes-native resources and workload mechanics; this chapter owns provider-managed service selection and integration.
**Diagram opportunities:** (1) provider control plane and customer node boundary; (2) cluster bootstrap and identity integration; (3) node-pool scale and upgrade; (4) managed versus self-managed responsibility; (5) provider-specific multi-cluster/fleet interface.

### CH09 IAM

**Reader outcome:** Design provider identity and authorization using human/workload principals, roles, resource scopes, federation, and least privilege.
**Coverage and evidence:** Principal/resource/action/policy models, role assumption, workload identities, cross-account/project access, policy inheritance, service-linked roles, credential rotation, and audit.
**Boundaries:** Part 15 owns general security engineering; CH01-03 describe provider-specific organization/identity contexts; Part 12 owns Kubernetes RBAC/workload identity.
**Diagram opportunities:** (1) principal-to-resource authorization evaluation; (2) federation and role-assumption sequence; (3) cross-account/project trust; (4) workload identity to provider API; (5) credential rotation/revocation.

### CH10 Monitoring

**Reader outcome:** Select provider monitoring, logging, tracing, and alert services while defining workload instrumentation and data ownership.
**Coverage and evidence:** Provider metrics/log/traces ingestion, dashboards, alert rules, audit integration, retention, managed service visibility, cross-account access, and cost/cardinality.
**Boundaries:** Part 14 owns generic observability; Part 12 CH14 applies telemetry to Kubernetes; Part 15 owns security audit policy.
**Diagram opportunities:** (1) workload/provider signal ingestion path; (2) cross-account observability topology; (3) alert lifecycle and action; (4) retention/cost flow; (5) managed-control-plane visibility boundary.

### CH11 Serverless

**Reader outcome:** Evaluate provider function, event, and serverless-container services using execution, scaling, state, cold-start, and operational contracts.
**Coverage and evidence:** Invocation models, concurrency, cold starts, runtime limits, triggers, retries, dead-letter handling, event ordering, state, observability, permissions, and pricing.
**Boundaries:** Part 07 owns distributed messaging/retry semantics; Part 10 owns serverless workload composition; Part 13 owns delivery pipelines.
**Diagram opportunities:** (1) event source to function invocation; (2) scaling/concurrency limit; (3) retry/dead-letter lifecycle; (4) cold-start request path; (5) serverless versus container/VM decision.

### CH12 Messaging

**Reader outcome:** Choose provider queues, topics, event buses, and streams using delivery, ordering, retention, replay, and failure requirements.
**Coverage and evidence:** Queue/topic/event/stream models, partitions, ordering, visibility/acknowledgment, retries, retention, dead-lettering, throughput, identity, and cost.
**Boundaries:** Part 07 owns generic distributed messaging and exactly once claims; Part 08 owns API event contracts; Part 10 owns cloud event architecture.
**Diagram opportunities:** (1) queue versus pub/sub versus stream; (2) producer-consumer acknowledgment; (3) partition ordering and replay; (4) retry/dead-letter flow; (5) provider messaging selection matrix.

### CH13 Secrets Management

**Reader outcome:** Select provider secret/key services and integrate retrieval, access, rotation, and audit with workload identity.
**Coverage and evidence:** Secret stores, key management services, envelope encryption, rotation, versioning, access policies, workload identity, caching, availability, and audit.
**Boundaries:** Part 15 owns general secret security; Part 12 CH08/CH13 own Kubernetes Secret consumption and security; Part 10 owns workload identity composition.
**Diagram opportunities:** (1) workload identity to secret retrieval; (2) envelope encryption hierarchy; (3) rotation with overlapping versions; (4) secret cache/refresh path; (5) audit and revocation flow.

### CH14 Cost Optimization

**Reader outcome:** Attribute, forecast, and reduce provider spend while preserving workload objectives and making unit economics visible.
**Coverage and evidence:** Billing dimensions, tags/labels, allocation, budgets, commitments, rightsizing, idle resource detection, data transfer, storage lifecycle, and cost anomaly response.
**Boundaries:** Part 19 owns performance/capacity engineering; Part 10 owns architecture trade-offs; this chapter owns provider billing and optimization tools.
**Diagram opportunities:** (1) usage-to-billing attribution; (2) shared-cost allocation; (3) commitment/consumption trade-off; (4) cost anomaly detection and response; (5) workload objective versus cost frontier.

### CH15 Landing Zones

**Reader outcome:** Establish governed provider foundations that support secure account/project onboarding, delegated ownership, network connectivity, and audit.
**Coverage and evidence:** Organization structure, baseline accounts/subscriptions/projects, identity, policy, logging, networking, shared services, onboarding, exceptions, and lifecycle.
**Boundaries:** Part 10 CH02 owns cross-provider organizational architecture; Part 15 owns security foundations; this chapter owns provider landing-zone products/patterns.
**Diagram opportunities:** (1) organizational hierarchy and baseline scopes; (2) shared-service connectivity; (3) onboarding workflow; (4) policy inheritance and exception flow; (5) landing-zone lifecycle and drift review.

### CH16 Cloud Migration

**Reader outcome:** Plan provider-specific migration tooling and execution while keeping business cutover, data consistency, and rollback explicit.
**Coverage and evidence:** Discovery, dependency mapping, migration services, data transfer, replication, wave planning, cutover, validation, rollback, and post-migration optimization.
**Boundaries:** Part 10 CH14 owns migration strategy and workload modernization architecture; Part 06 owns data-engine migration details; Part 13 owns pipeline mechanics.
**Diagram opportunities:** (1) discovery/dependency graph; (2) migration-wave sequencing; (3) bulk-copy plus change-capture path; (4) cutover/rollback state; (5) provider migration responsibility boundary.
