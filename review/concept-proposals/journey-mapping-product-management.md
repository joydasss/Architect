# Concept Proposals — Journey Mapping (Product Management) chapter

Staged for merge into [CORE_CONCEPTS.md](../../CORE_CONCEPTS.md). Do not edit
CORE_CONCEPTS.md directly from this chapter's session.

| Concept | Proposed Owner | Scope note |
|---|---|---|
| Customer lifecycle funnel (Acquisition -> Activation -> Retention -> Expansion -> Churn/Win-back as a commercial-relationship stage model, distinct from a single end-to-end experience journey) | Journey Mapping (Product Management) chapter | Full teaching (Sections 4.2-4.3): stage definitions, the AARRR/subscription-economy lineage, and the explicit distinction from both the Design Thinking experience journey (CH05) and a generic funnel chart |
| Lifecycle-stage-to-business-metric / revenue-event mapping (entry signal, primary metric, revenue event, and owner attached per stage) | Journey Mapping (Product Management) chapter | Full teaching (Section 4.4), including the "vanity-metric mapping" failure mode of reading one stage's metric without checking the adjacent stage it feeds |
| Stage-drop diagnostic (converting stage-to-stage conversion/retention drops into projected, segment-cross-checked revenue-at-stake figures as a roadmap-sequencing input) | Journey Mapping (Product Management) chapter | Full teaching (Section 4.5) of this one new input; explicitly does not re-teach Product Strategy's Three Horizons model or its fit/timing/capability/opportunity-cost test (CH15 4.6), and explicitly does not re-teach Market Analysis's segmentation methods (CH16 4.3), only consumes an existing segment as a targeting lens |
| Journey-stage health / leading-indicator dashboard (pairing a leading and a lagging indicator per lifecycle stage, with a named owner and alert threshold) | Journey Mapping (Product Management) chapter | Full teaching (Section 4.6), including the "lagging-only dashboard" failure mode |

## Notes for the merge step

- **Explicit scope boundary honored**: this chapter did not re-derive
  swimlane construction, the emotional curve / peak-end rule, current-state
  vs. future-state sequencing, or the frontstage/backstage distinction — all
  confirmed already owned by
  [Journey Mapping](../../02_Design_Thinking_and_Product_Management/CH05_Journey_Mapping.md).
  Every reference to that artifact is a recap + link, not a re-teaching.
  Section 4.3 explicitly reconciles this chapter's necessarily
  funnel-shaped artifact with CH05's own "don't confuse a journey map with
  a funnel chart" anti-pattern, to prevent a future reader (or merge
  reviewer) from flagging a false conflict between the two chapters.
- **Service Design not re-taught**: this chapter names
  [Service Design](../../02_Design_Thinking_and_Product_Management/CH12_Service_Design.md)
  only at the point where a lifecycle stage touches a backstage handoff,
  without re-deriving service-blueprint or line-of-visibility technique.
- **Portfolio sequencing not re-taught**: Section 4.5 adds exactly one new,
  quantified input (a stage, a projected revenue-at-stake figure, and an
  affected segment) to
  [Product Strategy](../../02_Design_Thinking_and_Product_Management/CH15_Product_Strategy.md#46-portfolio-sequencing-logic-why-this-bet-over-that-one)'s
  existing strategic-fit question, and does not restate the Three Horizons
  model or the fit/timing/capability/opportunity-cost test itself.
- **Market segmentation not re-taught**: Section 4.5 uses an existing
  segment (from
  [Market Analysis](../../02_Design_Thinking_and_Product_Management/CH16_Market_Analysis.md#43-market-segmentation-methods))
  as a targeting lens for a stage fix, without teaching segmentation
  methodology itself.
- **Complementary, not competing, with persona-weighted scoring**: this
  chapter's stage-drop diagnostic and
  [Personas (Product Management)](../../02_Design_Thinking_and_Product_Management/CH18_Personas_Product_Management.md#43-persona-weighted-opportunity-scoring)'s
  persona-weighted opportunity score are explicitly framed (Sections 4.5,
  5, 21) as two separate sequencing inputs meant to be read together for
  the same candidate bet, not alternative or overlapping techniques. No
  concept from that chapter is re-taught here.
- **Forward-named, not-yet-drafted chapters this chapter deliberately did
  not teach**: Story Mapping, Roadmaps, Backlog, Metrics, North Star
  Metrics, and Prioritization (RICE/MoSCoW/Kano) are all named at the
  point where this chapter's scope stops (Sections 1, 4.5, 10, 14, 21, 27)
  and linked via `PART_OVERVIEW.md` rather than a guessed filename, per
  this part's established convention.
- **No visibility into parallel sessions**: this chapter did not assume the
  content of Story Mapping (CH20) or Roadmaps (CH21), which may or may not
  exist yet from a parallel authoring session. If either chapter
  independently defines a stage-to-backlog translation mechanism or a
  revenue-event schema, the merge step should check for overlap with this
  chapter's Sections 4.4-4.5 (which stop at naming a stage and a projected
  revenue figure, not at producing a backlog item) before finalizing.
- **This chapter's own `PART_OVERVIEW.md` status table entry ("Journey
  Mapping | Not Started")** should be updated to "Drafted" as part of the
  batch reconciliation step — this session did not edit `PART_OVERVIEW.md`,
  `BOOK_PLAN.md`, or `CORE_CONCEPTS.md` per its file-boundary instructions.
- No other new concepts introduced beyond those listed above.
