# Enriched Rewrite Status

**Status date:** 2026-11-05  
**Scope:** Parts 01–26, all 391 chapter files found in the workspace.  
**Purpose:** Planning inventory of chapters that are rewritten, partially rewritten, or still need a complete rewrite. This is not a content approval or technical fact-check.

## Reference and Status Rules

The attached `part09-rewrite-brief.md` is the structural and depth reference for this inventory: teach mechanisms and trade-offs, include worked examples and failure behavior, use at least eight distinct diagrams, and aim for roughly 11,000–15,000 words without padding. The attached `part16-17-rewrite-brief.md` sets a higher target for those parts, but the user has confirmed Parts 09, 16, and 17 are complete. Part 18 and Part 20 chapter work in this conversation was measured against the Part 09 brief; Part 18 remains below that target and is therefore partial.

Status labels:

- **Rewritten:** a chapter-level in-depth rewrite has been completed or the user explicitly marked the entire part complete. The chapter has substantial teaching content and a rewritten structure. This label does not guarantee every provider fact, link, acronym, calculation, or diagram has been independently validated.
- **Partial rewrite:** the chapter has meaningful existing content or a rewrite pass, but still needs targeted deepening, structural modernization, validation, or completion against the applicable brief.
- **Complete rewrite needed:** the chapter remains a short or shallow draft, generally far below the reference depth, and needs a substantive rewrite rather than a light edit.
- **Targeted reference review:** the chapter is primarily a reference/appendix artifact; review accuracy, consistency, links, and cross-references rather than imposing a textbook chapter-length target.

Word counts below are a current inventory using `\b[\w-]+\b` over the full Markdown file, including code and Mermaid blocks. They are useful for triage, not a substitute for the Part 16/17 brief's diagram-excluded word count or a qualitative coverage review. Status is based on the rewrite work and user direction recorded to date, not word count alone.

## Summary by Part

| Part | Chapters | Current average words | Disposition | Follow-up |
|---|---:|---:|---|---|
| 01 Architecture Mindset | 3 | 5,594 | Partial rewrite | Review structure and deepen where the topic map requires; all use the older 27-section format. |
| 02 Design Thinking and Product Management | 31 | 9,552 | Partial rewrite | Substantial chapters exist; modernize structure and check short/uneven chapters against the topic map. |
| 03 Software Engineering Foundations | 5 | 12,339 | Partial rewrite | Strong existing depth, but no in-depth rewrite is recorded; perform coverage and accuracy review. |
| 04 Frontend Architecture | 8 | 12,189 | Partial rewrite | Strong existing depth; assess structure, topic coverage, and current framework facts. |
| 05 Networking and OS | 29 | 11,570 | Partial rewrite | Strong existing depth; review currency, ownership boundaries, and chapter structure. |
| 06 Databases and Storage | 22 | 11,958 | Partial rewrite | Strong existing depth and exemplar chapters; check consistency and topic-map coverage. |
| 07 System Design and Distributed Systems | 19 | 10,578 | Partial rewrite | Substantial existing content; review depth and consistency, especially shorter chapters. |
| 08 API Architecture | 11 | 8,658 | Partial rewrite | Substantial but uneven; deepen shorter chapters and modernize the old structure. |
| 09 Cloud Computing | 16 | 23,294 | Rewritten | User-confirmed complete; aligns with the attached cloud rewrite brief. Recheck drifting provider facts before publication. |
| 10 Cloud Architecture | 15 | 3,226 | Complete rewrite needed | Most chapters are about 2,800–4,000 words; expand substantially. |
| 11 AWS Well-Architected Framework | 10 | 3,022 | Complete rewrite needed | Most chapters are about 2,200–5,000 words; expand and verify current AWS-specific details. |
| 12 Kubernetes | 15 | 2,943 | Complete rewrite needed | Most chapters are about 2,400–3,900 words; deepen Kubernetes mechanisms and current-version details. |
| 13 DevOps | 17 | 1,573 | Complete rewrite needed | Mostly short drafts; several are near 1,000–1,600 words. |
| 14 Observability | 13 | 1,122 | Complete rewrite needed | Mostly short drafts; expand the core mechanics and operational examples. |
| 15 Security | 16 | 14,231 | Rewritten | All 16 chapters rewritten in this work against the Part 09 brief; run a separate technical/currency review. |
| 16 AI, ML, and GenAI | 31 | 31,753 | Rewritten | User-confirmed complete; current files are substantial. A separate review should resolve legacy unsourced anecdotes and check that word targets exclude Mermaid. |
| 17 AI Architecture | 15 | 30,323 | Rewritten | User-confirmed complete; current files are substantial. Verify diagram-excluded word counts and technical currency. |
| 18 Enterprise Architecture | 11 | 8,140 | Partial rewrite | All chapters received earlier rewrite passes, but most remain below the 11,000-word reference; re-expand selectively or fully. |
| 19 Performance Engineering | 14 | 1,009 | Complete rewrite needed | Chapters are about 825–1,149 words; rewrite to teach mechanisms and application. |
| 20 Architecture Patterns | 18 | 14,453 | Rewritten | All 18 chapters rewritten in this work; a few exceed 15,000 words. Run final editorial and technical validation. |
| 21 Architecture Documentation | 11 | 6,555 | Partial rewrite | CH01–CH05 have substantial rewrites; CH06–CH11 have first halves only. CH04 needs a fresh read because of intervening edits. |
| 22 Architectural Thinking and Decision Practice | 10 | 953 | Complete rewrite needed | Chapters are about 869–1,028 words; no rewrite is recorded. |
| 23 Soft Skills | 15 | 917 | Complete rewrite needed | Chapters are about 828–975 words; deepen with applied architecture scenarios and exercises. |
| 24 Real-World Case Studies | 25 | 989 | Complete rewrite needed | Chapters are about 891–1,073 words; develop complete case narratives, evidence, trade-offs, and outcomes. |
| 25 Additional Architect Competencies | 6 | 1,133 | Complete rewrite needed | Chapters are about 1,096–1,163 words; deepen each competency. |
| 26 Appendices and Glossary | 5 | 1,728 | Targeted reference review | Check terminology, acronym coverage, references, links, and generated index/TOC consistency; use fit-for-purpose depth rather than the chapter word target. |

