---
description: "Review one or more drafted chapters for technical accuracy, STYLE_GUIDE completeness, and — critically — overlap/duplication with CORE_CONCEPTS.md or sibling chapters drafted in the same batch."
agent: "agent"
tools: [read, search]
argument-hint: "One or more chapter file paths drafted together, e.g. 05_Networking_and_OS/CH01_HTTP.md 08_API_Architecture/CH01_REST.md"
---
Review the chapter(s) at `${input:chapterFiles}`.

1. **Technical accuracy** — flag any incorrect, outdated, or unsupported claims.
2. **Completeness** — confirm all 27 sections from
   [STYLE_GUIDE.md](../../STYLE_GUIDE.md) are present and non-trivial.
3. **Overlap check (critical)** — compare each chapter against
   [CORE_CONCEPTS.md](../../CORE_CONCEPTS.md) and against every other chapter
   passed in this same review. Flag any section that fully re-explains a
   concept owned by another chapter; it should instead be a 2-3 sentence
   recap + link. This check matters most when chapters were authored in
   isolated/parallel sessions with no shared conversation.
4. **Cross-references** — confirm links to other chapters/concepts/diagrams/
   code samples resolve to real files and anchors.
5. **Consistency** — terminology matches STYLE_GUIDE.md and sibling chapters.

Output a findings list tagged `[accuracy]` / `[completeness]` / `[overlap]` /
`[cross-reference]` / `[consistency]`, each with the chapter, section, and a
one-line fix recommendation. Save the findings to
`review/<chapter-id-or-batch-name>-review.md`. Do not edit the chapters
directly — that's the Editor's job (`edit-chapter.prompt.md`).
