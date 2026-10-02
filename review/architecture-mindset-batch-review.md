# Batch Review — Part 01 (Architecture Mindset)

Reviewed files:
[01_Architecture_Mindset/CH01_What_is_Software_Architecture.md](../01_Architecture_Mindset/CH01_What_is_Software_Architecture.md),
[01_Architecture_Mindset/CH02_Role_of_a_Solution_Architect.md](../01_Architecture_Mindset/CH02_Role_of_a_Solution_Architect.md),
[01_Architecture_Mindset/CH03_Architecture_Thinking.md](../01_Architecture_Mindset/CH03_Architecture_Thinking.md).

This is the first batch with more than two chapters authored in parallel,
isolated sessions, and the first where the proposed concept sets genuinely
collided (rather than being disjoint, as in the HTTP+REST pilot). Three
concepts — Conway's Law, fitness functions, and Architecture Decision
Records — were independently written in full by two or three of the three
chapters.

## [overlap] Conway's Law claimed by CH01 and CH03 — fixed

**Finding**: "What is Software Architecture?" Section 3 gives Conway's Law a
full historical/definitional treatment (1968 quote, Inverse Conway Maneuver).
"Architecture Thinking" Section 4 independently re-explained the same
definition as one of its "Core Concepts" bullets.

**Fix applied**: arbitrated ownership to "What is Software Architecture?"
(deeper, more foundational treatment). Trimmed "Architecture Thinking"'s
bullet to a recap + link
([CH03_Architecture_Thinking.md](../01_Architecture_Mindset/CH03_Architecture_Thinking.md)),
keeping only its decision-input framing. Logged in `CORE_CONCEPTS.md`
Batch 2 merge log.

## [overlap] Fitness functions claimed by CH01 and CH03 — fixed

**Finding**: "What is Software Architecture?" Section 9 self-declares
ownership with a definition and Section 10 code examples. "Architecture
Thinking" Section 16 (Testing) independently redefined the same concept at
similar depth.

**Fix applied**: arbitrated ownership to "What is Software Architecture?";
trimmed "Architecture Thinking"'s Testing-section bullet to a recap + link.

## [overlap] Architecture Decision Records claimed by CH01/CH02 (deferred) vs. CH03 (owned) — fixed

**Finding**: "What is Software Architecture?" and "Role of a Solution
Architect" both deferred full ADR ownership to Architecture Documentation
(Part 21), which doesn't exist yet. "Architecture Thinking" independently
wrote the deepest treatment (template, worked ADR-007 example, review
checklist) and claimed ownership outright. "Role of a Solution Architect"
additionally wrote its own full worked example (ADR-014) and planned a
second, separate `adr-template.md` file — a genuine content duplicate, not
just a competing ownership claim.

**Fix applied**: arbitrated ownership to "Architecture Thinking" as the
pragmatic current owner (best/most complete treatment; Part 21 doesn't exist
yet to arbitrate in its favor). Fixed "What is Software Architecture?"'s
dangling Part 21 link to point at "Architecture Thinking" instead. Trimmed
"Role of a Solution Architect"'s ADR-014 worked example and the planned
`adr-template.md` file down to a recap + link, keeping only its RACI-specific
framing (no orphaned code-block fragments remained after the edit — verified).

## [overlap] Quality attributes (CH01 taxonomy vs. CH03 trade-off framing) — reviewed, no fix needed

**Finding**: "What is Software Architecture?" Section 4.6 owns the quality
attributes taxonomy/definition. "Architecture Thinking" Section 4 uses
"quality attributes as the currency of trade-off analysis" as one of its own
core concepts.

**Assessment**: not duplicative — "Architecture Thinking" does not re-list or
redefine the taxonomy, only applies it as a trade-off-analysis input. No edit
made.

## [overlap] ATAM (CH01 mention vs. CH03 ownership) — consistent, no fix needed

**Finding**: "What is Software Architecture?" names ATAM only in passing as an
example of a decision framework, explicitly deferring to "Architecture
Thinking." "Architecture Thinking" fully owns and teaches trade-off analysis
/ ATAM. The two chapters' assumptions matched without coordination.

**Assessment**: no conflict, no edit needed.

## [overlap] 4+1 view model (CH01 full treatment vs. CH03 historical mention) — reviewed, no fix needed

**Finding**: "What is Software Architecture?" Section 4.8 gives the 4+1 view
model a full dedicated treatment (all five views explained). "Architecture
Thinking" Section 2 (Historical Evolution) mentions it in one sentence as
part of a chronological list of influential ideas, consistent with how both
chapters treat other historical influences (e.g., REST, TOGAF) elsewhere.

**Assessment**: proportionate — a brief historical mention, not a re-teach.
No edit made.

## [completeness] All three chapters

All 27 STYLE_GUIDE.md sections are present, in the correct order, with
non-trivial content, in all three chapters (verified by section-header scan).

## [accuracy] All three chapters

No factual errors found in the reviewed sections (Conway's Law attribution
and date, ADR authorship (Nygard, 2011), fitness functions (Ford/Parsons/Kua,
2017), 4+1 view model (Kruchten, 1995), ATAM (Bass/Clements/Kazman, SEI),
Boehm's cost-of-change curve).

## [cross-reference] All three chapters

- Sibling links between the three chapters (e.g., CH02 → CH03 for trade-off
  reasoning, CH01 → CH03 for ADRs, CH03 → CH01 for Conway's Law / fitness
  functions) resolve correctly now that all three files exist in the same
  folder — no dangling same-part links found after the edit pass.
- Forward references to parts 18 (Enterprise Architecture), 17 (Architecture
  Patterns), and 18 (Architecture Documentation) point to `PART_OVERVIEW.md`
  stubs since none of those parts have chapters drafted yet — acceptable for
  now, matches the established pattern from the HTTP/REST pilot review;
  revisit once those parts exist.
- No forward reference from Part 01 back to HTTP/REST (05, 08) was expected
  or found, appropriately — the domains don't naturally intersect at this
  level.

## [consistency] All three chapters

Terminology (quality attribute, one-way/two-way door, ASR, fitness function)
is used consistently across all three chapters after the edit pass.

## Summary

3 significant overlap issues found and fixed (Conway's Law, fitness
functions, ADRs) — all caused by parallel isolated authoring with no
cross-visibility between sibling chapters, the same root cause as the
HTTP/REST pilot's REST-Section-4 issue, but at higher frequency (3 conflicts
across 3 chapters vs. 1 across 2). Two additional near-miss overlaps (quality
attributes, 4+1 view model) were reviewed and judged non-duplicative. No
completeness, accuracy, or consistency issues. No further edit pass required
beyond the fixes already applied in this review.

**Process note for scaling**: as parallel batch size grows, concept-overlap
frequency appears to scale faster than linearly with chapter count (3
chapters produced 3 conflicts vs. 2 chapters producing 1) — worth revisiting
whether `CORE_CONCEPTS.md` should be consulted/updated *between* parallel
sub-agent calls (e.g., staggered rather than fully parallel dispatch) for
larger batches later in the project.
