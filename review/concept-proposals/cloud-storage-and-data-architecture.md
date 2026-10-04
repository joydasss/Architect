# Cloud Storage and Data Architecture Concepts

Source: `10_Cloud_Architecture/CH06_Cloud_Storage_and_Data_Architecture.md`

## Proposed concepts

| Concept | Proposed ownership | Boundary and overlap notes |
|---|---|---|
| Cloud workload data-placement and authority model across primary, derived, cached, analytical, and recovery copies | CH06 Cloud Storage and Data Architecture | Cross-service architecture for authority, locality, freshness, lifecycle, and recovery dependencies; Part 06 owns database/storage internals and Part 09 owns provider service contracts. |

## Recap-only concepts

- Database engines, replication, caching, partitioning, and consistency internals: Part 06.
- Provider storage classes, redundancy, snapshots, and backup services: Part 09 CH06.
- Generic RPO/RTO and recovery semantics: Part 07; workload recovery composition is Part 10 CH09.
