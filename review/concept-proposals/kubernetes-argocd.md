# Kubernetes Argo CD Concept Proposals

Source: `12_Kubernetes/CH12_ArgoCD.md`

## Proposed concepts

| Concept | Proposed ownership | Boundary and overlap notes |
|---|---|---|
| Argo CD source-render-compare-sync architecture | CH12 Argo CD | Owns Application source/revision/render context, repo-server, application controller, live-state cache, status, and sync. CH11 owns Helm rendering/package details. |
| AppProject and dual authorization boundary | CH12 Argo CD | Owns source/destination/resource-kind allowlists and Argo CD project roles. CH13 owns security foundations; Kubernetes destination RBAC remains distinct from Argo CD authorization. |
| Automated sync, self-heal, prune, and resource ownership | CH12 Argo CD | Owns Git-to-live drift policies, field ignores, pruning, and Application deletion/finalizer semantics. CH10 owns Operator lifecycle; CH07 owns storage/data retention contracts. |
| GitOps promotion and immutable deployment evidence | CH12 Argo CD | Owns Application target revisions, artifact/config promotion, multi-source risks, break-glass reconciliation, and Git revert versus controller rollback. Part 13 owns generic pipeline and Git mechanics. |
| ApplicationSet and app-of-apps fleet boundaries | CH12 Argo CD | Owns Application generation, bootstrap relationships, child lifecycle, and deletion blast radius. CH13 owns trust and permissions for generator inputs. |
| Sync phases, waves, hooks, and deletion ordering | CH12 Argo CD | Owns Argo CD-specific sync ordering and hook semantics. CH11 owns Helm hooks; CH10 owns long-running domain lifecycle and migrations. |
| Argo CD availability and restore boundary | CH12 Argo CD | Owns control-plane outage/recovery and controller/repository failure effects. Part 14 owns generic observability and Part 09 owns managed service availability. |

## Recap-only concepts

- Helm chart format, values, hooks, release revisions, and artifact integrity: CH11 Helm.
- Custom resources, Operator reconciliation, CRD migration, and resource finalizers: CH10 Operators.
- Kubernetes APIs, workload health, pruning effects, and storage data lifecycle: CH01, CH07, CH10, and CH13.
- Git and delivery pipeline mechanics: Part 13; general security and supply-chain foundations: Part 15.

## Reconciliation note

Emphasize that Argo CD compares rendered desired state with live state; `Synced` does not guarantee service health. Automated sync and pruning are separate controls. Application deletion, app-of-apps ownership, and field-ignore policies can alter resource ownership or data, so test the exact version and recovery behavior before enabling them broadly.
