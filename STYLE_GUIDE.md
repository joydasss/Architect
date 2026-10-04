# Style Guide

Single source of truth for every chapter in the Modern Solution Architecture
Handbook. Every prompt file and the `chapter-author` agent must point back to
this file. If a rule here conflicts with a one-off instruction given elsewhere,
this file wins.

## Audience

Senior Software Engineers, Staff Engineers, Tech Leads, Architects, Enterprise
Architects, and Engineering Managers with roughly 5-15 years of experience
transitioning into Solution Architecture. Write at graduate-textbook depth, not
blog-post depth.

## Core writing rules

1. Teach every in-scope topic to the depth its importance and complexity
  warrant. Do not substitute a summary for the explanation needed to
  understand and apply a central topic.
2. Every chapter must be self-contained enough to read standalone, but must
   still respect the **concept ownership rule** below.
3. Never skip internal implementation details when discussing how something
   works.
4. When describing an architecture decision, always explain *why* it was
   chosen over the alternatives, not just what it is.
5. Let chapter length follow its scope and topic map. Page counts are planning
  estimates, not quotas; do not add shallow material to reach a target. As a
  working expectation, a full chapter commonly needs 25-50 finished pages, a
  substantial topic about 15 pages, and a bounded subtopic about 6 pages.
  These are signals for planning and review, not pass/fail thresholds; if a
  broad map yields a much shorter draft, verify that it teaches rather than
  merely lists its topics.
6. **Acronym rule**: expand every acronym/abbreviation in parentheses at first
   use in a chapter (e.g. "Content Delivery Network (CDN)"), and use the
   expanded form consistently thereafter in prose. This applies with no
   exceptions in High-Level Design (HLD) and Low-Level Design (LLD) sections.
7. **Core-concept depth rule**: Teach central concepts in first-principles
  depth, not as pointers. For each major concept, cover the definition,
  mechanism, decision implications, failure modes, and concrete scenarios
  appropriate to that concept. A reader should be able to explain and apply
  the chapter's central ideas, including important edge cases and reasoning;
  labels or one-line mentions are not enough.
8. **Diagram rule**: every chapter must include at least five substantive,
  distinct diagrams or visual models. Choose forms that fit the subject:
  architecture/context or deployment views, network/data-flow diagrams,
  sequences, state machines, decision trees, timelines, failure-domain maps,
  trust-boundary diagrams, or ASCII for byte/packet-level detail. Use Mermaid
  where appropriate, but do not force every visual into a flowchart. Each
  diagram must explain a different useful relationship or mechanism, appear
  near its discussion, and receive enough prose to explain its implications.
  Tables, code blocks, and cosmetic variations do not count toward the five.
  Never use a diagram as a substitute for reasoning.
9. **Use diagrams/flowcharts wherever possible and applicable** — this applies
  throughout the chapter. Use a visual when it materially improves the
  reader's understanding of a comparison, sequence, organization, trade-off,
  or lifecycle. The five-diagram minimum is a floor, not a target to stop at;
  do not pad it with duplicates. When a topic is abstract, use complementary
  views such as context, relationship, decision, and failure models.
