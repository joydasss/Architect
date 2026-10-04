# Kubernetes Operators Concept Proposals

Source: `12_Kubernetes/CH10_Operators.md`

## Proposed concepts

| Concept | Proposed ownership | Boundary and overlap notes |
|---|---|---|
| Operator API and domain-lifecycle boundary | CH10 Operators | Owns when a custom resource/controller is justified over templating or a runbook, and the domain intent/status contract. Part 07 owns general distributed reconciliation theory. |
| Controller reconciliation contract | CH10 Operators | Owns watch-to-queue-to-reconcile behavior, idempotency, retries, conflict handling, partial progress, and status generation. Do not duplicate generic controller/control-loop mechanics outside the Kubernetes API context. |
| CRD schema, scope, and status design | CH10 Operators | Owns API shape, namespaced versus cluster scope, structural schema, status subresource, conditions, and least-surprise field ownership. CH13 owns security policy. |
| CRD served/storage versions and conversion migration | CH10 Operators | Owns custom API compatibility, conversion webhooks, stored object migration, deprecation, and version removal sequencing. Part 07 covers general compatibility strategy. |
| Operator deletion finalizer and managed-resource ownership | CH10 Operators | Owns finalizer state and user-data retention decisions. Kubernetes owner-reference garbage collection remains a platform mechanism; CH07 owns persistent storage lifecycle. |
| Operator runtime, RBAC, and webhook trust boundary | CH10 Operators | Owns controller/webhook deployment and required Kubernetes permissions. CH13 owns security foundations; Part 09 owns provider credentials and managed service operations. |

## Recap-only concepts

- Generic reconciliation, retries, eventual convergence, and distributed failure: Part 07.
- Chart templating, release history, and distribution: CH11 Helm.
- Git desired-state delivery: CH12 Argo CD; generic Git and pipeline mechanics remain Part 13.
- Pod readiness, resources, volumes, and disruption: CH01, CH08, and CH09.
- Kubernetes RBAC/security foundations: CH13; provider IAM and managed Kubernetes integration: Part 09.

## Reconciliation note

Keep the Operator distinct from Helm and GitOps: Helm can install an Operator, and GitOps can declare custom resources, but neither supplies domain reconciliation by itself. CRD deletion and finalizer cleanup can affect persistent data; avoid presenting uninstall as a routine package removal without an explicit retention and recovery policy.
