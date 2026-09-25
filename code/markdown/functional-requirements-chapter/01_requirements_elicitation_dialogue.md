# Artifact 1 — A Worked Requirements-Elicitation Dialogue

**Prompt as given (deliberately underspecified, System Design Interview style):**
> "Design a URL shortener."

This artifact shows the actual clarifying-question sequence a candidate (or a
Solution Architect in a real kickoff meeting) should run before writing a
single line of design, and how each answer collapses ambiguity into a
concrete, testable requirement. See
[Section 4.6](../../../07_System_Design_and_Distributed_Systems/CH01_Functional_Requirements.md#46-scoping-ambiguous-requirements-in-an-interview-setting)
of the chapter for the underlying technique this dialogue demonstrates.

---

## Turn 1 — Restate and anchor scope

**Candidate:** "Before I design anything, I want to confirm scope. Are we
building a service that (a) takes a long URL and returns a short one, and
(b) redirects the short one back to the original — both read and write
paths?"

**Interviewer:** "Yes, both."

**Why this matters:** anchors the boundary of the system before any
technical discussion starts. Without this, candidates routinely design only
the write path and discover the read path (which dominates traffic by
orders of magnitude, see Section 4.1 of the chapter) has no design at all.

## Turn 2 — Quantify scale (turns a vague NFR into a sizing input)

**Candidate:** "What's the expected write and read volume? Order of
magnitude is fine."

**Interviewer:** "100 million new URLs created per month; reads run about
100:1 against writes."

**Derived requirement:**
- FR-1 restated with a scale annotation: ~40 writes/sec average, ~4,000
  reads/sec average (used later to justify a design decision, not a
  functional requirement itself — flagged here only to show *why* the
  clarifying question was asked; the full non-functional treatment belongs
  to the sibling Non-Functional Requirements chapter).

## Turn 3 — Resolve an ambiguous verb ("shorten")

**Candidate:** "When you say shorten a URL — should the same long URL
always produce the same short URL, or can two requests for the same long
URL produce two different short URLs?"

**Interviewer:** "Up to you — justify your choice."

**Why this matters:** "shorten a URL" is exactly the kind of ambiguous verb
Section 4.4 of the chapter warns about — it hides a real design decision
(idempotent mapping vs. always-new-record) that changes the data model.
The candidate must make an explicit, stated assumption rather than silently
picking one.

**Resulting testable requirement:**
> FR-2: Given a long URL that has already been shortened by the same
> account, when the same account submits an identical long URL again, the
> system shall return the previously issued short URL rather than minting a
> new one. Given a long URL submitted by a different account (or
> anonymously), the system shall mint a new short URL, treating ownership
> as the deduplication scope.

## Turn 4 — Resolve a hidden non-functional-sounding requirement that is actually functional

**Candidate:** "Do short URLs expire, or do they live forever unless
deleted?"

**Interviewer:** "Let's say users can optionally set an expiration date;
default is no expiration."

**Resulting testable requirement:**
> FR-3: The system shall accept an optional `expires_at` timestamp at
> creation time. Given a request to resolve a short URL whose `expires_at`
> has passed, the system shall return HTTP 410 Gone rather than performing
> the redirect.

## Turn 5 — Surface an explicit non-goal (scope-cut)

**Candidate:** "I'm going to explicitly scope out custom vanity aliases
(e.g. `short.ly/my-brand`) and analytics/click-tracking dashboards unless
you want those in scope — they're common extensions but they roughly
double the design surface. Should I include either?"

**Interviewer:** "Include vanity aliases, skip analytics."

**Resulting requirement set change:**
- FR-4 (new, in scope): custom alias support with a collision-check rule.
- Explicit non-goal recorded: click analytics — **out of scope**, stated in
  the write-up so no reviewer later assumes it was forgotten rather than
  deliberately excluded.

## Turn 6 — Confirm the requirement set back to the interviewer before designing

**Candidate:** "To confirm before I start the high-level design: create a
short URL from a long URL (with optional custom alias and optional
expiration), redirect from short to long, per-account idempotent
deduplication of identical long URLs, and explicitly no analytics in this
pass. Did I miss anything load-bearing?"

**Interviewer:** "That's right — go ahead."

---

## Why this dialogue structure works (checklist form)

1. Anchor scope (what's in vs. out) before anything else.
2. Ask for order-of-magnitude scale even though it feeds NFRs, not FRs — it
   changes which functional edge cases matter (e.g. dedup at what scope).
3. Hunt for ambiguous verbs/nouns explicitly ("shorten", "same") and convert
   each into a Given/When/Then statement.
4. Distinguish requirements that sound non-functional but are actually
   functional behavior (expiration is a *behavior*, not a quality
   attribute).
5. State non-goals out loud and in writing — an omitted scope-cut reads as
   an oversight; a stated one reads as a deliberate architectural decision.
6. Play the requirement set back before moving to design, so any
   misunderstanding is caught in seconds rather than after a wasted design
   pass.

See [Artifact 3](03_scoped_requirement_set_url_shortener.md) for the final
consolidated, testable requirement set this dialogue produced, and
[Artifact 2](02_requirements_traceability_matrix.md) for how each of these
FR IDs traces forward into API/data-model decisions.
