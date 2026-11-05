# Concept proposals: Part 09 CH03 Google Cloud Platform

Source chapter: [Google Cloud Platform Architecture](../../09_Cloud_Computing/CH03_GCP.md)

These rows are proposed additions to `CORE_CONCEPTS.md`. The chapter teaches each one in full. A merge step should reconcile them with proposals from CH05 Networking, CH09 IAM, and CH04 Compute, which touch adjacent material. Owner paths are given relative to the repository root, as `CORE_CONCEPTS.md` uses them.

| Concept | Proposed owner | Scope note |
|---|---|---|
| Google Cloud VPC Service Controls service perimeters, access levels, and ingress/egress rules | `09_Cloud_Computing/CH03_GCP.md` | API-level data perimeter on top of IAM; dry-run rollout and restricted VIP. Private endpoint routing remains with CH05 Networking; cross-provider data-perimeter patterns belong to Part 10 |
| Google Cloud IAM policy types and evaluation order: allow (union inheritance), deny, and principal access boundary policies | `09_Cloud_Computing/CH03_GCP.md` | Provider-specific policy types and staged evaluation; cross-provider principal, role, and federation patterns remain with CH09 IAM |
| Google Cloud project deletion lifecycle and liens | `09_Cloud_Computing/CH03_GCP.md` | `DELETE_REQUESTED` 30-day window, billing unlink, lien and deny-policy protection; independent backup boundaries remain with CH06 Storage |
| Cloud quota versus physical capacity (allocation, rate, and concurrent quotas; reservations) | `09_Cloud_Computing/CH04_Compute.md` or `09_Cloud_Computing/CH03_GCP.md` | CH03 teaches the Google Cloud quota types, hierarchy levels, and location dimensions. If CH04 already owns cross-provider capacity procurement, CH03 should own only the Google Cloud quota model and CH04 the capacity-versus-quota principle |
