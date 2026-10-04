# Kubernetes Security Concept Proposals

Source: `12_Kubernetes/CH13_Security.md`

## Proposed concepts

| Concept | Proposed ownership | Boundary and overlap notes |
|---|---|---|
| Kubernetes API authentication, authorization, admission, and audit request path | CH13 Security | Owns how identity and policy transitions protect Kubernetes API operations. Part 15 owns generic security engineering; Part 09 owns provider identity and control-plane services. |
| Human, automation, node, workload, and provider identity boundaries | CH13 Security | Owns ServiceAccount tokens, node identity, least-privilege Kubernetes RBAC, and workload federation inputs. Part 09 owns provider IAM role and managed identity configuration. |
| Pod Security Standards and admission enforcement | CH13 Security | Owns namespace-level profile enforcement, staged migration, exceptions, and webhook risk. CH01 owns Pod securityContext mechanics; CH06 owns network policy. |
| Kubernetes namespace tenancy and residual shared-node risk | CH13 Security | Owns the difference between namespaced control-plane policy and hard kernel/node isolation. CH06/CH07 own network/storage behavior; Part 09 evaluates provider isolation and cost. |
| Secret API storage, access, delivery, and rotation | CH13 Security | Owns Kubernetes Secret limitations, etcd encryption configuration and access policy. CH08 owns volume projection semantics; Part 09 owns KMS products; credential domain owners own lifecycle. |
| Image provenance, admission trust, and node runtime exposure | CH13 Security | Owns Kubernetes image admission/runtime security boundary. Part 15 owns build and artifact supply-chain foundations; Part 09 owns registries and node services. |
| Kubernetes compromise containment and evidence preservation | CH13 Security | Owns cluster-level incident sequence and recovery requirements. Part 14 owns telemetry pipeline architecture; Part 15 owns incident-response principles and program. |

## Recap-only concepts

- NetworkPolicy implementation and CNI support: CH06 Networking.
- Volume projection, Secret mounts, and read-only semantics: CH08 Volumes.
- Pod lifecycle and securityContext field details: CH01 Pods.
- Generic threat modeling, image supply chain, security program, and incident process: Part 15.
- Cloud IAM, KMS, managed-cluster boundaries, and registry services: Part 09.
- Kubernetes log/metric/tracing pipeline architecture: CH14 Observability and Part 14.

## Reconciliation note

Do not equate namespace isolation with hard multi-tenant isolation. Treat Pod creation as delegated execution authority, not a harmless object-write permission. Kubernetes Secret base64 encoding is not encryption; storage encryption, authorization, node access, mounts, and consumer rotation are separate controls. Version and distribution caveats must be explicit for Pod Security, token, and admission behavior.
