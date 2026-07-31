# Review Prompt

Use after a chapter (or a batch of chapters drafted together) to check
technical accuracy and — critically — overlap with other chapters.

```text
Review <chapter file(s)> for:

1. Technical accuracy — flag any incorrect or outdated claims.
2. Completeness — confirm all 27 STYLE_GUIDE.md sections are present.
3. Overlap check — compare this chapter against CORE_CONCEPTS.md and against
   any sibling chapters drafted in the same batch. Flag any section that
   fully re-explains a concept already owned elsewhere; it should instead be
   a 2-3 sentence recap + link.
4. Cross-references — confirm links to other chapters/concepts resolve to
   real files/anchors.
5. Consistency — terminology matches STYLE_GUIDE.md and other chapters.

Output a list of specific line/section-level findings, each tagged
[accuracy] / [completeness] / [overlap] / [cross-reference] / [consistency].
```
