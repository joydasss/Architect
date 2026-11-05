# Concept proposals: Part 09 CH02 Azure

Proposed additions to `CORE_CONCEPTS.md` from the in-depth rewrite of
[CH02 Azure](../../09_Cloud_Computing/CH02_Azure.md). Each concept is taught
fully in that chapter and is not currently listed in `CORE_CONCEPTS.md`.
In the registry, the owner cell would be the link
`[Azure](09_Cloud_Computing/CH02_Azure.md)`, matching existing rows.

| Concept | Proposed owner | Scope note |
|---|---|---|
| Azure control-plane mutation guards: management locks versus deployment-stack deny settings versus Policy `denyAction` | Azure (Part 09 CH02) | Who each guard stops, who can bypass it, control-plane-only scope, and operational side effects (blocked `POST` actions, deployment-history pruning); data protection features remain with Storage |
| Azure logical-to-physical availability-zone mapping per subscription | Azure (Part 09 CH02) | Per-subscription zone-number mapping, discovery through `availabilityZoneMappings` and `checkZonePeers`, and its effect on cross-subscription co-location and failure analysis; the AWS zone-ID equivalent stays with CH01 |
| Azure quota versus capacity and the two-tier regional vCPU quota | Azure (Part 09 CH02) | Subscription-per-region family and total vCPU quotas, deallocated-core counting, and capacity reservations as the only capacity guarantee; provider-neutral capacity procurement stays with Compute |
| Azure managed-identity token caching and authorization-change propagation | Azure (Part 09 CH02) | About 24-hour token cache per resource, group-claim delay versus direct-assignment propagation, and the "anyone who runs code or assigns the identity" rule; cross-provider workload identity federation stays with IAM |

Merge note: the first and fourth rows touch IAM (CH09) and Secrets Management
(CH13). If the merge step prefers, the fourth row can be folded into the
existing CH09 row "Workload identity federation and managed cloud identities"
as an Azure-specific sub-note owned by CH02.
