# Concept Proposals — Story Mapping (CH20)

Staging file for `review/concept-proposals/` per the Concept Ownership Rule
in [STYLE_GUIDE.md](../../STYLE_GUIDE.md). To be merged into
[CORE_CONCEPTS.md](../../CORE_CONCEPTS.md) by a separate batch-merge step —
not edited directly by this chapter's authoring session.

## Proposed new concepts (owned by this chapter)

| Concept | Proposed owning chapter | Notes |
|---|---|---|
| Story map (definition, anatomy: backbone, tasks, release lines) | [Story Mapping](../../02_Design_Thinking_and_Product_Management/CH20_Story_Mapping.md) | Full artifact/technique (Jeff Patton); Section 4.1 |
| Backbone / activities row (narrative spine) | [Story Mapping](../../02_Design_Thinking_and_Product_Management/CH20_Story_Mapping.md) | User-narrative-order discipline, distinct from build/system order; Section 4.2 |
| Walking skeleton (story-mapping application) | [Story Mapping](../../02_Design_Thinking_and_Product_Management/CH20_Story_Mapping.md) | "Minimum sufficient, not easiest" task per activity, forming the thinnest end-to-end release; Section 4.3. **Flag for merge review**: "walking skeleton" originates from Alistair Cockburn's Crystal methodologies / general software-delivery practice (also referenced in continuous-delivery and XP-adjacent literature). This chapter scopes the term narrowly to its story-mapping application only. If a future DevOps, Testing, or Software Engineering Foundations chapter teaches the general software-delivery meaning of "walking skeleton" (a thin, deployable, end-to-end system slice used to prove architecture/pipeline viability before feature-complete work), that chapter may be the more foundational owner for the general term — the merge step should decide whether to keep two scoped entries (general vs. story-mapping application) or consolidate under whichever chapter lands first. |
| Vertical slicing by release / release lines (Now/Next/Later) | [Story Mapping](../../02_Design_Thinking_and_Product_Management/CH20_Story_Mapping.md) | Horizontal cuts across the full backbone forming genuine end-to-end releases, vs. horizontal/architecture-layer cuts; Section 4.4 |
| Flat backlog failure mode | [Story Mapping](../../02_Design_Thinking_and_Product_Management/CH20_Story_Mapping.md) | Loss of narrative arc when a backlog is worked as a single priority-ranked column; detection and prevention; Section 4.5 |

## Distinctions drawn against existing owned concepts (no new ownership claimed)

These sections explicitly distinguish this chapter's scope from concepts
already owned elsewhere, and recap rather than re-teach them. Listed here
only for merge-step visibility, not as new registry entries:

- Story map backbone (build sequence, single release scope) vs. journey
  map timeline (full experience, any horizon) — recaps and links
  [Journey Mapping](../../02_Design_Thinking_and_Product_Management/CH05_Journey_Mapping.md),
  already owned there. Section 4.6.
- Story map release lines (within-release ordering) vs. roadmap
  (across-release/initiative sequencing) — recaps and links
  [Product Strategy](../../02_Design_Thinking_and_Product_Management/CH15_Product_Strategy.md#47-strategy-to-roadmap-translation-contract)'s
  strategy-to-roadmap translation contract, already owned there. Section 4.7.
  Names, but does not teach, this part's not-yet-drafted **Roadmaps**
  chapter (CH21) as the future owner of roadmap sequencing mechanics
  itself.
- Persona goal as backbone input — recaps and links
  [Personas](../../02_Design_Thinking_and_Product_Management/CH03_Personas.md),
  already owned there. Section 4.8.
- How-Might-We (HMW) statement / problem statement canvas as backbone
  scope input — recaps and links
  [Problem Framing](../../02_Design_Thinking_and_Product_Management/CH06_Problem_Framing.md),
  already owned there. Section 4.8.

## Forward references to not-yet-drafted sibling chapters

Named only for scope boundary, not taught — no ownership claimed, for the
merge step's awareness:

- **Roadmaps** (CH21) — initiative/release sequencing across a
  multi-quarter horizon.
- **Journey Mapping** (Product Management variant, CH19) — this chapter
  anchors its journey-map distinction entirely against the already-drafted
  Design Thinking [Journey Mapping](../../02_Design_Thinking_and_Product_Management/CH05_Journey_Mapping.md)
  chapter, not against the not-yet-drafted PM variant, per this chapter's
  instructions.
- **Backlog** — general backlog-management mechanics beyond the
  flat-backlog failure mode this chapter names.
- **MVP (Minimum Viable Product)** — named in Section 4.3 as an adjacent
  concept to the walking skeleton, not taught.
- **Metrics** / **North Star Metrics** — named in Sections 14 as the
  future owners of full metric-design technique.

## No conflicts detected from this session

This chapter's authoring session had no visibility into any other
in-progress chapter draft. All five proposed concepts above appear to be
genuinely new to this part's registry based on the current
[CORE_CONCEPTS.md](../../CORE_CONCEPTS.md) snapshot read at drafting time;
the walking-skeleton flag above is the only item this session recommends
extra scrutiny on during merge.
