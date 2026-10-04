# Kubernetes Helm Concept Proposals

Source: `12_Kubernetes/CH11_Helm.md`

## Proposed concepts

| Concept | Proposed ownership | Boundary and overlap notes |
|---|---|---|
| Helm chart packaging and rendered-manifest contract | CH11 Helm | Owns chart structure, templates, release context, schema validation, and rendered output. CH01-CH10 own Kubernetes resource semantics. |
| Helm values precedence and configuration ownership | CH11 Helm | Owns values coalescing, environment overrides, schema, and secret handling in release configuration. CH13 owns Kubernetes Secret security and Part 13 owns pipeline secret mechanics. |
| Helm release revision and rollback boundary | CH11 Helm | Owns install, upgrade, uninstall, history, hooks, and the limits of resource rollback. Application/database migrations remain with their domain owner; CH12 owns GitOps rollback/reconciliation. |
| Helm CRD packaging lifecycle caveat | CH11 Helm | Owns chart-specific CRD placement and version-specific lifecycle behavior. CH10 owns CRD schema evolution, conversion, stored-object migration, and finalizers. Mark Helm 3/4 differences explicitly. |
| Helm dependency locking, OCI distribution, and provenance | CH11 Helm | Owns chart artifact distribution and package verification. Part 09 owns registry products; Part 15 owns general software supply-chain integrity. |
| Helm versus Kustomize, Operator, and GitOps boundaries | CH11 Helm | Owns tool-selection tradeoffs without duplicating CH10 Operator behavior or CH12 Argo CD reconciliation. One desired-state owner per resource set. |

## Recap-only concepts

- Kubernetes object schemas, resource ownership, and reconciliation: CH01-CH10.
- Domain lifecycle automation and custom resource versioning: CH10 Operators.
- Git as continuously reconciled desired state, application health, and sync: CH12 Argo CD.
- General delivery pipeline design: Part 13.
- Registry services and provider credentials: Part 09; general artifact integrity: Part 15.

## Reconciliation note

Use an explicit Helm client version in documentation and automation. Several current Helm pages warn that their chart/value/provenance content has not yet been updated for Helm 4, so lifecycle assertions about CRDs, upgrades, and signatures need validation against the pinned release. Do not characterize release rollback as undoing external side effects or persistent application data.