10. **PDF landscape diagrams**: when a diagram is wide, deeply nested, or has
    many parallel lanes (for example, a service blueprint, a multi-swimlane
    journey map, or a large org chart) such that portrait orientation would
    compress or truncate it, mark it for full-page landscape rendering in the
    PDF build using the raw-LaTeX landscape wrapper (see "PDF landscape
    diagrams" under Diagrams below) rather than shrinking the diagram to fit.
11. **Explain, don't point**: every central, chapter-owned concept, pattern,
  or decision must be explained with the definition, mechanism, reasoning,
  and examples its depth warrants. Do not reduce important material to a
  label or use a dead-end "see X for details" reference. Recap+link is for
  concepts genuinely owned by another chapter; supporting topics may be
  concise when they are clear and useful.

## Topic maps and chapter structure

Before drafting, create or review the chapter's entry in the part's
`TOPIC_MAP.md`, grounded in the chapter scope, part overview, and
`CORE_CONCEPTS.md`. State the intended reader outcome, boundaries, and central
questions. Decompose major topics into concrete subtopics, mechanisms, and
questions a reader needs answered. Be comprehensive within that scope: “all
possible topics” means the meaningful coverage required to fulfill the
chapter's purpose, not unbounded tangents or repetition of another chapter's
material.

Each chapter map must make its coverage inspectable. Include the chapter's
reader outcome and scope; relevant stakeholder concerns, requirements,
constraints, and assumptions; the major topics and their important subtopics;
prerequisites and ownership links; and explicit exclusions or deferrals.
For architecture-decision chapters, include the consequential alternatives,
quality-attribute scenarios, risks, and evidence the reader needs to compare
options. A map that lists labels without saying what the reader must
understand, decide, or be able to do is not ready for drafting. Identify at
least five distinct diagram opportunities in the map, naming what each visual
explains and where it belongs. Select different useful views rather than five
copies of the same flow. The author may refine the set while drafting, but the
finished chapter must retain at least five substantive diagrams or visual
models.

For each major topic, identify the explanation its depth warrants: foundational
model, cause and effect, internal mechanism, variants, decision criteria,
trade-offs, operational concerns, failure modes, edge cases, and examples.
These are depth lenses, not a requirement to force every item into every topic.
Give central or difficult topics more space; treat supporting topics
concisely without reducing them to unexplained labels.

**Do not confuse flexible structure with compressed coverage.** A topic map is
not an outline to summarize in one paragraph per bullet. Each central topic
must become a teachable explanation: establish the model, show how it works,
reason through important choices and alternatives, and make consequences
concrete with worked examples, scenarios, or evidence. Develop significant
mechanisms and trade-offs far enough that a reader can apply them, including
important operational and failure behavior. Tables and diagrams support this
explanation; they do not replace it. A chapter is not complete merely because
every map item receives a mention.

Use two practical depth levels without turning them into a heading template:

- **Central topics** are explained so the reader can reason about and apply
  them. Cover the governing model, important mechanisms or interactions,
  alternatives and decision criteria, consequences and trade-offs, and
  relevant operational, failure, security, or performance behavior. Work at
  least one representative scenario far enough to show how the reasoning is
  used. Split the treatment into multiple sections when the topic has distinct
  mechanisms or decisions; do not compress a broad central topic into a single
  overview paragraph.
- **Supporting topics** receive enough context to understand their role and
  relationship to the chapter's decisions. Explain them more fully when they
  create a material constraint or risk; otherwise use a concise treatment and
  link to the owning chapter where appropriate.

The number of mapped topics and their complexity should be visible in the
resulting chapter's substantive development. Page ranges are a diagnostic
signal, not a target to pad toward: a broad map in a very short chapter should
trigger a coverage review, while a tightly bounded topic need not be expanded
with unrelated material.

There is no mandatory section count, heading list, or section order. Organize
the chapter around its subject and reader journey. Combine related topics,
split complex topics where useful, and omit headings that would add no
substantive content. Historical context, implementation, comparisons, case
studies, exercises, and review checklists are optional forms: include them
when they advance the chapter's goals, not to satisfy a template.

Use relevant coverage lenses when they materially serve the subject, such as
concepts, architecture, implementation, performance, scalability, security,
operations, observability, failure, testing, trade-offs, or practice. Review
completeness against the approved topic map and ownership boundaries, never by
counting sections, diagrams, pages, or code examples alone. Account for every
mapped topic in the chapter or document a clear reason for deferring or
excluding it. When a broad chapter is substantially shorter than its planning
estimate or comparable full-depth chapters, the author, reviewer, and editor must
explicitly check for underdeveloped topics rather than assuming brevity is a
virtue.

Within each topic, explain cause and effect, distinguish adjacent concepts,
and give the reader practical decision heuristics where appropriate. Keep
concept-ownership boundaries: recap and link to concepts owned elsewhere
instead of duplicating their full treatment. Where a topic has a meaningful
flow, lifecycle, taxonomy, or multi-step mechanism, include a diagram near the
explanation when it improves understanding.

For architecture decisions, connect requirements to the design rather than
presenting a catalog of practices. Where relevant, make stakeholder concerns,
constraints, assumptions, quality-attribute scenarios, candidate views,
decisions and rationale, alternatives, risks, and validation evidence
traceable through the chapter. Use concrete stimuli and outcomes for important
quality scenarios (for example, a failure or load condition, the expected
system response, and a measurable success criterion). These are architecture
reasoning tools, not mandatory standalone headings; select those that serve
the chapter's subject and reader outcome.

### Alignment with architecture practice

This guide follows the intent of established architecture-description and
workload-review practice without claiming that those frameworks prescribe a
textbook chapter format. ISO/IEC/IEEE 42010:2022 specifies requirements for
architecture descriptions, frameworks, viewpoints, and model kinds; it does
not prescribe a creation process or a recording format. The arc42 template
emphasizes goals, stakeholders, constraints, quality goals, decisions,
cross-cutting concepts, and risks while allowing sections to be adapted to the
system. AWS and Azure Well-Architected guidance emphasizes workload context,
trade-offs, risks, review, and iterative improvement. Apply their relevant
reasoning practices, but keep provider-specific frameworks in their assigned
chapters.

References: [ISO/IEC/IEEE 42010:2022](https://www.iso.org/standard/74393.html),
[arc42 Introduction and Goals](https://docs.arc42.org/section-1/),
[arc42 Quality Requirements](https://docs.arc42.org/section-10/),
[AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html),
and [Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/what-is-well-architected-framework).

## Concept ownership rule (anti-repetition)

Chapters are frequently drafted in isolated, parallel agent sessions that
cannot see each other's output. To avoid the same concept (e.g. CAP theorem,
OAuth 2.0, TLS handshake, idempotency) being fully re-explained in every
chapter that touches it:

- [CORE_CONCEPTS.md](CORE_CONCEPTS.md) is the registry of which chapter *owns*
  the full explanation of each cross-cutting concept.
- Before drafting, check `CORE_CONCEPTS.md`. If a concept is already owned by
  another chapter, do **not** re-teach it. Instead write a 2-3 sentence recap
  and link to the owning chapter, e.g.:
  > HTTP status codes (see [HTTP](../05_Networking_and_OS/CH01_HTTP.md#status-codes))
  > communicate the outcome of a request; REST APIs rely on them to signal
  > success, client error, and server error without inventing a parallel scheme.
- If a chapter introduces a new cross-cutting concept, propose it in
  `review/concept-proposals/<chapter-id>.md` rather than writing directly to
  `CORE_CONCEPTS.md` — a separate merge step reconciles proposals from
  multiple chapters drafted in parallel, avoiding concurrent-write conflicts.
- Foundational/lower-level chapters generally own the concepts they introduce
  first (e.g. the Networking/HTTP chapter owns HTTP status codes and caching
  headers; the API/REST chapter owns REST-specific concepts like HATEOAS).

The former 27-section list is retired as a mandatory template. Its headings
remain optional prompts when useful, but authors must not create empty or
shallow sections just to preserve that sequence. The same rule applies to
page, diagram, code-example, exercise, and end-matter counts: include each
only when it contributes to the chapter's learning goals.

## Coverage

- **Languages/frameworks**: Java 21, Spring Boot, Python, FastAPI, Node.js,
  NestJS, Angular, React, Next.js — include examples in the languages relevant
  to the chapter's topic, not all of them in every chapter.
- **Clouds**: AWS, Azure, and GCP — note provider-specific implications where
  they materially differ; don't pad with trivial "X exists in all three" filler.
- **Diagrams**: use Mermaid for sequence/flow/architecture shapes and ASCII
  diagrams for packet/byte-level detail when the visual adds clarity. Embed
  useful diagrams inline at the point of explanation. Reserve
  `diagrams/<type>/` files for larger, reusable, or workshop-scale assets
  that do not fit inline; link to those rather than duplicating them.

### PDF landscape diagrams

When a diagram is too wide/dense for a portrait page (e.g. many parallel
swimlanes, a wide sequence diagram, a large org chart), wrap it with the
raw-LaTeX `landscape` environment so the PDF build rotates just that page
instead of shrinking the diagram to illegibility:

````markdown
```{=latex}
\begin{landscape}
```

```mermaid
flowchart LR
    A[...] --> B[...] --> C[...]
```

```{=latex}
\end{landscape}
```
````

### Mermaid rendering in the PDF build

Authors always write plain ```` ```mermaid ```` fenced code blocks in the
Markdown source — never embed pre-rendered images for diagrams that are
naturally Mermaid-shaped. The PDF build (`scripts/build-book.ps1`) runs
Pandoc with the `mermaid-filter` filter (installed via `npm install` at the
repo root, see `package.json`), which converts every Mermaid code block into
a rendered image before layout, so diagrams appear as real graphics in the
PDF rather than as literal code text. Markdown/EPUB readers that render
Mermaid natively (e.g. GitHub, most EPUB readers) are unaffected — the source
stays the same either way. If `mermaid-filter` isn't installed, the build
still runs (non-fatal) but Mermaid blocks fall back to plain code text in the
PDF, so always run `npm install` once before a PDF build.

This renders normally (ignored) in Markdown/EPUB and rotates only that page in
the PDF build, which includes the `pdflscape` LaTeX package for this purpose
(see `scripts/build-book.ps1`). Use this sparingly — only for diagrams that
genuinely need the extra width, not as a default for every diagram.

- **Code**: runnable samples live under `code/<language>/`; chapters reference
  them by relative link rather than embedding large listings inline.

## Optional supporting elements

Interview questions, hands-on labs, design-review checklists, trade-off
matrices, and further reading can be useful when they support the chapter's
reader outcome. They are not required in every chapter; select and shape them
to fit the subject.
