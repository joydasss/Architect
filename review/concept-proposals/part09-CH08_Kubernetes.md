# Concept Proposals — Kubernetes (cloud-managed) (CH08, Part 09 Cloud Computing)

New cross-cutting concepts introduced by the in-depth rewrite of
[Managed Kubernetes on AWS, Azure, and Google Cloud](../../09_Cloud_Computing/CH08_Kubernetes.md).
Existing CH08 rows in `CORE_CONCEPTS.md` (responsibility matrix, cluster modes
and node-pool ownership, upgrade/disruption/version-support planning, CNI/CSI/
identity/load-balancing integrations, managed Kubernetes versus managed
containers) remain as they are.

| Concept | Suggested owner | Scope note |
|---|---|---|
| Provider fleet products and sameness-based identity scoping | [Kubernetes](../../09_Cloud_Computing/CH08_Kubernetes.md) | GKE fleets (Config Sync, Policy Controller, Multi Cluster Gateway, rollout sequencing, namespace and Workload Identity sameness), Azure Kubernetes Fleet Manager (update runs, hub-cluster resource placement), and the composed EKS alternatives. Section 18. Part 12 CH15 owns provider-neutral multi-cluster and fleet-boundary concepts (its own proposal names Part 09 as owner of provider fleet products) and should recap and link; Part 12 CH12 owns GitOps mechanics. |
| Managed Kubernetes control-plane tiers and SLA scope | [Kubernetes](../../09_Cloud_Computing/CH08_Kubernetes.md) | Distinguishes API-server uptime SLAs (EKS standard and Provisioned Control Plane, AKS Free/Standard/Premium with and without zones, GKE zonal/regional/Autopilot) from data-plane commitments (GKE Autopilot Pod SLA, AKS Automatic pod readiness SLA), with the SLA-to-downtime-budget conversion and the "control plane down means no changes, not no traffic" consequence. Sections 2.5 and 3. Monitoring (CH10) owns the managed-control-plane visibility boundary; Part 07 and Part 14 own SLO practice. |

Related concepts this chapter recaps rather than owns:

- Instance metadata credential exposure and IMDSv2 protections: proposed for
  Compute (CH04) in `part09-CH04_Compute.md`; CH08 section 15 applies it to
  nodes and links to CH04.
- Provider quota-versus-capacity model: proposed for AWS (CH01) and Compute
  (CH04); CH08 sections 10.6 and 14 apply it to node provisioning and link to
  Compute.
