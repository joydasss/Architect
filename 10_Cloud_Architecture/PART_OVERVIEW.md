# Part 10 — Cloud Architecture

Supplemental architecture module focused on designing complete cloud workloads across organizational accounts, networks, data, compute, reliability, security, and operations. [Part 09 — Cloud Computing](../09_Cloud_Computing/PART_OVERVIEW.md) owns provider/service introductions and individual service mechanics; this module owns cross-service architecture decisions, reference topologies, and trade-offs.

## Scope boundary

Part 09 remains the home for AWS, Azure, Google Cloud Platform (GCP), compute, networking, storage, Identity and Access Management (IAM), messaging, serverless, landing zones, and migration service details. Part 10 composes those capabilities into workloads, including hybrid and multi-cloud designs. AWS-specific application of the AWS Well-Architected Framework (WAF) is kept separate in [Part 11](../11_AWS_Well_Architected_Framework/PART_OVERVIEW.md). Kubernetes and generic security/observability mechanics remain with their existing parts.

## Chapters

| Chapter | Focus | Status |
|---|---|---|
| Cloud Architecture Foundations and Shared Responsibility | Cloud operating models, service boundaries, elasticity, consumption, shared responsibility, and decision dimensions for workload placement. | Not Started |
| Organizational Hierarchy, Accounts, and Landing-Zone Architecture | Design account/subscription/project boundaries, environments, delegated administration, policy inheritance, and workload onboarding; recap Part 09 landing-zone mechanics. | Not Started |
| Cloud Network and Connectivity Architectures | Compose virtual networks, segmentation, ingress/egress, private connectivity, DNS, routing, and hybrid links into workload topologies. | Not Started |
| Cloud Identity and Access Architecture | Structure workforce and workload identities, federation, permission boundaries, secrets, and cross-account access; recap provider IAM implementations and Part 15 Security. | Not Started |
| Compute Placement and Runtime Architecture | Select virtual machines, containers, managed platforms, functions, and specialized compute from workload, control, portability, and operations constraints. | Not Started |
| Cloud Storage and Data Architecture | Place object, block, file, database, analytics, and backup services across data classes, access patterns, residency, durability, and lifecycle needs. | Not Started |
| Cloud-Native Application and Integration Patterns | Compose stateless services, managed dependencies, configuration, service discovery, and platform boundaries without re-teaching Part 20 pattern mechanics. | Not Started |
| Event, Queue, and Messaging Architectures in Cloud | Choose brokers, queues, event buses, and streaming services for ordering, replay, delivery, and integration; recap Part 07 distributed messaging concepts. | Not Started |
| Resilience, Availability, and Disaster-Recovery Architectures | Design failure domains, multi-zone/region topologies, recovery objectives, backups, failover, and dependency-aware degraded modes. | Not Started |
| Hybrid Cloud and Multi-Cloud Architecture | Decide when hybrid or multiple providers are justified; address identity, network, data gravity, portability, operations, and failure boundaries. | Not Started |
| Edge, Regional, and Global Workload Placement | Place compute and data near users/devices while balancing latency, sovereignty, connectivity, update, and fleet-management constraints. | Not Started |
| Cloud Security, Governance, and Compliance Architecture | Apply guardrails, policy boundaries, encryption/key ownership, workload isolation, evidence, and compliance controls across accounts and services. | Not Started |
| Cloud Cost, Performance, and Sustainability Architecture | Connect workload shape to cost drivers, utilization, commitment, data transfer, right-sizing, carbon impact, and architectural trade-offs. | Not Started |
| Cloud Migration and Modernization Architecture | Choose rehost/refactor/replatform/replace/retire paths, migration waves, coexistence, data cutover, rollback, and post-migration optimization. | Not Started |
| Cloud Architecture Reviews and Reference Designs | Apply cross-provider review checklists and case studies to complete workloads; map detailed AWS Well-Architected reviews to Part 11. | Not Started |
