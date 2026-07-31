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

1. Teach every topic from first principles to expert level — never write a
   summary in place of an explanation.
2. Every chapter must be self-contained enough to read standalone, but must
   still respect the **concept ownership rule** below.
3. Never skip internal implementation details when discussing how something
   works.
4. When describing an architecture decision, always explain *why* it was
   chosen over the alternatives, not just what it is.
5. Target 25-50 pages per full chapter (topics: ~15 pages, subtopics: ~6 pages).
6. **Acronym rule**: expand every acronym/abbreviation in parentheses at first
   use in a chapter (e.g. "Content Delivery Network (CDN)"), and use the
   expanded form consistently thereafter in prose. This applies with no
   exceptions in High-Level Design (HLD) and Low-Level Design (LLD) sections.
7. **Core Concepts depth rule**: Section 4 must teach each concept in
   first-principles depth, not as pointers. For each major concept, include:
   definition, mechanism (how it works), decision implications (when/why to
   use it), common failure mode, and at least one concrete scenario. A
   concept is not fully taught until a reader unfamiliar with it could explain
   it back correctly, including edge cases and reasoning — bullet lists of
   labels or one-line mentions do not satisfy this rule.
8. **Diagram rule**: every chapter must include inline diagrams (Mermaid
   flowcharts/sequence/state diagrams, or ASCII diagrams for byte/packet-level
   detail) directly in the prose wherever a process, decision flow, state
   machine, pipeline, or structural relationship is being explained — not only
   as an external reference under `diagrams/`. Prose explains the reasoning;
   the diagram makes the shape of the process or structure visually scannable.
   As a floor, Section 4 (Core Concepts) and Section 5 (Internal Working)
   together must contain at least 2-3 inline diagrams for a full chapter (at
   least 1 for a subtopic-length chapter), placed next to the concept they
   illustrate, not batched at the end. Never let a diagram substitute for the
   explanation — always pair it with the text that teaches the *why*.
9. **Use diagrams/flowcharts wherever possible and applicable** — this applies
   to every section, not only Section 4/5. If a comparison table, a sequence
   of steps, an org structure, a trade-off, or a lifecycle can be shown
   visually, add a diagram in addition to the prose rather than leaving it as
   text-only, throughout Sections 1-27.
10. **PDF landscape diagrams**: when a diagram is wide, deeply nested, or has
    many parallel lanes (for example, a service blueprint, a multi-swimlane
    journey map, or a large org chart) such that portrait orientation would
    compress or truncate it, mark it for full-page landscape rendering in the
    PDF build using the raw-LaTeX landscape wrapper (see "PDF landscape
    diagrams" under Diagrams below) rather than shrinking the diagram to fit.
11. **Explain, don't point**: every concept, pattern, or decision must be
    explained clearly and elaboratively — definition, mechanism, reasoning,
    and a concrete example — never reduced to a one-line mention, a bare
    bullet label, or "see X for details" when X doesn't actually exist yet or
    when the concept is this chapter's own to teach. Recap+link is only for
    concepts genuinely owned by another chapter per the Concept Ownership
    Rule below; everything this chapter owns must be taught in full.

## Section 4 quality bar

Section 4 (Core Concepts) is the conceptual backbone of the chapter. Treat it
as teachable theory plus applied reasoning, not a glossary.

- Explain cause-and-effect, not just labels.
- Distinguish adjacent concepts explicitly (for example, strategy vs artifact,
  structure vs process, visual fidelity vs behavioral fidelity).
- Include operational heuristics or checks a practitioner can apply.
- Keep concept-ownership boundaries: if another chapter owns a concept,
  recap in 2-3 sentences and link; do not duplicate full teaching.
- Where a concept has a decision flow, lifecycle, taxonomy branching, or
  multi-step mechanism, include an inline Mermaid diagram immediately after
  (or interleaved with) the prose that explains it — see the Diagram rule
  above. A concept described only as prose bullets when it has an obvious
  flow/structure shape (for example, a ladder, a state machine, a decision
  tree) has not met the quality bar.

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

## Standard chapter template (27 sections)

Every chapter must include, in this order:

1. Introduction
2. Historical Evolution
3. Why It Exists
4. Core Concepts
5. Internal Working
6. Design Principles
7. Architecture Patterns
8. Production Architecture
9. Implementation
10. Complete Code Examples
11. Performance
12. Scalability
13. Security
14. Observability
15. Failure Scenarios
16. Testing
17. Common Mistakes
18. Best Practices
19. Anti-Patterns
20. Trade-off Analysis
21. Comparison Table
22. Real-World Case Study
23. Interview Questions
24. Hands-on Exercises
25. Design Exercises
26. Architecture Review Questions
27. Summary

## Coverage

- **Languages/frameworks**: Java 21, Spring Boot, Python, FastAPI, Node.js,
  NestJS, Angular, React, Next.js — include examples in the languages relevant
  to the chapter's topic, not all of them in every chapter.
- **Clouds**: AWS, Azure, and GCP — note provider-specific implications where
  they materially differ; don't pad with trivial "X exists in all three" filler.
- **Diagrams**: use Mermaid for anything sequence/flow/architecture-shaped, and
  ASCII diagrams for packet/byte-level detail. Per the Diagram rule above,
  diagrams that illustrate a Section 4/5 concept must be embedded inline as a
  fenced Mermaid (or ASCII) block at the point of explanation, not just
  referenced. Reserve `diagrams/<type>/` files for larger, reusable, or
  workshop-scale assets (e.g. a full org chart, a multi-page journey map) that
  don't fit as an inline block — link to those rather than duplicating them.

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

This renders normally (ignored) in Markdown/EPUB and rotates only that page in
the PDF build, which includes the `pdflscape` LaTeX package for this purpose
(see `scripts/build-book.ps1`). Use this sparingly — only for diagrams that
genuinely need the extra width, not as a default for every diagram.
- **Code**: runnable samples live under `code/<language>/`; chapters reference
  them by relative link rather than embedding large listings inline.

## Ending elements (every chapter)

- Interview questions
- Hands-on lab
- Design review checklist
- Trade-off matrix
- Further reading (cross-references to related chapters)
