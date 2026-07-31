# Batch Review — Part 02 Batch 4 (Usability Testing, Accessibility, Service Design)

Reviewed files:
[02_Design_Thinking_and_Product_Management/CH10_Usability_Testing.md](../02_Design_Thinking_and_Product_Management/CH10_Usability_Testing.md),
[02_Design_Thinking_and_Product_Management/CH11_Accessibility.md](../02_Design_Thinking_and_Product_Management/CH11_Accessibility.md),
[02_Design_Thinking_and_Product_Management/CH12_Service_Design.md](../02_Design_Thinking_and_Product_Management/CH12_Service_Design.md),
with cross-check updates to
[CH05_Journey_Mapping.md](../02_Design_Thinking_and_Product_Management/CH05_Journey_Mapping.md)
and [CH09_Wireframing.md](../02_Design_Thinking_and_Product_Management/CH09_Wireframing.md).

## [correctness] Duplicate chapter-body append in CH11/CH12 — fixed

**Finding**: Both CH11 and CH12 contained an accidental second copy of chapter
sections appended after the first complete 27-section sequence (likely from
parallel-session conflict recovery).

**Fix applied**:
- Normalized [CH11_Accessibility.md](../02_Design_Thinking_and_Product_Management/CH11_Accessibility.md) to a single 1-27 sequence.
- Normalized [CH12_Service_Design.md](../02_Design_Thinking_and_Product_Management/CH12_Service_Design.md) to a single 1-27 sequence.
- Re-validated heading count: each file now has exactly 27 numbered sections.

## [overlap] CH10 vs CH11 testing scope — reviewed, no conflict

**Finding**: Both chapters discuss testing, but at different abstraction levels.
- CH10 owns usability-method protocol architecture (formative/summative,
  moderated/unmoderated, readiness gates, severity-risk triage, closure ledger).
- CH11 owns accessibility-specific evidence layering and release expectations
  (automation + manual + assistive-technology validation; focus/error contracts).

**Assessment**: complementary, not duplicative. No trimming required.

## [overlap] CH05 defer-to-Service-Design boundary — now resolved

**Finding**: CH05 previously deferred full service-blueprint depth to a
not-yet-drafted Service Design chapter.

**Fix applied**: Updated CH05 comparison-table owner note to direct link:
[CH12_Service_Design.md](../02_Design_Thinking_and_Product_Management/CH12_Service_Design.md).

## [cross-reference] CH09 Usability placeholder — now resolved

**Finding**: CH09 still pointed to a "not yet drafted" Usability Testing owner
placeholder.

**Fix applied**: Updated CH09 comparison-table owner to
[CH10_Usability_Testing.md](../02_Design_Thinking_and_Product_Management/CH10_Usability_Testing.md).

## [completeness] New chapters

All three new chapters (CH10-CH12) contain the full 27-section template in the
required order.

## [summary]

1 major correctness issue found and fixed (duplicate appended chapter bodies in
CH11/CH12), 2 now-resolvable cross-reference updates applied (CH05->CH12,
CH09->CH10), and no unresolved ownership conflicts across this batch.
