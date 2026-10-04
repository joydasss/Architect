---
description: "Build a comprehensive, bounded topic map for a chapter, checking scope and concept ownership before drafting."
agent: "agent"
tools: [read, search]
argument-hint: "Chapter name and its part folder, e.g. HTTP in 05_Networking_and_OS"
---
Create a comprehensive, topic-first map for the chapter "${input:chapter}"
(part folder: `${input:partFolder}`). Organize it around the subject's central
questions; do not use a fixed section count, heading list, or chapter template.

1. Read [STYLE_GUIDE.md](../../STYLE_GUIDE.md) for depth, scope, and ownership
   requirements. Chapter structure is flexible.
2. Read [CORE_CONCEPTS.md](../../CORE_CONCEPTS.md). For every concept this
   chapter is likely to touch, note whether it's already owned by another
   chapter. Mark those as "recap only (see <owning chapter>)" in the outline
   instead of planning a full explanation.
3. Read [BOOK_PLAN.md](../../BOOK_PLAN.md) and the relevant `PART_OVERVIEW.md`
   to confirm this chapter's scope doesn't duplicate a sibling chapter/topic.
4. Decompose each major topic into concrete subtopics, mechanisms, variants,
   decision criteria, trade-offs, failure modes, operational concerns, and
   examples as appropriate to its importance and complexity. Identify relevant
   stakeholders, requirements, constraints, assumptions, and quality-attribute
   scenarios with observable outcomes. Be comprehensive within scope without
   adding tangents or duplicating owned material.
5. Identify recap-and-link boundaries, likely diagrams/data/code examples,
   provider or domain distinctions, and explicit exclusions. Flag ownership
   conflicts rather than silently duplicating content. Ensure the map explains
   what the reader must understand, decide, or be able to do for each major
   topic, not only its label.
   Identify at least five distinct diagram or visual-model opportunities,
   state what each explains, and place it near the topic it supports. Vary the
   visual form; do not default to five flowcharts.
6. Save or update this chapter's entry in `${input:partFolder}/TOPIC_MAP.md`.
   Preserve existing sibling entries. This map is a coverage contract, not a
   required one-topic-per-prose-section layout.

Do not draft the chapter itself. The author may combine, reorder, or split
mapped topics when that improves the explanation, but must account for each
mapped topic or explain a deliberate deferral.
