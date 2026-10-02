# Batch Review — Part 02 Batch 7 (Journey Mapping [PM], Story Mapping, Roadmaps)

Reviewed files:
[02_Design_Thinking_and_Product_Management/CH19_Journey_Mapping_Product_Management.md](../02_Design_Thinking_and_Product_Management/CH19_Journey_Mapping_Product_Management.md),
[02_Design_Thinking_and_Product_Management/CH20_Story_Mapping.md](../02_Design_Thinking_and_Product_Management/CH20_Story_Mapping.md),
[02_Design_Thinking_and_Product_Management/CH21_Roadmaps.md](../02_Design_Thinking_and_Product_Management/CH21_Roadmaps.md).

This batch resolves the disambiguated Product Management "Journey Mapping"
chapter (flagged since Batch 4/6) and two long-pending Product Strategy
forward references (strategy-to-roadmap contract; external roadmap
disclosure).

## [overlap] "Now/Next/Later" used by both Story Mapping and Roadmaps — reviewed, non-duplicative

**Finding**: "Story Mapping" Section 4.4 uses "Now/Next/Later" to label
within-release backlog cuts (task-level, weeks-to-months horizon). "Roadmaps"
Section 4.4 fully teaches "The Now/Next/Later Horizon Format" as a
multi-quarter, initiative/theme-level communication convention.

**Assessment**: both chapters explicitly draw this altitude distinction
themselves — "Story Mapping" Section 4.7 includes a diagram distinguishing
its release lines from a roadmap's coarser theme sequencing, and explicitly
defers roadmap construction to "the not-yet-drafted Roadmaps chapter";
"Roadmaps" Section 4.4 explicitly distinguishes its format from Product
Strategy's Three Horizons on an orthogonal axis. Same label, two different
altitudes, no re-teaching in either direction. No edit needed.

## [gap, flagged for future] "Walking skeleton" — narrowly scoped, no current conflict

**Finding**: "Story Mapping" scoped "walking skeleton" narrowly to its own
application (minimum-sufficient task per activity) and flagged that the term
also has a general software-delivery meaning (Cockburn/Crystal,
continuous-delivery thin-slice architecture proof).

**Assessment**: no conflict today — no Software Engineering Foundations or
DevOps chapter exists yet to compete for the general term. Flagging in this
review (and in `CORE_CONCEPTS.md`'s merge log) for re-check when Part 03 or
Part 13 is drafted.

## [resolution] Product Strategy's two forward references — cleanly closed out

**Finding**: "Product Strategy" Section 4.7 (strategy-to-roadmap translation
contract) and Section 13 (controlled external roadmap disclosure) both
explicitly named a future "Roadmaps" chapter as the owner.

**Assessment**: "Roadmaps" is that chapter and resolves both — a six-step
contract-construction pipeline and a tiered external-disclosure policy —
without re-teaching Product Strategy's Three Horizons, strategy stack, or
JTBD. Clean resolution, no conflict.

## [cross-reference] Stale placeholders now resolvable — fixed

**Finding**: three chapters drafted before this batch still had "not yet
drafted" placeholders for chapters that now exist:
- "Empathy"'s sibling "Journey Mapping" (CH05) comparison table still named
  a generic "future chapter" for both the PM Journey Mapping and Story
  Mapping variants.
- "Product Strategy" (CH15) comparison table still said "Roadmaps chapter
  (not yet drafted)".
- "Competitive Analysis" (CH17, drafted in the previous batch alongside
  Market Analysis) still said "Market Analysis chapter (not yet drafted)"
  in its own comparison table — missed in the prior batch's cross-reference
  cleanup pass.

**Fix applied**: updated all three to direct links (CH19, CH20, CH21, CH16
respectively).

## [completeness] All three chapters

All three chapters contain the full 27-section template (verified: 27/27
section headers each).

## [diagram/depth compliance] All three chapters

CH19 has 10 inline Mermaid diagrams (incl. 1 landscape-wrapped), CH20 has 10
(incl. 1 landscape-wrapped backbone+release-line grid), CH21 has 13 (incl. 2
landscape-wrapped) — all well above the 2-3 floor. Section 4 subsections in
all three read as full explanations, consistent with the strengthened
STYLE_GUIDE bar.

## Summary

Zero ownership conflicts. One same-label/different-altitude term reviewed
and confirmed non-duplicative (Now/Next/Later). One term flagged for future
re-check (walking skeleton). Three stale cross-reference placeholders fixed
(one of which was a miss from the previous batch's cleanup pass — worth
double-checking older chapters' comparison tables in future batches, not
just the newest ones).
