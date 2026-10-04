# Kubernetes Storage Concept Proposals

Source: `12_Kubernetes/CH07_Storage.md`

## Proposed concepts

| Concept | Proposed ownership | Boundary and overlap notes |
|---|---|---|
| PersistentVolume/PersistentVolumeClaim binding and reclaim lifecycle | CH07 Storage | Owns Kubernetes PV/PVC API states, one-to-one binding, static/dynamic provisioning boundary, owner protection, and reclaim-policy semantics. Part 09 owns storage product behavior; Part 06 owns database persistence. |
| StorageClass as provisioner and scheduling policy | CH07 Storage | Owns class selection, defaulting, provisioner contract, reclaim/expansion policy, and WaitForFirstConsumer coordination with topology. Provider-specific parameters remain with Part 09. |
| CSI controller/node lifecycle for provisioning, attach, mount, and resize | CH07 Storage | Owns Kubernetes-facing responsibility split and lifecycle evidence, not vendor backend internals. Part 09 owns service drivers and backend guarantees; Part 05 owns filesystem and kernel mechanics. |
| Kubernetes volume access modes and topology implications | CH07 Storage | Owns API-level matching/placement meaning, including RWO versus RWOP distinctions and why modes are not general application locks. CH08 owns Pod mount declarations. |
| VolumeSnapshot/VolumeSnapshotContent recovery workflow | CH07 Storage | Owns snapshot CRD/controller/CSI request chain and deletion policy. Part 06 owns database-consistent backup and restore; Part 07 owns recovery objectives. |

## Recap-only concepts

- Pod identity, lifecycle, resource, and scheduling semantics: CH01 Pods owns the Pod contract.
- Pod `volumes`, `volumeMounts`, `volumeDevices`, ephemeral volume lifetime, and container sharing: CH08 Volumes owns consumption inside the Pod.
- Container filesystem, mount namespace, and kernel block behavior: Part 05 CH26/CH28 owns those internals.
- Storage service performance, durability, encryption, pricing, snapshots, and provider-specific behavior: Part 09 CH06 owns these service guarantees and mechanics.
- Database persistence, transaction consistency, and engine-native recovery: Part 06 owns those concepts.

## Reconciliation note

Part 09 CH08 already summarizes Kubernetes integration with cloud storage and CSI. Keep this chapter upstream-facing: claim/binding semantics, StorageClass policy, topology coordination, CSI lifecycle boundaries, and snapshot resource flow. During Part 12 batch review, compare CH08 Volumes so it consumes the PVC/PV model without re-teaching provisioning and reclaim behavior.
