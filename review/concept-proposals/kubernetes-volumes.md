# Kubernetes Volumes Concept Proposals

Source: `12_Kubernetes/CH08_Volumes.md`

## Proposed concepts

| Concept | Proposed ownership | Boundary and overlap notes |
|---|---|---|
| Pod volume declaration and per-container mount contract | CH08 Volumes | Owns how `.spec.volumes`, `volumeMounts`, and `volumeDevices` expose sources to containers. CH01 owns Pod identity and shared resource boundary; Part 05 owns filesystem and mount namespace mechanics. |
| Kubernetes ephemeral-volume lifetime taxonomy | CH08 Volumes | Owns `emptyDir`, projected, CSI ephemeral, and generic ephemeral Pod-lifecycle distinctions. CH07 owns PVC/PV and StorageClass provisioning/reclaim mechanics. |
| Projected-volume composition and source-update behavior | CH08 Volumes | Owns composing ConfigMap, Secret, Downward API, and token sources into a path and the requirement for application reload. CH13 owns identity/secret security. |
| `subPath`, read-only mount, and propagation behavior at the Pod boundary | CH08 Volumes | Owns Kubernetes fields and their workload consequences; Part 05 owns kernel mount propagation internals and CH13 owns security decisions. |
| Pod mount-source trust boundary (`hostPath` and image volumes) | CH08 Volumes | Owns when node-coupled or read-only image-backed sources fit a Pod; Part 05 owns container filesystem primitives and CH13 owns threat modeling/admission controls. |

## Recap-only concepts

- Pod co-location, shared networking, container restart, and Pod replacement: CH01 Pods owns the Pod lifetime contract.
- PV/PVC binding, StorageClass, CSI provisioning/attach/reclaim, topology, and snapshots: CH07 Storage owns these mechanisms.
- Linux mount namespaces, bind mounts, OverlayFS, and container writable layers: Part 05 CH26/CH28 own the operating-system and container runtime mechanics.
- Kubernetes Secret governance and service account/workload identity: CH13 Security owns cluster security; Part 09 owns provider secret services.

## Reconciliation note

CORE_CONCEPTS.md contains the Part 05 row for Pod namespace composition and the container-to-orchestration hand-off, but no Kubernetes volume ownership row. Keep CH08 focused on the Kubernetes volume API and lifecycle behavior. CH07 must remain the authority for storage provisioning and backend contracts; this chapter should explain only enough claim consumption to distinguish a persistent source from Pod-scoped and projected sources.
