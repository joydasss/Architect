# Part Prompt

Use once per part, before drafting its chapters, to establish part-level scope
and depth targets.

```text
Write Part <N> of the Architect Handbook: <Part Name>.

This part should teach <Part Name> from first principles to expert level.
Assume the reader is a backend/frontend engineer transitioning into Solution
Architecture.

Every topic in this part should explain: why it exists, the problems it
solves, its internal mechanics, performance characteristics, security
implications, cloud implications, and common failure modes.

Include diagrams, production debugging guidance, interview questions, and
architecture scenarios for each chapter in this part.

Consult BOOK_PLAN.md for the exact chapter list for this part, and
CORE_CONCEPTS.md before drafting any chapter to avoid re-explaining concepts
owned by another part.

Before chapter drafting begins, create or update a `<part-folder>/TOPIC_MAP.md`
with a reader outcome, scope/ownership boundaries, coverage and decision
concerns, and at least five distinct diagram opportunities for every chapter.
Add `Topic map: [TOPIC_MAP.md](TOPIC_MAP.md)` near the top of that part's
`PART_OVERVIEW.md`. When revisiting a part that predates this workflow, backfill
its topic map and overview link before continuing chapter work; never add a link
to a map file that does not exist.

Target <page estimate> pages for the part as a whole.
```
