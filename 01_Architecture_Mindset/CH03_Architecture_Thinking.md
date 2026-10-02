# Chapter: Architecture Thinking

Part: [01 — Architecture Mindset](PART_OVERVIEW.md) · Status: Drafted

## 1. Introduction

Architecture thinking is the cognitive discipline of reasoning about
significant, hard-to-reverse design decisions under incomplete information
and competing stakeholder concerns. It is not a technology, a framework, or a
diagram notation — it is the mental toolkit a Solution Architect applies
*before* reaching for any specific pattern, cloud service, or code
structure. This chapter is deliberately scoped to that toolkit: how to
classify decisions, surface trade-offs, apply systems thinking, recognize the
cognitive biases that distort technical judgment, and document the resulting
rationale so it survives past the meeting it was made in.

This chapter does not define what software architecture *is* as a discipline,
nor does it describe the responsibilities of the Solution Architect role —
those are covered by this part's other two chapters (see
[PART_OVERVIEW.md](PART_OVERVIEW.md)). What follows assumes you already know,
at a working level, that architecture concerns the decisions that are
expensive to change later; this chapter is about *how to think through those
decisions well*, independent of whether the decision at hand is about a
database, an API style, a deployment topology, or an org structure.

Every later chapter in this handbook — REST versus GraphQL, monolith versus
microservices, SQL versus NoSQL, synchronous versus event-driven — is, at
bottom, an application of the trade-off reasoning introduced here. Those
chapters own the specifics of their own domain; this chapter owns the
general-purpose reasoning process and vocabulary (decision reversibility,
quality-attribute-driven trade-off analysis, Architecture Decision Records)
that the rest of the book leans on without re-deriving it.

## 2. Historical Evolution

- **Structured design (1970s)** — Yourdon, Constantine, and DeMarco
  formalized decomposition and coupling/cohesion as things worth reasoning
  about explicitly, rather than leaving module boundaries to accident.
- **"No Silver Bullet" (Fred Brooks, 1986)** — distinguished *essential*
  complexity (inherent to the problem) from *accidental* complexity
  (introduced by our tools and choices), and argued no single technique would
  ever eliminate the essential kind. This distinction remains one of the
  sharpest tools in architecture thinking.
- **4+1 architectural view model (Philippe Kruchten, 1995)** — proposed that
  no single diagram captures a system; logical, process, development,
  physical, and scenario views each answer a different stakeholder's
  question. This normalized the idea that architecture is *multiple
  perspectives*, not one blueprint.
- **Attribute-Driven Design and ATAM (Architecture Tradeoff Analysis Method)
  (Bass, Clements, Kazman — late 1990s, Software Engineering Institute)** —
  gave the field its first rigorous, repeatable method for evaluating an
  architecture against competing quality attributes (performance,
  availability, security, modifiability) via structured scenarios, rather
  than informal opinion.
- **Architecture Decision Records (Michael Nygard, 2011)** — proposed
  capturing individual decisions as small, immutable, timestamped documents
  living next to the code, replacing the single ever-changing "design
  document" that nobody trusted as current.
- **Evolutionary Architecture and fitness functions (Neal Ford, Rebecca
  Parsons, Patrick Kua — *Building Evolutionary Architectures*, 2017)** —
  reframed architecture as something that changes incrementally under
  automated, objective guardrails, rather than something fixed at a single
  up-front design phase.
- **"One-way door / two-way door" decision framing (popularized by Amazon's
  leadership practices, 2010s)** — gave teams a fast heuristic for calibrating
  how much process a decision deserves, based on how reversible it is, rather
  than treating all decisions with uniform (and usually excessive) ceremony.
- **Wardley Mapping (Simon Wardley, 2010s)** — added a strategic,
  evolution-aware layer to architecture thinking: mapping components by
  their visibility to the user and their evolutionary maturity (genesis to
  commodity) to reason about *where* to invest architectural effort.