## Chapter-Level Disposition

Each row below identifies every chapter in the part and its disposition. A range such as `CH01–CH11` means every chapter in that inclusive range has that status.

### Rewritten

| Part | Chapters | Notes |
|---|---|---|
| 09 | CH01–CH16 | User-confirmed complete. |
| 15 | CH01–CH16 | In-depth rewrites completed; see validation caveats below. |
| 16 | CH01–CH31 | User-confirmed complete. Some earlier session edits were later replaced by full rewrites. |
| 17 | CH01–CH15 | User-confirmed complete. |
| 20 | CH01–CH18 | In-depth rewrites completed; current inventory includes intervening user/formatter edits to these files. |

**Rewritten total: 96 chapters across 5 parts.**

### Partial Rewrite

| Part | Chapters | Why partial |
|---|---|---|
| 01 | CH01–CH03 | Existing chapters have roughly 4,700–6,900 words, but retain the older chapter structure and have no in-depth rewrite status. |
| 02 | CH01–CH31 | Existing chapters range roughly 3,800–15,800 words; the part is uneven and has not been brought through a consistent rewrite/coverage review. |
| 03 | CH01–CH05 | Substantial chapters (roughly 9,800–15,300 words), but no rewrite pass is recorded. |
| 04 | CH01–CH08 | Substantial chapters (roughly 10,800–15,100 words), but no rewrite pass is recorded. |
| 05 | CH01–CH29 | Substantial chapters (roughly 9,900–14,900 words), but no rewrite pass is recorded. |
| 06 | CH01–CH22 | Substantial chapters (roughly 9,200–15,300 words), but no rewrite pass is recorded. |
| 07 | CH01–CH19 | Substantial chapters (roughly 7,300–15,200 words), but no rewrite pass is recorded. |
| 08 | CH01–CH11 | Substantial but uneven chapters (roughly 6,100–10,000 words), but no rewrite pass is recorded. |
| 18 | CH01–CH11 | Earlier rewrites exist (roughly 5,650–9,850 words). They are not yet at the current 11,000–15,000-word reference depth, and need coverage/quality review. |
| 21 | CH01–CH11 | CH01–CH05 have prior substantial rewrites (roughly 7,200–10,600 words); CH06–CH11 are incomplete first halves (roughly 3,400–4,900 words). Re-read CH04 before editing because of reported intervening user/formatter changes. |

