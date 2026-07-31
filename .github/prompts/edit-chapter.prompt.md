---
description: "Apply reviewer findings to a chapter: polish language, fix cross-references, and convert any flagged duplicated explanations into a recap + link to the owning chapter."
agent: "agent"
tools: [read, edit, search]
argument-hint: "Chapter file path and its review findings file, e.g. 08_API_Architecture/CH01_REST.md review/http-rest-batch-review.md"
---
Edit the chapter at `${input:chapterFile}` using the findings in
`${input:reviewFile}`.

1. For every `[overlap]` finding, replace the flagged full explanation with a
   2-3 sentence recap and a relative Markdown link to the owning chapter
   (per [CORE_CONCEPTS.md](../../CORE_CONCEPTS.md)) — do not simply delete the
   content, since the chapter must still make sense standing alone.
2. For every `[cross-reference]` finding, fix the link/anchor.
3. For every `[accuracy]` / `[completeness]` / `[consistency]` finding, make
   the corresponding correction.
4. Polish language and flow without changing technical meaning.
5. Update the chapter's status to `Edited` in the relevant `PART_OVERVIEW.md`
   and in `BOOK_PLAN.md`.
