# Concept Proposals — Empathy chapter

Staged for merge into [CORE_CONCEPTS.md](../../CORE_CONCEPTS.md). Do not edit
CORE_CONCEPTS.md directly from this chapter's session.

| Concept | Proposed Owner | Scope note |
|---|---|---|
| Design-thinking five-stage process (Empathize → Define → Ideate → Prototype → Test) | Empathy chapter | Overall framework shape, non-linear/iterative nature, and stage sequencing only — each stage's own reasoning technique is owned by that stage's own chapter (Problem Framing, Ideation, Rapid Prototyping/Wireframing, Usability Testing) once drafted |
| Human-Centered Design (HCD) / ISO 9241-210 | Empathy chapter | Definition and standards grounding, introduced here as the discipline the Empathize stage operationalizes |
| Empathy map (Says/Thinks/Does/Feels/Pains/Gains) | Empathy chapter | Full artifact definition, construction discipline, and synthesis workflow |
| Cognitive vs. affective vs. compassionate empathy (Goleman's distinction) | Empathy chapter | Psychological framing used to explain why understanding alone doesn't change decisions without action |
| Curse of knowledge (Heath & Heath) | Empathy chapter | Cognitive bias explaining why builders struggle to model novice users; introduced here as the "Why It Exists" driver |
| False-consensus effect | Empathy chapter | Cognitive bias explaining why teams overestimate how representative their own preferences are |
| Ladder of inference (Argyris) | Empathy chapter | Reasoning model used as the mechanism behind "suspend judgment before synthesizing" |
| Stakeholder empathy (beyond end users — operators, support, compliance, maintainers) | Empathy chapter | Extension of the empathy discipline to non-customer human audiences of a system |

## Notes for the merge step

- No overlap detected with existing `CORE_CONCEPTS.md` entries — this is the
  first chapter drafted in Part 02, and none of the existing entries (HTTP,
  REST, Part 01 Architecture Mindset concepts) touch design-thinking or
  product-management vocabulary.
- This chapter is the **first chapter of the Design Thinking subsection** in
  its part and deliberately claims ownership of the overarching five-stage
  design-thinking framework itself (not just the Empathize stage), on the
  reasoning that later stage-owning chapters (Problem Framing, Ideation,
  Rapid Prototyping, Wireframing, Usability Testing) should recap + link back
  here for the framework's overall shape rather than each re-introducing it.
  If the batch review finds another chapter in this part independently
  claimed the same framework-level ownership, arbitrate using the same
  "more foundational chapter" rule applied in Batch 2 of the merge log.
- Two sibling chapters in the same subsection — **Research** (CH02) and
  **Personas** (CH03) — were being drafted in parallel, isolated sessions and
  were not visible to this one. This chapter explicitly avoided re-teaching:
  - Specific user-research field methods (interviews, contextual inquiry,
    diary studies, surveys) — assumed to belong to Research.
  - Persona/archetype construction and packaging — assumed to belong to
    Personas.
  If either sibling chapter also produced empathy-map or design-thinking
  framework content at meaningful depth, the batch review should reconcile
  ownership rather than this chapter unilaterally assuming precedence.
- This chapter references a **Journey Mapping** chapter and a **Problem
  Framing** chapter, both listed as "not yet drafted" in this part's
  `PART_OVERVIEW.md` at the time of writing — links point to
  `PART_OVERVIEW.md` rather than a specific chapter file, since those files
  did not exist in this session. Update these forward-references once those
  chapters are drafted.
- Flagging for the merge step: this part's `PART_OVERVIEW.md` lists
  **"Personas"** and **"Journey Mapping"** as chapter titles in *both* the
  Design Thinking subsection and the later Product Management subsection
  (chapters ~14-31 in this same part). This chapter only reasoned about the
  Design Thinking-subsection versions (assumed filenames `CH03_Personas.md`
  and a later `CHxx_Journey_Mapping.md` within Design Thinking). The
  Product Management versions will need disambiguated filenames (e.g.
  `CH18_Personas_Product_Management.md`) — out of scope for this chapter,
  noted here only so the merge/reconciliation step is aware before those
  chapters are drafted.