**Partial total: 150 chapters across 10 parts.**

### Complete Rewrite Needed

| Part | Chapters | Current range | Priority rationale |
|---|---|---:|---|
| 10 | CH01–CH15 | 2,797–3,968 | Short drafts across the entire part. |
| 11 | CH01–CH10 | 2,203–4,985 | Short drafts; provider-specific claims need current verification. |
| 12 | CH01–CH15 | 2,398–3,899 | Short drafts; Kubernetes APIs and behavior are version-sensitive. |
| 13 | CH01–CH17 | 970–4,230 | Most chapters are very short; rewrite and deepen each. |
| 14 | CH01–CH13 | 825–2,250 | Most chapters are very short; develop the observability mechanisms and practice. |
| 19 | CH01–CH14 | 918–1,149 | All chapters are short drafts. |
| 22 | CH01–CH10 | 869–1,028 | All chapters are short drafts; no rewrite has started. |
| 23 | CH01–CH15 | 828–975 | All chapters are short drafts. |
| 24 | CH01–CH25 | 891–1,073 | All case-study chapters need full scenario development. |
| 25 | CH01–CH06 | 1,096–1,163 | All chapters are short drafts. |

**Complete rewrite needed total: 140 chapters across 10 parts.**

### Targeted Reference Review

| Part | Chapters | Review scope |
|---|---|---|
| 26 | CH01–CH05 | Validate definitions, acronym expansions, citations/references, internal links, and generated indexes/TOC. Do not inflate reference material to a textbook chapter target. |

## Validation Notes and Risks

- The all-part inventory found **391 chapter files**. The status groups account for all of them: 96 rewritten, 150 partial, 140 requiring complete rewrite, and 5 appendices/reference chapters for targeted review.
- The Part 09 brief calls for about 11,000–15,000 words of real content. The Part 16/17 brief calls for at least 23,000 words excluding Mermaid. The current inventory's word counts include Mermaid and code, so a proper compliance count for Parts 16 and 17 still requires the brief's diagram-exclusion method.
- Part 16 and Part 17 are marked rewritten because the user explicitly said they were completed. The inventory shows their content is substantial, but not every chapter was independently checked against all topic-map items.
- Parts 15 and 20 have not received a full technical fact-check. Several subagents explicitly did not verify provider, standards, or protocol facts against current primary documentation. Mermaid diagrams were generally counted, not rendered.
- Part 18 is classified partial even though every chapter received an earlier rewrite pass: its word counts remain below the current depth reference.
- Part 21 is incomplete. CH06–CH11 need their remaining sections. CH04 requires a fresh read before further work because its file was reported as changed by a user or formatter.
- Earlier Part 16 enrichment inserted some unsourced production-style anecdotes. A source-or-reframe review remains recommended before publication.
- Some Part 20 chapter files changed after the earlier rewrite pass. This status inventory uses the latest available file contents and word counts gathered on 2026-11-05.
- No chapter status is a substitute for checking accuracy, link validity, acronym expansion, Markdown lint, diagram rendering, arithmetic, and ownership boundaries before publication.

## Suggested Work Order

1. Finish Part 21 CH06–CH11, first reading the current CH04 file and respecting any user edits.
2. Rewrite Part 22 CH01–CH10, using the Part 09 depth target unless a part-specific brief supersedes it.
3. Rewrite Parts 10–14 and 19, where the current drafts are consistently short.
4. Rewrite Parts 23–25, including end-to-end scenarios where appropriate.
5. Bring Part 18 to the current depth target and validate all Parts 15 and 20 chapters.
6. Conduct targeted reviews of Parts 01–08, 02 in particular because its chapters vary widely in length, and Part 26 reference material.
7. Clean up the previously identified unsourced Part 16 anecdotes and perform a final cross-part ownership and link audit.
