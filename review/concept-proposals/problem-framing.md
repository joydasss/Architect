# Concept Proposals — Problem Framing chapter

Staged for merge into [CORE_CONCEPTS.md](../../CORE_CONCEPTS.md). Do not edit
CORE_CONCEPTS.md directly from this chapter's session.

| Concept | Proposed Owner | Scope note |
|---|---|---|
| Point-of-View (POV) statement ("[User] needs [need] because [insight]") | Problem Framing chapter | Full construction discipline: user/need/insight slots, need-as-outcome-not-feature rule, insight-as-genuine-cause rule |
| How-Might-We (HMW) statement | Problem Framing chapter | The artifact [Empathy's comparison table](../../02_Design_Thinking_and_Product_Management/CH01_Empathy.md#21-comparison-table) already forward-referenced as owned here; full construction technique plus the seven reframing lenses (amp up the positive, remove the negative, explore the opposite, question an assumption, identify unexpected resources, change the status quo, analogy from another context) |
| Abstraction laddering (laddering up/down) | Problem Framing chapter | Scope-calibration technique for a need or HMW statement; distinguished explicitly from root-cause analysis (different axis: scope vs. causal depth) |
| Five Whys applied to problem statements | Problem Framing chapter | Root-cause vs. symptom framing technique, borrowed from the Toyota Production System and taught here in its problem-framing application specifically (not the general TPS/manufacturing history, which is only briefly cited) |
| Problem statement canvas | Problem Framing chapter | Full field-by-field structured brief artifact (background, target user, evidence citations, current-state pain, POV, selected HMWs, desired outcome, non-goals, constraints, assumptions log) |
| Opportunity Solution Tree (Teresa Torres) | Problem Framing chapter | Three-level outcome/opportunity/solution structure as a continuous-discovery alternative to a one-time canvas |
| Assumption surfacing (for problem statements) | Problem Framing chapter | Explicit validated/unvalidated tagging discipline applied to a problem statement's embedded claims |
| "Solution in disguise" detection check | Problem Framing chapter | The blank-substitution test for whether a stated "need" has secretly already picked a specific solution |

## Notes for the merge step

- This chapter fulfills the forward-reference in [Empathy's comparison
  table](../../02_Design_Thinking_and_Product_Management/CH01_Empathy.md#21-comparison-table),
  which already listed "Problem (How-Might-We) statement" as owned by a
  future "Problem Framing" chapter. No content changes to `CH01_Empathy.md`
  were made from this session — the merge step should update that table's
  final-column link (currently "Problem Framing (this part, not yet
  drafted)") to point at this chapter's file now that it exists, and
  likewise for any other sibling chapter (Research, Personas) that carries
  the same placeholder-style forward reference.
- **Amazon's "Working Backwards" / PR-FAQ** is named only for
  disambiguation in Section 21's comparison table, not taught in depth —
  flagging it here in case a future Product Strategy or Product Discovery
  chapter (Product Management subsection, not yet drafted) wants to claim
  it; this chapter takes no ownership position on it.
- **Jobs-to-be-Done (JTBD)** was already flagged by
  `review/concept-proposals/personas.md` as a likely candidate for a
  Product Strategy or Problem Framing chapter. This chapter did **not**
  end up teaching JTBD at any depth (it uses POV/HMW instead as its core
  technique) — the merge step should route JTBD ownership to whichever
  future chapter (most likely Product Strategy) actually teaches it in
  depth, not to this chapter.
- **Sibling chapters drafted in parallel, not visible to this session**:
  "User Interviews" (this part, chapter 4) and "Journey Mapping" (this
  part, chapter 5) were both being drafted concurrently and did not exist
  as files at the time of this writing. This chapter deliberately:
  - Did not claim ownership of pain-point *identification* — only of
    reframing an already-identified pain point (from Journey Mapping, once
    it exists) into a bounded problem statement, per this chapter's
    assignment.
  - Did not teach interview/validation technique in depth (Section 16
    references "problem validation interviews" but defers the actual
    interviewing craft to User Interviews).
  - Linked to `PART_OVERVIEW.md` rather than a guessed filename for both,
    to avoid repeating the pending issue already logged in
    `CORE_CONCEPTS.md`'s merge log (Batch 3) where the Research chapter
    forward-referenced a predicted `CH04_User_Interviews.md` filename. The
    merge step should update these `PART_OVERVIEW.md` links to direct file
    links once both chapters are confirmed drafted and their exact
    filenames are known.
  - If either "User Interviews" or "Journey Mapping" independently produced
    POV/HMW, laddering, root-cause, or problem-statement-canvas content at
    teaching depth, the merge step should arbitrate ownership using the
    "more foundational chapter" rule from Batch 2 — this chapter is the
    part's dedicated Define-stage chapter and is the natural default owner,
    but the review should verify no independent duplicate treatment exists
    before finalizing.
- No overlap expected with Part 01 (Architecture Mindset) concepts; this
  chapter's only cross-part references are recap links to Architecture
  Decision Records and Architecturally Significant Requirements, both
  already owned elsewhere and not re-claimed here.
- This chapter's own `PART_OVERVIEW.md` status table entry ("Problem
  Framing | Not Started") should be updated to "Drafted" as part of the
  batch reconciliation step — this session did not edit `PART_OVERVIEW.md`
  or `BOOK_PLAN.md` per its file-boundary instructions.
