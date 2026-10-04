# Chapter Prompt

Use once per chapter. This is the template wrapped by
`.github/prompts/plan-chapter.prompt.md` and the `chapter-author` agent.

```text
Write a substantive, self-contained chapter on <Chapter Topic> for Solution
Architects, using the approved chapter entry in the part's `TOPIC_MAP.md` as
the scope and depth contract. Follow `STYLE_GUIDE.md`; organize the chapter
around the reader's learning journey. There is no mandatory section count or
heading order.

Teach each central topic from its model and mechanisms through decisions,
alternatives, consequences, operational and failure behavior, and concrete
application. Treat supporting topics proportionately. Cover beginner through
expert needs where relevant, including implementation, performance, security,
testing, production scenarios, and trade-offs. Include code, comparisons,
exercises, and checklists when they improve the reader's ability to apply the
material; do not add filler to satisfy a section or page count. The finished
chapter needs at least five distinct, substantive diagrams or visual models
placed near the concepts they explain.

Before writing, check CORE_CONCEPTS.md. If a concept used in this chapter is
already owned by another chapter, write a 2-3 sentence recap and link to it
instead of re-teaching it in full. If this chapter introduces a new
cross-cutting concept, note it at the end for a proposal entry in
review/concept-proposals/<chapter-id>.md instead of writing directly to
CORE_CONCEPTS.md.

Use Mermaid inline for useful architecture, sequence, lifecycle, and decision
views; use ASCII for byte- or packet-level detail. Link runnable examples under
`code/<language>/` rather than embedding large listings. Page ranges in the
style guide are planning signals, not quotas.
```
