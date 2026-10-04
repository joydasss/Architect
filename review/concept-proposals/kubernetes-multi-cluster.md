# Kubernetes Multi-Cluster Concept Proposals

Source: `12_Kubernetes/CH15_Multi_Cluster.md`

## Proposed concepts

| Concept | Proposed ownership | Boundary and overlap notes |
|---|---|---|
| Independent cluster and fleet-management boundary | CH15 Multi-Cluster | Owns the distinction between per-cluster APIs/control loops and fleet-level inventory, policy, rollout, and control. Part 09 owns provider fleet products; CH12 owns GitOps implementation. |
| Multi-cluster decision and topology selection | CH15 Multi-Cluster | Owns when independent cluster failure, tenant, lifecycle, or region boundaries justify fleet overhead. CH13 owns namespace versus stronger tenant isolation; Part 10 owns hybrid/multi-cloud design. |
| Fleet version compatibility and staged policy rollout | CH15 Multi-Cluster | Owns per-cluster version/add-on matrix, canary/wave rollout, and stop/rollback gates. Part 09 owns provider upgrade products; CH10 owns Operator CRD evolution. |
| Cross-cluster service discovery and traffic path | CH15 Multi-Cluster | Owns the implementation boundary for ServiceExport/ServiceImport, gateways, global routing, and health detection. CH04-CH06 own in-cluster Service, ingress, and network behavior. |
| Cross-cluster workload identity and trust | CH15 Multi-Cluster | Owns how identities and credentials are federated or kept cluster-specific. CH13 owns Kubernetes identity security; Part 09 owns provider IAM federation. |
| Multi-cluster data authority and failover | CH15 Multi-Cluster | Owns fleet traffic/workload handoff and the need for fencing, promotion, and recovery objectives. Part 07 owns data consistency and replication semantics; Part 09 owns managed replication products. |
| Fleet observability and failure evidence | CH15 Multi-Cluster | Owns stable cluster identity and fleet correlation/failure boundaries. CH14 owns signal pipelines and alert engineering. |

## Recap-only concepts

- Provider cluster provisioning, account/region, quota, pricing, and managed-fleet operations: Part 09.
- Hybrid/multi-cloud placement and governance: Part 10.
- GitOps application generation and sync: CH12 Argo CD; generic Git and pipeline mechanics: Part 13.
- Distributed data consistency, leader authority, and replication correctness: Part 07.
- Cross-cluster security and trust: CH13; observability pipeline: CH14.

## Reconciliation note

A second cluster is not sufficient for availability. Traffic routing, identity, capacity, data replication, fencing, failover, and failback must be designed and tested. Treat Multi-Cluster Services API resources as an API contract requiring a compatible implementation; do not imply that they provide the network dataplane or failover policy by themselves.
