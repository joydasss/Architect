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
  ASCII diagrams for packet/byte-level detail. Diagram sources live under
  `diagrams/<type>/` and are referenced (not duplicated) from chapters.
- **Code**: runnable samples live under `code/<language>/`; chapters reference
  them by relative link rather than embedding large listings inline.

## Ending elements (every chapter)

- Interview questions
- Hands-on lab
- Design review checklist
- Trade-off matrix
- Further reading (cross-references to related chapters)
