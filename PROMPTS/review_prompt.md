# Review Prompt

Use after a chapter or batch of chapters is drafted and concept proposals are
staged. This is the depth-review step before editing; run it again on material
changes before marking a chapter `Edited`.

```text
Review <chapter file(s)> against `STYLE_GUIDE.md`, the approved entry in the
part's `TOPIC_MAP.md`, `CORE_CONCEPTS.md`, and relevant sibling chapters.

1. **Accuracy:** Flag incorrect, outdated, or unsupported claims. Mark
   version-sensitive product details that need current authoritative-source
   verification.
2. **Scope and depth:** Confirm stakeholder concerns and mapped topics are
   substantively addressed. For central topics, check models, mechanisms,
   alternatives, consequences, failure and operational behavior, and concrete
   application. Flag material gaps; do not ask for padding or a target page
   count.
3. **Diagrams:** Confirm at least five distinct, substantive diagrams or
   visual models, placed near and explained with their topics. Do not count
   tables, code blocks, or cosmetic variants.
4. **Ownership and overlap:** Compare against `CORE_CONCEPTS.md` and sibling
   chapters. Flag full re-explanations of owned concepts; recommend a concise
   recap and link instead.
5. **Cross-references and consistency:** Confirm local links resolve and
   terminology follows the style guide and sibling chapters.

Output specific section-level findings tagged `[accuracy]`, `[scope-depth]`,
`[diagram]`, `[overlap]`, `[cross-reference]`, or `[consistency]`. Save findings
to `review/<chapter-id-or-batch-name>-review.md`. Do not edit the chapters in
the review step; the editor applies findings, then the reviewer checks material
revisions before status advances to `Edited`.
```
