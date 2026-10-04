---
description: "Review drafted chapters for accuracy, topic-map coverage, appropriate depth, and overlap with the ownership registry or sibling chapters."
agent: "agent"
tools: [read, search]
argument-hint: "One or more chapter file paths drafted together, e.g. 05_Networking_and_OS/CH01_HTTP.md 08_API_Architecture/CH01_REST.md"
---
Review the chapter files at `${input:chapterFiles}`.

1. **Technical accuracy** — flag any incorrect, outdated, or unsupported claims.
2. **Scope and depth** — compare the chapter with its approved entry in the
   part's `TOPIC_MAP.md`. Confirm that stakeholder concerns, requirements,
   constraints, assumptions, and relevant quality scenarios inform the
   coverage; mapped topics are substantively covered; and depth matches
   importance and complexity. Do not treat a brief mention of every map item
   as coverage. For central topics, check the model, mechanisms, alternatives,
   consequences, operational/failure behavior, and concrete application.
   Flag material gaps, unsupported tangents, or topics silently deferred. If a
   broad chapter is substantially shorter than its planning signal or
   comparable full-depth chapters, investigate underdeveloped topics; do not
   recommend padding to meet a page count.
   Confirm that the chapter includes at least five distinct, substantive
   diagrams or visual models, placed near and explained with the relevant
   topics. Do not count tables, code blocks, or cosmetic variants.
3. **Overlap check (critical)** — compare each chapter against
   [CORE_CONCEPTS.md](../../CORE_CONCEPTS.md) and against every other chapter
   passed in this same review. Flag any section that fully re-explains a
   concept owned by another chapter; it should instead be a 2-3 sentence
   recap + link. This check matters most when chapters were authored in
   isolated/parallel sessions with no shared conversation.
4. **Cross-references** — confirm links to other chapters/concepts/diagrams/
   code samples resolve to real files and anchors.
5. **Consistency** — terminology matches STYLE_GUIDE.md and sibling chapters.

Output a findings list tagged `[accuracy]` / `[scope-depth]` / `[overlap]` /
`[cross-reference]` / `[consistency]`, each with the chapter, section, and a
one-line fix recommendation. Save the findings to
`review/<chapter-id-or-batch-name>-review.md`. Do not edit the chapters
directly — that's the Editor's job (`edit-chapter.prompt.md`).
