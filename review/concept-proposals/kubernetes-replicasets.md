# Kubernetes ReplicaSets Concept Proposals

Source: `12_Kubernetes/CH03_ReplicaSets.md`

## Proposed concepts

| Concept | Proposed ownership | Boundary and overlap notes |
|---|---|---|
| ReplicaSet selector-driven Pod cardinality reconciliation | CH03 ReplicaSets | Owns desired-versus-observed Pod membership, controller creation/deletion, and status interpretation. General controller loops remain recap-only to Part 07. |
| ReplicaSet owner-reference and orphan-Pod adoption behavior | CH03 ReplicaSets | Owns how matching uncontrolled Pods may be acquired and how controller ownership affects membership. Part 12 CH02 owns Deployment-level ReplicaSet adoption and rollout semantics. |
| ReplicaSet template change versus Deployment-managed revision | CH03 ReplicaSets | Owns the limitation that a direct ReplicaSet template change does not roll existing Pods; CH02 owns template hashes, revisions, and controlled rolling updates. |
| ReplicaSet scale-down selection and termination overlap | CH03 ReplicaSets | Owns best-effort Pod deletion selection and the distinction between desired count and resource-consuming terminating Pods. CH01 owns Pod termination lifecycle. |

## Recap-only concepts

- Pod identity, restart versus replacement, resource and probe behavior: CH01 Pods owns the Pod API and lifecycle.
- Deployment-to-ReplicaSet ownership, rolling updates, revision history, and rollback limits: CH02 Deployments owns these interactions.
- General reconciliation and eventual convergence: Part 07 owns the distributed-systems framing; this chapter applies it to ReplicaSet membership.
- Kubernetes Service endpoint selection and Pod networking: CH04 Services and CH06 Networking own those paths.
- Provider-managed control-plane and node operations: Part 09 CH08 owns cloud-service boundaries.

## Reconciliation note

CORE_CONCEPTS.md already assigns Pod namespace composition and container-to-orchestration hand-off to Part 05 CH28. Keep that concept scoped to OS isolation primitives. This chapter owns the ReplicaSet controller's selector, owner-reference, and replica-count contract, not the underlying namespace implementation. Compare CH02's Deployment/ReplicaSet proposal during the Part 12 batch merge to keep the ownership hierarchy explicit.