- **Team Topologies and cognitive load (Matthew Skelton, Manuel Pais,
  2019)** — connected architecture decisions explicitly to team boundaries
  and the finite cognitive capacity of the humans who must operate a system,
  reinforcing Conway's Law as a design input rather than an afterthought.

## 3. Why It Exists

Architecture decisions differ from ordinary engineering decisions in three
ways that make ad hoc, un-examined judgment risky: they are often expensive
or slow to reverse once built upon; they must satisfy multiple, frequently
conflicting stakeholder concerns (a faster response time for users versus a
lower cloud bill for finance, for instance) simultaneously; and they are made
under genuine uncertainty about future load, team growth, and requirements
that haven't been written yet. Technical correctness alone does not resolve
any of these three problems — a "correct" design that ignores the org's
actual team structure, or that optimizes a quality attribute nobody asked
for, can still be a bad architectural decision. Architecture thinking exists
to make the trade-offs, the uncertainty, and the reversibility of a decision
*explicit* and *examined*, instead of leaving them implicit in one person's
intuition — because implicit trade-offs cannot be challenged, revisited, or
learned from when circumstances change.

## 4. Core Concepts

- **Essential versus accidental complexity (Brooks)**. Essential complexity
  is inherent to the problem domain itself (an inventory system must
  reconcile concurrent stock updates; that difficulty doesn't go away no
  matter what you build). Accidental complexity is complexity introduced by
  the tools, platforms, and choices used to solve the problem (a
  home-grown message queue with hand-rolled retry logic, when a managed
  queue would do). Architecture thinking's first move on any hard problem is
  separating the two: you cannot engineer away essential complexity, only
  manage it; you should always try to engineer away accidental complexity.

- **Reversible ("two-way door") versus irreversible ("one-way door")
  decisions**. A two-way door decision can be undone at low cost if it turns
  out wrong (choosing a logging library, picking an initial pagination
  scheme for an internal-only endpoint). A one-way door decision is
  expensive or impossible to reverse once committed (choosing a primary data
  store's replication topology after production data has accumulated,
  picking a multi-tenant isolation model, committing to a public API
  contract). The single highest-leverage habit in architecture thinking is
  classifying a decision correctly *before* deciding how much analysis it
  deserves: two-way doors should be decided fast, by the person closest to
  the work, with room to change course; one-way doors deserve the full
  weight of trade-off analysis, broader stakeholder input, and often a
  reversible *first step* (a spike, a pilot, a feature flag) before full
  commitment.

- **Quality attributes as the currency of trade-off analysis**. Every
  architecture decision trades one quality attribute against another —
  availability against cost, latency against consistency, flexibility
  against simplicity, security against usability. Architecture thinking
  requires naming the quality attributes actually in tension for the
  decision at hand (not a generic checklist) and stating priorities among
  them explicitly, because an architecture cannot maximize every quality
  attribute at once. A decision made without naming which attribute it
  optimizes for, and which it knowingly sacrifices, has not actually been
  analyzed — it has been guessed.

- **Architecture Decision Records (ADRs)**. A short, immutable, dated
  document capturing one decision: the context that made it necessary, the
  options considered, the decision made, its consequences (including
  accepted downsides), and its status (proposed, accepted, superseded). ADRs
  turn architecture rationale from tribal knowledge held in one person's head
  into a durable, searchable record that survives staff turnover and lets a
  future team understand *why*, not just *what*. See the template and worked
  example in Section 10.

- **Trade-off Analysis (the general method, of which ATAM (Architecture
  Tradeoff Analysis Method) is the most formalized version)**. A structured
  way of comparing options against explicit quality-attribute scenarios
  ("under a 5x traffic spike, p99 latency must stay under 300ms") rather than
  comparing them in the abstract. The output is not a single "best" answer
  but a matrix of which option satisfies which scenario at what cost — the
  decision itself still requires a human to weigh priorities, but the matrix
  makes disagreement about *priorities* separable from disagreement about
  *facts*.

