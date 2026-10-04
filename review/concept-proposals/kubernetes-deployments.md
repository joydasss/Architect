# Kubernetes Deployments Concept Proposals

Source: `12_Kubernetes/CH02_Deployments.md`

## Proposed concepts

| Concept | Proposed ownership | Boundary and overlap notes |
|---|---|---|
| Deployment-to-ReplicaSet-to-Pod ownership and reconciliation hierarchy | CH02 Deployments | Deployment chooses the current template and rollout policy; ReplicaSet maintains one template's Pod count. CH01 owns Pod lifecycle; CH03 owns ReplicaSet selector and cardinality reconciliation. |
| Deployment template revision and rollout trigger semantics | CH02 Deployments | A Pod-template change creates a new revision; scaling alone does not. Revisions are represented by retained ReplicaSets, not by an immutable release artifact. |
| Rolling-update availability and surge constraints | CH02 Deployments | Kubernetes `maxUnavailable`/`maxSurge` behavior, rounding, capacity and termination interactions. General release safety stays with Part 13; availability objectives stay with Part 07. |
| Deployment progress conditions and stalled-rollout diagnosis | CH02 Deployments | Owns progress deadlines, status conditions, and controller retry behavior. Tooling or higher-level automation may act on status but does not change the controller's built-in behavior. |
| Deployment rollback boundary and revision retention | CH02 Deployments | Rollback restores a retained Pod template; it does not revert external data or side effects. Part 07/Part 06 own data consistency and recovery mechanisms. |

## Recap-only concepts

- Pod lifecycle, probes, resource semantics, and graceful termination: CH01 Pods owns the API-level behavior.
- ReplicaSet selector and desired-versus-observed cardinality reconciliation: CH03 ReplicaSets owns these mechanics.
- General controller/reconciliation and distributed failure principles: Part 07 owns the broad concepts; CH02 applies them to Deployment controllers.
- General deployment pipelines, approvals, and release governance: Part 13 owns delivery practice; this chapter owns only Kubernetes rollout semantics.
- Horizontal Pod Autoscaler behavior: CH09 owns scaling loops; CH02 notes that `.spec.replicas` needs a single authority.
- Voluntary disruption and PodDisruptionBudget mechanics: CH01 covers the Pod boundary; this chapter distinguishes them from Deployment-controlled rolling updates.

## Reconciliation note

Do not merge these rows into Part 09's managed Kubernetes service-selection and upgrade ownership. Kubernetes-native Deployment object semantics belong in Part 12. During the Part 12 batch review, reconcile `maxUnavailable`/`maxSurge` with CH01 Pod readiness and CH09 autoscaler capacity assumptions.
