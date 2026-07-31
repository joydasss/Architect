---
description: "Expand a chapter name into a detailed section outline, checking CORE_CONCEPTS.md for concepts owned elsewhere before scoping."
agent: "agent"
tools: [read, search]
argument-hint: "Chapter name and its part folder, e.g. HTTP in 05_Networking_and_OS"
---
Expand the chapter "${input:chapter}" (part folder: `${input:partFolder}`) into
a detailed section-by-section outline.

1. Read [STYLE_GUIDE.md](../../STYLE_GUIDE.md) for the mandatory 27-section
   chapter template.
2. Read [CORE_CONCEPTS.md](../../CORE_CONCEPTS.md). For every concept this
   chapter is likely to touch, note whether it's already owned by another
   chapter. Mark those as "recap only (see <owning chapter>)" in the outline
   instead of planning a full explanation.
3. Read [BOOK_PLAN.md](../../BOOK_PLAN.md) and the relevant `PART_OVERVIEW.md`
   to confirm this chapter's scope doesn't duplicate a sibling chapter/topic.
4. Produce an outline with one bullet per of the 27 template sections, noting
   for each: the specific subtopics to cover, any concepts to recap+link
   rather than re-teach, and which diagrams/code samples will be needed later.

Do not write the chapter itself — output only the outline.
