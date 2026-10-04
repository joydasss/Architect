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

## Reading order (26 parts)

Ordered per the chat's own "Suggested Book Sequence," not the original
Roman-numeral Part numbering (each overview cross-references its original Part).
Row position defines reading order. Supplemental modules retain their stable
folder IDs (23-26) while appearing beside the related core parts.

| Part ID | Part | Original Part(s) | Chapters | Status |
|---|---|---|---|---|
| 01 | [Architecture Mindset](01_Architecture_Mindset/PART_OVERVIEW.md) | I | 3 | **3 Edited (first full-scale batch)** |
| 02 | [Design Thinking and Product Management](02_Design_Thinking_and_Product_Management/PART_OVERVIEW.md) | XV, XIV | 31 | **31/31 Edited (Design Thinking complete 13/13; Product Mgmt 18/18) — Part 02 COMPLETE** |
| 03 | [Software Engineering Foundations](03_Software_Engineering_Foundations/PART_OVERVIEW.md) | II | 5 | **5/5 Edited — Part 03 COMPLETE** |
| 04 | [Frontend Architecture](04_Frontend_Architecture/PART_OVERVIEW.md) | III | 8 | **8/8 Edited — Part 04 COMPLETE** |
| 05 | [Networking and Operating Systems](05_Networking_and_OS/PART_OVERVIEW.md) | VII + new | 29 | **29/29 Edited — Part 05 COMPLETE** |
| 06 | [Databases and Storage](06_Databases_and_Storage/PART_OVERVIEW.md) | VI | 22 | Complete — 22/22 |
| 07 | [System Design and Distributed Systems](07_System_Design_and_Distributed_Systems/PART_OVERVIEW.md) | IV | 19 | Complete — 19/19 |
| 08 | [API Architecture](08_API_Architecture/PART_OVERVIEW.md) | V | 11 | Complete — 11/11 |
| 09 | [Cloud Computing](09_Cloud_Computing/PART_OVERVIEW.md) | VIII | 16 | **16/16 Drafted** |
| 10 | [Cloud Architecture (supplements Part 09)](10_Cloud_Architecture/PART_OVERVIEW.md) | new | 15 | **15/15 Drafted; all topics mapped** |
| 11 | [AWS Well-Architected Framework (supplements Parts 09 and 10)](11_AWS_Well_Architected_Framework/PART_OVERVIEW.md) | new | 10 | **10/10 Drafted; all topics mapped** |
| 12 | [Kubernetes](12_Kubernetes/PART_OVERVIEW.md) | IX | 15 | **15/15 Drafted; all topics mapped** |
| 13 | [DevOps](13_DevOps/PART_OVERVIEW.md) | X | 17 | **17/17 Drafted** |
| 14 | [Observability](14_Observability/PART_OVERVIEW.md) | XI | 13 | **13/13 Drafted** |
| 15 | [Security](15_Security/PART_OVERVIEW.md) | XII | 16 | **16/16 Drafted** |
| 16 | [AI, Machine Learning, and Generative AI](16_AI_and_GenAI/PART_OVERVIEW.md) | XIII | 31 | **31/31 Drafted** |
| 17 | [AI Architecture (supplements Part 16)](17_AI_Architecture/PART_OVERVIEW.md) | new | 15 | **15/15 Drafted** |
| 18 | [Enterprise Architecture](18_Enterprise_Architecture/PART_OVERVIEW.md) | XVI | 11 | **11/11 Drafted** |
| 19 | [Performance Engineering](19_Performance_Engineering/PART_OVERVIEW.md) | XVII | 14 | **14/14 Drafted** |
| 20 | [Architecture Patterns](20_Architecture_Patterns/PART_OVERVIEW.md) | XVIII | 18 | **18/18 Drafted** |
| 21 | [Architecture Documentation](21_Architecture_Documentation/PART_OVERVIEW.md) | XIX | 11 | **11/11 Drafted** |
| 22 | [Architectural Thinking and Decision Practice (supplements Part 01)](22_Architectural_Thinking_and_Decision_Practice/PART_OVERVIEW.md) | new | 10 | **10/10 Drafted** |
| 23 | [Soft Skills](23_Soft_Skills/PART_OVERVIEW.md) | XX | 15 | **15/15 Drafted** |
| 24 | [Real-World Case Studies](24_Real_World_Case_Studies/PART_OVERVIEW.md) | XXI | 25 | **25/25 Drafted (audit pending)** |
| 25 | [Additional Architect Competencies](25_Additional_Architect_Competencies/PART_OVERVIEW.md) | new | 6 | **6/6 Drafted** |
| 26 | [Appendices and Glossary](26_Appendices_and_Glossary/PART_OVERVIEW.md) | new | 5 | **5/5 Drafted** |

**Total: ~391 planned chapter/topic entries** across 26 parts by the chapter
counts in this table (the original ~180 "chapter" estimate corresponds more
closely to the top-level modules; some listed entries may be grouped into
fewer full chapters after detailed planning, per the Level 3/4
chapter-versus-topic distinction).

Supplemental modules appear at their contextual place in the sequence:
Cloud Architecture (10) and AWS Well-Architected (11) follow Cloud Computing;
AI Architecture (17) follows AI and GenAI; Architectural Thinking and
Decision Practice (22) precedes Soft Skills and builds on Part 01. Their
numbered folders match their current sequence positions.

## Pilot chapters (proof of the anti-repetition pipeline)

| Chapter | Part | File | Status |
|---|---|---|---|
| HTTP | 05_Networking_and_OS | [CH01_HTTP.md](05_Networking_and_OS/CH01_HTTP.md) | Edited (enriched to full depth, Batch 16) |
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

## Deferred Post-Completion To-Do

Keep this validation open until all planned modules and chapters are complete:

- [ ] Re-run gRPC runtime integration and compile both `.proto` schemas for
  Part 08 CH03 using `grpcio`, `grpcio-tools`, and `protoc`; these tools were
  unavailable during the chapter's authored validation.
