# Concept Proposals — Personas (Product Management) chapter

Staged for merge into [CORE_CONCEPTS.md](../../CORE_CONCEPTS.md). Do not edit
CORE_CONCEPTS.md directly from this chapter's session.

| Concept | Proposed Owner | Scope note |
|---|---|---|
| Persona-weighted opportunity scoring (base prioritization score x persona value weight, maximum vs. reach-adjusted-blend conventions) | Personas (Product Management) chapter | Full teaching (Section 4.3): the multiplication formula, the multi-persona weighting convention trade-off, and the "reach-only weighting silently reintroduces majority-rule bias" failure mode. Deliberately does not teach base scoring-framework mechanics (RICE/MoSCoW/Kano), which stay with the not-yet-drafted Prioritization chapter |
| Persona-to-segment-value alignment (mapping a behavioral persona to its segment's revenue/strategic-account/growth value as a separate, explicitly linked layer) | Personas (Product Management) chapter | Full teaching (Section 4.4). Explicitly keeps revenue/segment data out of the persona artifact itself (CH03's boundary); does not teach market segmentation technique, which belongs to the not-yet-drafted Market Analysis chapter |
| Persona-based stakeholder arbitration protocol (name-the-persona -> check-ranking -> compare-weighted-score -> escalate-to-council sequence for resolving conflicting internal stakeholder requests) | Personas (Product Management) chapter | Full teaching (Section 4.5). Reuses, but does not redefine, CH03's primary/secondary/supplemental/negative ranking as one input step |
| Persona council (standing, product-owned, cross-functional governance body that arbitrates contested prioritization disputes and periodically reviews the value-weighting model) | Personas (Product Management) chapter | Full teaching (Section 4.6), including its explicit charter/scope distinction from (a) CH03's design/research persona-accuracy governance function and (b) Product Strategy's whole-bet strategy review forum |
| Persona weight as a portfolio-sequencing input (naming a served persona and its value weight inside a bet's strategic-fit rationale) | Personas (Product Management) chapter | Full teaching (Section 4.7) of this one narrow addition; explicitly does not re-teach Product Strategy's Three Horizons model or the fit/timing/capability/opportunity-cost test itself, which stay fully owned by Product Strategy |

## Notes for the merge step

- **Explicit scope boundary honored**: this chapter did not re-derive the
  persona definition, component checklist, taxonomy, construction pipeline,
  or governance lifecycle — all confirmed already owned by
  [Personas](../../02_Design_Thinking_and_Product_Management/CH03_Personas.md).
  Every reference to primary/secondary/supplemental/negative ranking,
  proto-persona vs. data-driven spectrum, staleness/zombie-persona framing,
  etc. is a recap + link, not a re-teaching.
- **JTBD not re-taught**: this chapter treats Jobs-to-be-Done strictly as a
  complementary input (recap only) and does not touch its mechanics, fully
  respecting [Product Strategy](../../02_Design_Thinking_and_Product_Management/CH15_Product_Strategy.md#45-jobs-to-be-done-jtbd)'s
  ownership.
- **Portfolio sequencing not re-taught**: Section 4.7 adds exactly one input
  (persona name + weight) to Product Strategy's existing strategic-fit
  question and does not restate the Three Horizons model or the
  fit/timing/capability/opportunity-cost test.
- **Forward-named, not-yet-drafted chapters this chapter deliberately did
  not teach**: Market Analysis (segmentation technique itself), Competitive
  Analysis, Roadmaps, Backlog, Prioritization (RICE/MoSCoW/Kano base scoring
  mechanics), Metrics, and North Star Metrics are all named at the point
  where this chapter's scope stops (Sections 1, 4.4, 10, 14, 21) and linked
  via `PART_OVERVIEW.md` rather than a guessed filename, per this part's
  established convention (see Product Strategy's own staging file).
- **No visibility into parallel sessions**: this chapter did not assume the
  content of Market Analysis (CH16) or Competitive Analysis (CH17), which
  may or may not exist yet from a parallel authoring session. If either
  chapter independently defines a market-segment-to-value technique or a
  persona-adjacent business artifact, the merge step should check for
  overlap with this chapter's Section 4.4 (which only consumes a segment's
  value as a given input, not derives it) before finalizing.
- **This chapter's own `PART_OVERVIEW.md` status table entry ("Personas |
  Not Started")** should be updated to "Drafted" as part of the batch
  reconciliation step — this session did not edit `PART_OVERVIEW.md`,
  `BOOK_PLAN.md`, or `CORE_CONCEPTS.md` per its file-boundary instructions.
- No other new concepts introduced beyond those listed above.
