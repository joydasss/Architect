# Kubernetes Pods Concept Proposals

Source: `12_Kubernetes/CH01_Pods.md`

## Proposed concepts

| Concept | Proposed ownership | Boundary and overlap notes |
|---|---|---|
| Kubernetes Pod as the API-level scheduling, co-location, and lifecycle unit | CH01 Pods | Owns Pod-level specification, placement, ephemeral identity, and shared-resource contract. Part 05 CH28 retains Linux namespace/cgroup primitives and the container-to-orchestration hand-off; Part 09 CH08 retains managed-cluster responsibility. |
| Container restart versus Pod replacement and controller recovery | CH01 Pods | Distinguishes kubelet-local container restart from a new Pod UID and higher-level controller replacement. CH02/CH03 apply the distinction to Deployment and ReplicaSet reconciliation without re-deriving the Pod lifecycle. |
| Kubernetes native sidecar lifecycle | CH01 Pods | Owns restartable init-container ordering, readiness/startup interaction, termination order, and resource coupling. Generic sidecar-proxy/service-mesh architecture remains with Part 05 CH11 and Part 20 where applicable. |
| Kubernetes startup, readiness, and liveness probe action semantics | CH01 Pods | Owns the Kubernetes mapping from probe results to startup gating, endpoint readiness, and container restart. Part 14 retains generic health/observability and alerting principles. |
| Pod resource request, limit, and QoS scheduling/eviction contract | CH01 Pods | Owns Kubernetes API-level scheduling and eviction implications. Part 05 CH25/CH28 retains kernel memory, OOM, CPU, and cgroup enforcement mechanisms; CH09 applies requests to autoscaling. |

## Recap-only concepts

- Linux namespaces, cgroups, container runtime, and kernel OOM behavior: Part 05 CH25 and CH28 own the mechanisms; CH01 explains only the Kubernetes Pod contract built on them.
- Managed control plane, node pools, cloud service integrations, and provider operating boundaries: Part 09 CH08 owns these topics.
- Deployment and ReplicaSet controller semantics: Part 12 CH02 and CH03 own rollout and replica reconciliation.
- Service selectors and endpoint discovery: Part 12 CH04 owns stable service routing; CH01 notes only that readiness affects endpoint eligibility.
- CNI, CSI, persistent-volume provisioning, and cloud storage/network products: Part 12 CH06-CH08 and Part 09 service chapters own those mechanisms.
- Generic security, identity threat modeling, and observability practice: Parts 15 and 14 own these foundations; CH01 applies their implications to Pod sharing and probes.

## Reconciliation note

CORE_CONCEPTS.md already contains a Part 05 entry for the container-to-orchestration hand-off and Pod namespace composition. Keep that row scoped to Linux primitive composition and link from this chapter; do not move or duplicate its kernel-level explanation. During the Kubernetes batch merge, compare CH02, CH03, CH06-CH09, and CH13 proposals against the corresponding Part 05/09/14/15 ownership rows before merging.
