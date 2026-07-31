# Batch Review — Part 02 Batch 5 (Lean UX, Product Discovery, Product Strategy)

Reviewed files:
[02_Design_Thinking_and_Product_Management/CH13_Lean_UX.md](../02_Design_Thinking_and_Product_Management/CH13_Lean_UX.md),
[02_Design_Thinking_and_Product_Management/CH14_Product_Discovery.md](../02_Design_Thinking_and_Product_Management/CH14_Product_Discovery.md),
[02_Design_Thinking_and_Product_Management/CH15_Product_Strategy.md](../02_Design_Thinking_and_Product_Management/CH15_Product_Strategy.md).

This batch closes the Design Thinking subsection (13/13) and opens the
Product Management subsection (2/18).

## [overlap] Dual-track agile claimed at different depths — resolved, no edit needed

**Finding**: "Lean UX" Section 7 mentions the dual-track discovery/delivery
pattern with an explicit recap+link note (not a full-ownership claim).
"Product Discovery" Section 4.1 independently wrote the full first-principles
treatment ("The Discovery/Delivery Track Split (Dual-Track Agile)").

**Assessment**: not a real conflict — "Lean UX" already recapped rather than
re-taught. Arbitrated ownership to "Product Discovery" in `CORE_CONCEPTS.md`
(the more foundational, dedicated chapter for this concept). No chapter edit
required.

## [overlap] Two similarly-named "cadence" concepts — reviewed, non-duplicative

**Finding**: "Product Discovery" Section 4.4 teaches "Continuous Discovery
Cadence" (weekly customer-touchpoint habit, Torres). "Lean UX" Section 4.8
teaches "Continuous Small-Batch Validation Cadence" (cycle-length/batch-size
discipline within a Lean UX loop).

**Assessment**: read both sections in full — these operate on different axes
(frequency of customer contact vs. batch size of validated work) and neither
re-derives the other. No edit made.

## [gap] General Lean Startup / Build-Measure-Learn had no formal owner — fixed

**Finding**: "Lean UX" flagged that the general (non-design-specific) Lean
Startup / Build-Measure-Learn loop was only ever mentioned at
historical-evolution depth in "Research" and "Rapid Prototyping", with no
`CORE_CONCEPTS.md` ownership row for future chapters (e.g. Experimentation,
A/B Testing) to recap against.

**Fix applied**: added a `CORE_CONCEPTS.md` row assigning the general concept
to "Research" (earliest/deepest existing mention), so "Lean UX"'s
design-scoped Build-Measure-Learn application has a clear recap target.

## [resolution] JTBD and PR-FAQ ownership — cleanly closed out

**Finding**: Jobs-to-be-Done and PR-FAQ ("Working Backwards") had both been
explicitly flagged as deferred-not-taught by "Personas" and "Problem Framing"
in earlier batches, naming a future Product Strategy chapter as the likely
owner.

**Assessment**: "Product Strategy" is that chapter and now fully teaches both
in Sections 4.4-4.5. Resolves two long-pending forward references with no
conflict — neither Personas nor Problem Framing taught either concept beyond
a disambiguation mention.

## [cross-reference] Placeholder references now resolvable — fixed

**Finding**: "Product Discovery" and "Product Strategy" were both drafted in
parallel with no visibility into each other or into "Lean UX," so each used
generic prose mentions ("this part's forthcoming Product Strategy chapter,"
"a parallel, not-yet-visible Lean UX chapter") instead of links.

**Fix applied**: updated cross-references in both chapters (Introduction,
Section 7/8 narrative, Section 16, and Further Reading) to direct links now
that all three files exist: CH14 -> CH13/CH15, CH15 -> CH13/CH14.

## [completeness] All three chapters

All three chapters contain the full 27-section template (verified via
section-header scan: 27/27 each, no duplication).

## [diagram/depth compliance] All three chapters

All three chapters were authored after the STYLE_GUIDE.md diagram-rule and
elaboration-rule update and were explicitly instructed to follow it in their
task prompts. Verified: CH13 has 12 inline Mermaid diagrams (incl. 1
landscape-wrapped), CH14 has 10, CH15 has 14 (incl. 1 landscape-wrapped OKR
cascade) — all comfortably above the 2-3 floor, and Section 4 subsections
read as full explanations (definition/mechanism/decision implications/failure
mode/scenario), not pointer bullets.

## Summary

No unresolved ownership conflicts. One ownership gap fixed (general Lean
Startup/Build-Measure-Learn now has a formal owner). Two long-pending
forward references (JTBD, PR-FAQ) resolved cleanly. Cross-reference
placeholders updated to direct links across CH14 and CH15. No completeness,
diagram, or depth issues found — this batch met the newly strengthened
STYLE_GUIDE bar on the first pass.