- **Systems thinking: feedback loops and second-order effects**. Architecture
  decisions rarely act in isolation — adding a cache changes the load
  profile on the database, which changes what capacity planning looks like,
  which changes the cost model, which changes what the business will
  approve next quarter. Architecture thinking asks not just "what does this
  decision do" but "what does this decision change downstream, and does that
  downstream change feed back into the original problem" (a reinforcing or
  balancing feedback loop). Ignoring second-order effects is how well-intentioned
  local optimizations (e.g., a team independently choosing its own message
  broker) produce global problems (operational sprawl across the
  organization).

- **Conway's Law and the inverse Conway maneuver** (full definition and
  history owned by
  [What is Software Architecture?, Section 3](CH01_What_is_Software_Architecture.md#3-why-it-exists)).
  Architecture thinking treats this as a design input, not an accident to
  route around after the fact: if you want a modular system, you often need
  to shape team boundaries first, because a team structure that doesn't
  match the intended module boundaries will eventually pull the
  architecture back toward whatever the team structure actually is.

- **Cognitive biases that distort architectural judgment**. Architects are
  not immune to well-documented decision biases, and naming them is itself a
  architecture-thinking skill: **resume-driven development** (choosing a
  technology to build a marketable skill rather than because it fits the
  problem), **sunk cost fallacy** (continuing to invest in a chosen
  architecture because of what's already been spent on it, not because it's
  still the right choice), **confirmation bias** (seeking evidence that
  supports a preferred option instead of actively trying to falsify it),
  **HiPPO (Highest Paid Person's Opinion)** decision-making (deferring to
  seniority/authority over evidence), and **groupthink** (a team converging
  on consensus without anyone stress-testing the decision). A trade-off
  matrix and an ADR's "options considered" section are partly there to make
  these biases visible and challengeable.

- **Optionality and the last responsible moment**. Where a decision is
  genuinely uncertain and reversible, architecture thinking favors *deferring*
  commitment until the last point at which delaying no longer has a lower
  cost than deciding now — not deferring indefinitely (which is its own
  failure mode, "analysis paralysis"), but not deciding prematurely either,
  when a small amount of additional information would materially change the
  answer.

## 5. Internal Working

Architecture thinking, applied to a single decision, follows a repeatable
loop rather than a single leap to a solution:

1. **Frame the problem and name the quality attribute drivers.** What is
   actually being decided, and which quality attributes (from Section 4) are
   in tension? Skipping this step is the single most common cause of
   architecture debates that go in circles — the participants are often
   arguing from different, unstated priority orderings of the same quality
   attributes.
2. **Classify reversibility.** Is this a one-way door or a two-way door
   (Section 4)? This determines how much of the remaining process is
   worth investing in.
3. **Generate genuinely distinct options**, including the option of doing
   nothing/deferring. A trade-off analysis with only one real option
   dressed up as several is not an analysis.
4. **Evaluate each option against the named quality-attribute scenarios**,
   using a trade-off matrix (Section 10) to make the comparison legible to
   people who weren't in the room.
5. **Decide, and record the decision as an ADR** (Section 4), explicitly
   including the rejected alternatives and *why* they were rejected — this
   is what lets a future re-evaluation start from "what's changed since"
   instead of re-litigating settled ground.
6. **Instrument the decision with a feedback signal** — a fitness function,
   a dashboard, or simply a review date — so the decision's real-world
   consequences feed back into the next iteration of this loop, closing the
   systems-thinking loop from Section 4.

```text
Frame problem + name           Classify reversibility        Generate options
quality-attribute drivers  -->  (one-way vs two-way door) --> (incl. "do nothing")
        ^                                                            |
        |                                                            v
Feedback signal            <--   Record decision (ADR)   <--  Evaluate trade-offs
(fitness function,               incl. rejected options         (trade-off matrix)
 dashboard, review date)
```

A flowchart form of this loop, suitable for a workshop wall or a diagram
asset, is referenced at
[diagrams/flow/architecture-decision-loop.md](../diagrams/flow/architecture-decision-loop.md).

## 6. Design Principles

- **Optimize for the cost of being wrong, not just the cost of building
  right.** Since decisions are made under uncertainty, the expected cost of
  an option should weigh both how likely it is to be the wrong call *and*
  how expensive that would be to fix — a cheap, easily-reversed option that's
  50% likely to be wrong can beat an expensive, hard-to-reverse option that's
  80% likely to be right.
- **Match rigor to reversibility, not to seniority or anxiety.** Spend
  analysis effort proportional to how hard a decision is to undo, not to how
  senior the person raising it is or how uncomfortable the uncertainty feels.
- **Separate concerns by volatility, not only by layer.** Group what changes
  for the same reason, at the same rate, together — and isolate it from what
  changes for different reasons at different rates — which is a generalization
  of the same instinct behind traditional layered separation of concerns.
- **Prefer explicit, written trade-offs over implicit tribal knowledge.**
  If the rationale for a decision exists only in one person's memory, the
  organization has not actually made a durable decision — it has deferred
  the real decision to whenever that person is unavailable.
- **Design for the team you actually have.** Conway's Law (Section 4) means
  an architecture that ignores real team boundaries and communication
  patterns will drift toward matching them anyway, usually at a higher cost
  than designing for them deliberately from the start.
- **Favor the simplest design that satisfies the *known, named* quality
  attribute drivers** — not the simplest design in the abstract, and not a
  design speculatively generalized for requirements nobody has actually
  stated yet.

## 7. Architecture Patterns

These are recurring *decision-making* patterns — techniques for structuring
the thinking process itself, distinct from the system design patterns
covered in [Part 20 — Architecture Patterns](../20_Architecture_Patterns/PART_OVERVIEW.md).

- **ADR-per-decision**: one short document per decision rather than one
  monolithic, perpetually-stale design document (Section 4).
- **ATAM-style trade-off workshops**: bring stakeholders together around
  concrete quality-attribute scenarios rather than abstract preferences,
  producing a shared trade-off matrix as the workshop's artifact.
- **Wardley Mapping**: plot components on axes of user visibility and
  evolutionary maturity (genesis → custom-built → product → commodity) to
  decide *where* bespoke architectural investment is warranted versus where
  a commodity solution should be bought or adopted rather than built.
- **Risk-storming / risk matrix**: a lightweight group exercise to
  surface and rank the specific risks a design must mitigate, before
  choosing the design that mitigates the highest-ranked ones first.
- **Spikes and steel threads**: a small, time-boxed, throwaway
  implementation used specifically to resolve a named unknown before
  committing to a one-way door decision — the output is *information*, not
  production code.
- **Architecture katas**: structured practice exercises (see Section 25)
  used to build the trade-off-reasoning muscle on low-stakes scenarios before
  applying it to real, expensive decisions.

## 8. Production Architecture

In a functioning engineering organization, architecture thinking is not a
one-time event but a continuous pipeline that connects a proposal to
production feedback:

```text
Problem framed (quality-attribute drivers named)
            |
            v
  Design doc / RFC (Request for Comments) circulated for review
            |
            v
   Architecture review (rigor scaled to reversibility, Section 5)
            |
            v
   ADR recorded (decision + rejected alternatives + rationale)
            |
            v
      Implementation, guarded by fitness functions in CI
      (Continuous Integration) where the decision is testable
            |
            v
  Production telemetry validates or challenges the decision's
  assumptions  --------------------------------------------->  feeds back
                                                                 into the
                                                                 next
                                                                 decision
                                                                 loop
```

The review step's weight should scale with reversibility (Section 5): a
two-way door decision might only need an asynchronous comment thread on the
ADR itself, while a one-way door decision (a new data store, a public API
contract, a multi-region topology) warrants a live trade-off workshop with
the stakeholders who own the competing quality attributes.

## 9. Implementation

Day to day, applying architecture thinking looks like concrete, repeatable
habits rather than a special "architecture mode": writing a one-page ADR
before, not after, a non-trivial decision is implemented; running a trade-off
matrix (Section 10) whenever more than one credible option exists; keeping a
lightweight risk log for a project's open one-way door decisions so they
don't get made by default through inaction; and scheduling a review trigger
(a date, a metric threshold, or a scale milestone) for any decision made
under real uncertainty, so it gets revisited deliberately rather than only
when something breaks.

## 10. Complete Code Examples

An ADR is a template, not code — here is the standard structure this chapter
recommends, worked through for a concrete decision:

```markdown
# ADR 007: Use a modular monolith for the new billing service

## Status
Accepted (2026-02-10)

## Context
The billing service must ship an MVP (Minimum Viable Product) within one
quarter, with a single team of four engineers. Domain boundaries between
invoicing, payments, and dunning are still being discovered, and traffic
volume is unproven.

## Decision
Build a single deployable modular monolith with enforced module boundaries
(invoicing/payments/dunning as separate packages with a fitness function
banning cross-package internal imports), rather than starting with separate
microservices.

## Options considered
1. Microservices per domain module from day one — rejected: domain
   boundaries aren't stable yet, and splitting them prematurely would make
   the (still-likely) boundary corrections expensive cross-service changes
   instead of cheap in-process refactors.
2. Single unstructured monolith — rejected: without enforced module
   boundaries, coupling would silently increase, making a future split
   strictly harder, not easier.
3. Modular monolith with enforced boundaries (chosen) — keeps the
   one-way-door cost low (a future extraction is a refactor, not a
   distributed-systems rewrite) while avoiding the accidental complexity
   (Section 4) of operating multiple services before there's a proven need.

## Consequences
- We accept slower horizontal scaling of individual modules independently,
  in exchange for lower operational cost and faster iteration now.
- A fitness function (Section 16) enforcing module-boundary isolation is
  required in CI from day one, or this decision silently degrades to option 2.
- Revisit trigger: if invoicing's throughput requirement diverges from
  payments' by more than 5x, or team headcount crosses eight engineers.
```

A small trade-off-matrix scoring tool (weighted-sum comparison across named
quality-attribute scenarios, as described in Section 4/5) is referenced here
for the code-chapter pass to implement:

- Python: [code/python/architecture-thinking-chapter/tradeoff_matrix.py](../code/python/architecture-thinking-chapter/tradeoff_matrix.py)
- Node.js: [code/node/architecture-thinking-chapter/tradeoff_matrix.js](../code/node/architecture-thinking-chapter/tradeoff_matrix.js)

## 11. Performance

Applied to the decision-making process itself, "performance" means
time-to-decision, not CPU cycles: timeboxing spikes so an open question
doesn't silently expand to fill the schedule; using a one-page ADR instead of
a multi-week design-document cycle for anything classified as a two-way
door; and avoiding "meeting-driven architecture," where the same trade-offs
get re-debated in every recurring sync because nothing was written down the
first time. The single biggest performance win in architecture thinking is
correctly classifying reversibility (Section 4) early — most analysis-paralysis
cases are two-way doors being treated, out of anxiety, as one-way doors.

## 12. Scalability

Scaling architecture thinking across an organization means it cannot remain
a single architect's bottleneck. This is achieved by: distributing decision
rights (a lightweight RACI — Responsible, Accountable, Consulted, Informed —
per decision category, so most two-way doors never need to reach a central
board); publishing the organization's ADR log so precedent is discoverable
instead of re-litigated team by team; and replacing central gatekeeping with
self-service fitness functions (Section 16) that teams run in their own CI
pipelines, so architectural guardrails scale with the number of teams instead
of with the availability of a central reviewer. This connects directly to
Conway's Law (Section 4): decision-making structure is itself an
architectural choice, and a single central bottleneck architect produces the
same kind of drag on a growing organization that a single shared database
does on a growing system.

## 13. Security

Security is one of the quality attributes traded off in Section 4 rather
than a separate concern layered on afterward — threat modeling (for example,
using the STRIDE (Spoofing, Tampering, Repudiation, Information disclosure,
Denial of service, Elevation of privilege) heuristic to systematically
enumerate what could go wrong) is architecture thinking's trade-off method
applied specifically to adversarial quality attributes. The full treatment of
threat modeling, STRIDE, and the OWASP (Open Worldwide Application Security
Project) Top 10 is owned by [Security](../15_Security/PART_OVERVIEW.md); the
point for this chapter is narrower: security requirements must be named as
explicit quality-attribute drivers *before* option evaluation (Section 5,
step 1), because a security requirement discovered after a decision is made
is a decision that will need to be revisited, at whatever cost its
reversibility (Section 4) implies.

## 14. Observability

Architecture thinking treats production telemetry as the empirical evidence
that closes the systems-thinking feedback loop (Section 4, Section 5): a
decision's stated assumptions ("this cache will keep database load under
40%") should map to a metric that can later confirm or falsify them. Full
metrics, tracing, and logging design is owned by
[Observability](../14_Observability/PART_OVERVIEW.md); the point here is that
every non-trivial ADR should name the signal that will tell you if it was
wrong, not just the reasoning for why it seemed right at decision time.

## 15. Failure Scenarios

- **Ivory-tower architecture**: decisions made in isolation from the delivery
  team, disconnected from real constraints, that arrive as a mandate rather
  than a collaboratively reasoned trade-off — these get quietly
  worked around rather than followed.
- **Analysis paralysis**: a two-way door decision misclassified as a one-way
  door, consuming weeks of workshop time on a choice that could have been
  made, tried, and cheaply reversed in days.
- **Undocumented rationale rot**: a decision's reasoning lived only in the
  heads of engineers who have since left, so the current team either
  re-litigates settled trade-offs from scratch or, worse, silently violates
  a constraint nobody remembers the reason for.
- **Cargo-culted patterns**: adopting a pattern (microservices, event
  sourcing, a specific cloud service) because a well-known company used it,
  without checking whether the same quality-attribute drivers actually apply
  to your context.
- **HiPPO override with no recorded dissent**: a trade-off analysis
  correctly favors option A, a senior stakeholder overrides it to option B
  without a documented rationale, and the reasons for the override are lost
  the moment it turns out to be wrong.

## 16. Testing

Architecture decisions are "tested" differently from code, but the
discipline is the same:

- **Fitness functions** (full definition and code examples owned by
  [What is Software Architecture?, Sections 9-10](CH01_What_is_Software_Architecture.md#9-implementation)):
  applied here as the check that a decision's intended property still
  holds — a dependency-direction check (e.g., using a tool like ArchUnit for
  Java) that fails the build if a module boundary from an ADR is violated,
  or a latency budget check in a performance test suite.
- **Architecture review as peer review**: a trade-off matrix and its ADR
  should be reviewed the way code is — by someone who wasn't in the room when
  it was drafted, specifically checking whether the named quality-attribute
  drivers and rejected alternatives are actually complete.
- **Game days / chaos exercises**: deliberately test the *assumptions*
  behind a resilience-related decision (e.g., "the system tolerates losing
  one availability zone") against reality rather than trusting the design
  intent alone.
- **ADR review checklist**: does the record name the quality-attribute
  drivers, the rejected alternatives with reasons, the reversibility
  classification, and a revisit trigger? An ADR missing any of these has not
  actually captured the trade-off, only the outcome.

## 17. Common Mistakes

- Treating architecture as a one-time, up-front phase completed before
  delivery starts, instead of a continuous loop (Section 5) revisited as
  assumptions change.
- Letting personal technology preference (resume-driven development,
  Section 4) substitute for quality-attribute-driven analysis.
- Skipping the "options considered / rejected" step, leaving no record of
  *why* the alternatives weren't chosen — which forces every future
  reconsideration to start from zero.
- Applying uniform process rigor to every decision regardless of
  reversibility, causing both analysis paralysis on cheap decisions and
  under-analysis on expensive ones.
- Naming quality attributes generically ("it should be scalable and
  secure") instead of as concrete, falsifiable scenarios ("must sustain
  10,000 requests/sec at p99 < 200ms with one availability zone down").

## 18. Best Practices

- Write an ADR for every decision that would be expensive to reconstruct the
  reasoning for later — err toward writing one, not toward skipping it.
- Name quality-attribute drivers as concrete scenarios before evaluating
  options, not after a preferred option has already been picked.
- Classify reversibility explicitly and let it set the rigor budget for the
  rest of the process.
- Instrument every non-trivial decision with a feedback signal (a fitness
  function, a metric, or at minimum a calendar revisit date).
- Make disagreements about *priorities* visible and separate from
  disagreements about *facts*, using a shared trade-off matrix as the
  common artifact.

## 19. Anti-Patterns

- **Ivory tower architecture** — decisions handed down without delivery-team
  input or feedback loops back from production (Section 15).
- **Golden hammer** — reflexively applying one favorite pattern or technology
  to every problem regardless of its actual quality-attribute drivers.
- **Analysis paralysis** — endlessly deliberating a decision that was
  actually a cheap, reversible two-way door.
- **Architecture-by-PowerPoint** — a design that looks coherent in a
  presentation but was never validated against real constraints, team
  capacity, or existing systems.
- **Undocumented tribal-knowledge architecture** — a system whose real
  constraints and the reasons behind them exist only in a few people's
  memories, not in any durable record.

## 20. Trade-off Analysis

| Decision | Benefit | Cost |
|---|---|---|
| Write an ADR per decision vs. a single evolving design doc | Durable, per-decision rationale that survives staff turnover; easy to supersede individually | More documents to maintain discoverability across |
| Classify and fast-track two-way doors vs. uniform review rigor | Much faster iteration on low-stakes decisions | Requires trusting individual/team judgment on the classification itself |
| Central architecture review board vs. distributed decision rights | Consistency, cross-team visibility of precedent | Becomes a bottleneck as the organization scales (Section 12) |
| Defer a decision to the last responsible moment vs. decide early for certainty | Better-informed decision, avoids premature one-way commitments | Risk of drifting into analysis paralysis if the deferral has no clear trigger |

## 21. Comparison Table

| Framework | Granularity | Primary audience | Update cadence | Best fit |
|---|---|---|---|---|
| ADR (Architecture Decision Record) | One decision | Engineers, future maintainers | Immutable once accepted; superseded, not edited | Any non-trivial, especially one-way door, decision |
| RFC (Request for Comments) | One proposal, pre-decision | Broader stakeholder group | Iterated during review, then closed | Building consensus before a decision is finalized |
| Design document | Whole system or subsystem | New team members, broad audience | Periodically revised, tends to go stale | Onboarding and holistic system understanding |
| ATAM workshop output | One architecture, multiple scenarios | Architects, senior stakeholders | Point-in-time snapshot | High-stakes, multi-quality-attribute one-way door decisions |
| Wardley Map | Whole value chain | Strategic/leadership stakeholders | Revised as components evolve | Deciding where to build bespoke vs. buy/adopt commodity |

## 22. Real-World Case Study

A payments platform team needed to decide how to structure a new billing
capability under a one-quarter deadline, with domain boundaries between
invoicing, payments, and dunning still not fully understood. Rather than
defaulting to microservices (the organization's prevailing pattern for other
systems — an instance of the golden-hammer anti-pattern the team explicitly
named and avoided), the team ran a short trade-off exercise: they named the
actual quality-attribute drivers (time-to-MVP, cost of getting the module
boundaries wrong given they were still being discovered, and a known future
need for invoicing to scale independently once volume proved out), classified
the choice of *initial* deployment topology as a two-way door (an in-process
module split can be extracted into a service later; the reverse — merging
services back — is far more expensive), and chose a modular monolith with a
fitness function enforcing module isolation in continuous integration
(Section 10's worked ADR example is drawn from this case). Two quarters
later, once invoicing's load diverged sharply from payments', the team
revisited the same ADR, found its recorded revisit trigger had fired, and
extracted invoicing into its own service — a change the enforced module
boundaries made mechanical rather than a rewrite. The full trade-offs of
monolith-versus-microservices as a *pattern* are owned by
[Part 20 — Architecture Patterns](../20_Architecture_Patterns/PART_OVERVIEW.md);
what this case illustrates is the thinking process — driver-naming,
reversibility classification, and instrumented revisit — not the pattern
itself.

## 23. Interview Questions

1. Walk me through a recent architecture decision you made — what made it a
   one-way door or a two-way door, and did that classification change how
   much process you applied?
2. How do you identify the quality-attribute drivers for a decision before
   choosing among options, and what do you do when two stakeholders name
   conflicting drivers as the top priority?
3. Describe a decision you later reversed. What evidence triggered the
   reversal, and was that evidence something you'd planned to watch for at
   decision time, or a surprise?
4. How do you respond when a senior stakeholder's preference (a HiPPO —
   Highest Paid Person's Opinion — situation) conflicts with your trade-off
   analysis?
5. What's the difference between essential and accidental complexity, and
   why does misidentifying one as the other lead teams to solve the wrong
   problem?

## 24. Hands-on Exercises

Take a real, moderately significant decision from your current or a recent
project. Write a full ADR for it using the template in Section 10, including
at least two genuinely rejected alternatives with reasons. Then run the
trade-off-matrix tool referenced in Section 10 against those same options
and check whether the matrix's output matches the decision you actually
made — if it doesn't, identify which quality-attribute priority was implicit
in your original decision but missing from the matrix.

## 25. Design Exercises

**Scenario**: an e-commerce inventory system must decide its data-consistency
approach ahead of a predictable Black-Friday-scale traffic spike (strong
consistency per warehouse vs. eventual consistency with reconciliation across
warehouses). Produce: (1) an explicit list of quality-attribute drivers as
concrete scenarios (not generic labels), (2) at least three genuinely
distinct options including "do nothing differently," (3) a trade-off matrix
scoring each option against each scenario, and (4) a reversibility
classification with a stated rationale. Evaluation criteria: are the drivers
concrete and falsifiable; are the options genuinely distinct rather than
restatements of one option; does the reversibility classification match the
actual cost of undoing the choice once live; is a revisit trigger specified.

## 26. Architecture Review Questions

- Is the decision documented (an ADR or equivalent) with the rejected
  alternatives and the reasons they were rejected, not just the final
  choice?
- Are the quality-attribute drivers named as concrete, falsifiable scenarios
  rather than generic labels like "scalable" or "secure"?
- Is the decision correctly classified as reversible or irreversible, and
  was the rigor applied actually proportional to that classification?
- Is there a specific signal (a fitness function, a metric, or a review
  date) that will tell the team if this decision turns out to be wrong?
- Who has the authority to revisit this decision, and under what condition
  should they?

## 27. Summary

Architecture thinking is the reasoning discipline underneath every
technology-specific decision covered elsewhere in this handbook: naming the
quality attributes actually in tension, classifying a decision's
reversibility before deciding how much rigor it deserves, generating and
honestly evaluating genuinely distinct options, recording the resulting
rationale (including what was rejected and why) so it survives past the
meeting it was made in, and closing the loop with a feedback signal that can
confirm or falsify the decision later. None of this replaces domain
expertise in any specific area — networking, data storage, distributed
systems, cloud platforms — it is the method by which that expertise gets
turned into a defensible, revisitable decision instead of an opinion.

**Further reading**: [Part 01 — Architecture Mindset](PART_OVERVIEW.md) ·
[Part 07 — System Design and Distributed Systems](../07_System_Design_and_Distributed_Systems/PART_OVERVIEW.md) ·
[Part 20 — Architecture Patterns](../20_Architecture_Patterns/PART_OVERVIEW.md) ·
[Part 21 — Architecture Documentation](../21_Architecture_Documentation/PART_OVERVIEW.md) ·
[Part 14 — Observability](../14_Observability/PART_OVERVIEW.md) ·
[Part 15 — Security](../15_Security/PART_OVERVIEW.md)
