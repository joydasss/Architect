# Concept Proposals — Research chapter

Staged for merge into [CORE_CONCEPTS.md](../../CORE_CONCEPTS.md). Do not edit
CORE_CONCEPTS.md directly from this chapter's session.

| Concept | Proposed Owner | Scope note |
|---|---|---|
| Generative vs. evaluative research | Research chapter | The primary taxonomy axis: research run before a solution exists (understanding the problem) vs. against an existing artifact (measuring whether a solution works) |
| Qualitative vs. quantitative research (+ attitudinal/behavioral axis) | Research chapter | The data-shape taxonomy and the combined attitudinal/behavioral × qualitative/quantitative methods-landscape grid (NN/g framing) used to place any specific method |
| Research synthesis technique (affinity diagramming, thematic analysis, open/axial/selective coding) | Research chapter | How raw qualitative data becomes a defensible finding; observation-vs-interpretation discipline |
| Sample size and saturation heuristics (qualitative "5±2"/saturation vs. quantitative statistical power) | Research chapter | When a study has "enough" participants, and the distinction between the two very different underlying justifications |
| Research bias taxonomy (confirmation bias, leading questions, social desirability bias, say-do gap, sampling bias, recency/primacy effects) applied to user research | Research chapter | Names the systematic distortions research methodology designs around; triangulation as the general countermeasure |
| ResearchOps / research repository pattern / hub-and-spoke research team topology | Research chapter | Operational scaling model for research capability inside a growing product organization; the research-specific analogue of an architecture team topology, not a duplicate of it |
| Research plan artifact (research questions, method + rationale, recruitment/screener, sample-size justification, instrument outline, analysis plan) | Research chapter | The standard planning document that should exist before recruiting begins for any study |

## Notes for the merge step

- No overlap detected with existing entries in `CORE_CONCEPTS.md` (all
  currently Architecture Mindset / HTTP / REST concepts) — this chapter
  introduces a disjoint, design-and-research-specific concept set.
- This chapter deliberately did **not** claim ownership of interview
  technique (question wording, moderation, rapport-building) — that is
  explicitly deferred to a forthcoming `CH04_User_Interviews.md` chapter in
  this same part folder, which was not visible to this session and may not
  exist yet. If that chapter, once drafted, claims a different scope than
  assumed here (pure one-on-one interview mechanics), the batch review
  should reconcile the boundary rather than this chapter re-claiming it.
- This chapter also deliberately did **not** claim persona construction —
  deferred to a sibling `CH03_Personas.md` chapter in this same batch, not
  visible to this session. If Personas independently covers research
  planning/synthesis at similar depth, the batch review should arbitrate;
  this chapter's proposals above should take precedence as the more
  foundational/upstream treatment (Personas consumes synthesized research
  as an input, per the Concept Ownership Rule's "foundational chapters own
  concepts they introduce first" guidance).
- This chapter mentions but does **not** claim the Double Diamond / Design
  Thinking process framework (Discover-Define-Develop-Deliver) — that may
  already be introduced by `CH01_Empathy.md` as the first chapter in this
  part, or may need its own future home; flagging for the batch review to
  check rather than this chapter asserting ownership speculatively.
- This chapter forward-references a not-yet-drafted Experimentation/A-B
  Testing chapter (Product Management subsection, later in this same part)
  for statistical power/A-B testing mechanics, and links to `PART_OVERVIEW.md`
  rather than a specific chapter filename since that subsection's numbering
  is not yet finalized (per the disambiguation note on duplicate "Personas"/
  "Journey Mapping" titles across the two subsections).
- Assumed sibling filenames used in links: `CH01_Empathy.md`,
  `CH03_Personas.md`, `CH04_User_Interviews.md` — none were visible to this
  session (only `PART_OVERVIEW.md` exists in this part folder at drafting
  time). These follow the `CHxx_Title.md` convention and the chapter
  ordering given in `PART_OVERVIEW.md`'s Design Thinking table; verify at
  merge time that the actual files landed at these paths and fix any
  dangling links if not.
