# Book Plan — Table of Contents

Master table of contents for the *Modern Solution Architecture Handbook*.
This is the source of truth used by every prompt/agent to avoid duplicate or
missing chapters — see the Concept Ownership Rule in
[STYLE_GUIDE.md](STYLE_GUIDE.md) and the registry in
[CORE_CONCEPTS.md](CORE_CONCEPTS.md).

Per-chapter status values: `Not Started` → `Drafted` → `Concepts Staged` →
`Merged` → `Reviewed` → `Edited`. Full chapter lists live in each part's
`PART_OVERVIEW.md`; this file tracks part-level progress and the two pilot
chapters explicitly.

## Reading order (22 parts)

Ordered per the chat's own "Suggested Book Sequence," not the original
Roman-numeral Part numbering (each overview cross-references its original Part).

| # | Part | Original Part(s) | Chapters | Status |
|---|---|---|---|---|
| 01 | [Architecture Mindset](01_Architecture_Mindset/PART_OVERVIEW.md) | I | 3 | **3 Edited (first full-scale batch)** |
| 02 | [Design Thinking and Product Management](02_Design_Thinking_and_Product_Management/PART_OVERVIEW.md) | XV, XIV | 31 | **31/31 Edited (Design Thinking complete 13/13; Product Mgmt 18/18) — Part 02 COMPLETE** |
| 03 | [Software Engineering Foundations](03_Software_Engineering_Foundations/PART_OVERVIEW.md) | II | 5 | **5/5 Edited — Part 03 COMPLETE** |
| 04 | [Frontend Architecture](04_Frontend_Architecture/PART_OVERVIEW.md) | III | 8 | Not Started |
| 05 | [Networking and Operating Systems](05_Networking_and_OS/PART_OVERVIEW.md) | VII + new | 29 | **1 Reviewed (HTTP, pilot)** |
| 06 | [Databases and Storage](06_Databases_and_Storage/PART_OVERVIEW.md) | VI | 22 | Not Started |
| 07 | [System Design and Distributed Systems](07_System_Design_and_Distributed_Systems/PART_OVERVIEW.md) | IV | 18 | Not Started |
| 08 | [API Architecture](08_API_Architecture/PART_OVERVIEW.md) | V | 11 | **1 Edited (REST, pilot)** |
| 09 | [Cloud Computing](09_Cloud_Computing/PART_OVERVIEW.md) | VIII | 16 | Not Started |
| 10 | [Kubernetes](10_Kubernetes/PART_OVERVIEW.md) | IX | 15 | Not Started |
| 11 | [DevOps](11_DevOps/PART_OVERVIEW.md) | X | 17 | Not Started |
| 12 | [Observability](12_Observability/PART_OVERVIEW.md) | XI | 13 | Not Started |
| 13 | [Security](13_Security/PART_OVERVIEW.md) | XII | 16 | Not Started |
| 14 | [AI and GenAI](14_AI_and_GenAI/PART_OVERVIEW.md) | XIII | 19 | Not Started |
| 15 | [Enterprise Architecture](15_Enterprise_Architecture/PART_OVERVIEW.md) | XVI | 11 | Not Started |
| 16 | [Performance Engineering](16_Performance_Engineering/PART_OVERVIEW.md) | XVII | 14 | Not Started |
| 17 | [Architecture Patterns](17_Architecture_Patterns/PART_OVERVIEW.md) | XVIII | 18 | Not Started |
| 18 | [Architecture Documentation](18_Architecture_Documentation/PART_OVERVIEW.md) | XIX | 11 | Not Started |
| 19 | [Soft Skills](19_Soft_Skills/PART_OVERVIEW.md) | XX | 15 | Not Started |
| 20 | [Real-World Case Studies](20_Real_World_Case_Studies/PART_OVERVIEW.md) | XXI | 25 | Not Started |
| 21 | [Additional Architect Competencies](21_Additional_Architect_Competencies/PART_OVERVIEW.md) | new | 6 | Not Started |
| 22 | [Appendices and Glossary](22_Appendices_and_Glossary/PART_OVERVIEW.md) | new | 5 | Not Started |

**Total: ~296 chapter/topic entries** across 22 parts (the ~180 "chapter"
estimate from the chat corresponds roughly to the top-level items above; many
entries, e.g. under Databases or Networking, will be grouped as topics within
a smaller number of full chapters once drafted, per the chat's Level 3/4
chapter-vs-topic distinction).

## Pilot chapters (proof of the anti-repetition pipeline)

| Chapter | Part | File | Status |
|---|---|---|---|
| HTTP | 05_Networking_and_OS | [CH01_HTTP.md](05_Networking_and_OS/CH01_HTTP.md) | Reviewed (no changes required) |
| REST | 08_API_Architecture | [CH01_REST.md](08_API_Architecture/CH01_REST.md) | Edited (overlap with HTTP resolved) |

Full pipeline completed: Drafted → Concepts Staged → Merged →
[Batch Review](review/http-rest-batch-review.md) → Edited. See
[CORE_CONCEPTS.md](CORE_CONCEPTS.md#merge-log) for the merge log and the
review file above for the overlap finding and fix applied to REST.

## Scaling out

Once both pilots reach `Edited`, repeat the same
plan → author → diagram → code → merge → review → edit loop per chapter,
updating this file's per-part chapter tables (in each `PART_OVERVIEW.md`) as
chapters move through each status. See README.md § Scaling out.
