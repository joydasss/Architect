# Chapter Prompt

Use once per chapter. This is the template wrapped by
`.github/prompts/plan-chapter.prompt.md` and the `chapter-author` agent.

```text
Write a complete textbook chapter on <Chapter Topic> for Solution Architects,
following the 27-section template in STYLE_GUIDE.md exactly, in order.

Cover beginner through expert level. Include history, why it exists, core
concepts, internal implementation, architecture patterns, production
architecture, complete code examples (referencing code/<language>/ rather than
embedding large listings), performance, scalability, security, observability,
failure scenarios, testing, common mistakes, best practices, anti-patterns,
trade-off analysis, a comparison table, a real-world case study, interview
questions, hands-on exercises, design exercises, an architecture review
checklist, and a summary.

Before writing, check CORE_CONCEPTS.md. If a concept used in this chapter is
already owned by another chapter, write a 2-3 sentence recap and link to it
instead of re-teaching it in full. If this chapter introduces a new
cross-cutting concept, note it at the end for a proposal entry in
review/concept-proposals/<chapter-id>.md instead of writing directly to
CORE_CONCEPTS.md.

Include ASCII diagrams for byte/packet-level detail and note where Mermaid
diagrams should go (produced separately via diagram-chapter.prompt.md).

Target 25-50 pages.
```
