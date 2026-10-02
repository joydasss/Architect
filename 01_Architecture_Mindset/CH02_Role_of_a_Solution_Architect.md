# Chapter: Role of a Solution Architect

Part: [01 — Architecture Mindset](PART_OVERVIEW.md) · Status: Drafted

## 1. Introduction

A Solution Architect is the person accountable for the technical shape of a
system across its full lifecycle — not just the diagram on day one, but the
decisions, trade-offs, and constraints that keep that system coherent as
requirements, teams, and scale all change under it. This chapter is about the
**role as a job function and career**: what a Solution Architect actually
does day to day, how the role differs from adjacent titles (Enterprise
Architect, Technical/Staff Engineer, Cloud Architect, Security Architect), how
the role is organized inside a company, and what "good" looks like in
practice. It deliberately does **not** define architecture itself — see
[What is Software Architecture?](CH01_What_is_Software_Architecture.md) for
that — and it does not teach the reasoning frameworks architects use to
evaluate trade-offs, which is the subject of
[Architecture Thinking](CH03_Architecture_Thinking.md). Where those chapters
define the discipline and its cognitive toolkit, this chapter defines the
*person who holds the job* and the organizational machinery around them.

The title "Solution Architect" is used loosely across the industry — at some
companies it means a pre-sales technical role at a cloud vendor; at others
it's the senior-most individual contributor on a product engineering team; at
others still it's a dedicated non-coding role sitting between Enterprise
Architecture and delivery teams. This chapter treats Solution Architect as the
role responsible for the end-to-end technical solution for one product,
platform, or program — translating business and product requirements into a
coherent technical design, making and documenting the significant technical
decisions, and remaining accountable for the solution's technical health after
delivery, not just at kickoff.

## 2. Historical Evolution

- **1970s-1980s — Systems Analyst / Chief Programmer**: large mainframe
  projects had a senior technical lead (IBM's "Chief Programmer Team" model)
  responsible for overall design, but the title "architect" was not yet in
  common use in software.
- **1987 — Zachman Framework**: John Zachman published a framework for
  classifying enterprise artifacts, borrowing the "architecture" metaphor
  from building construction and giving Enterprise Architecture its first
  formal vocabulary — a discipline this chapter's role interacts with
  constantly but does not itself own (see
  [Enterprise Architecture](../18_Enterprise_Architecture/PART_OVERVIEW.md)).
- **1992 — "Software Architecture" as a named discipline**: Dewayne Perry and
  Alexander Wolf's paper *Foundations for the Study of Software Architecture*
  and Mary Shaw's contemporaneous work gave academic grounding to treating a
  system's structure as a first-class design artifact, separate from any
  single module's implementation.
- **1990s — Client-server and the first "Software Architect" job titles**:
  as systems grew beyond what one senior developer could hold in their head,
  companies began formally splitting "architect" from "lead developer,"
  often as a promotion path for the most experienced engineers.
- **Late 1990s-2000s — SOA (Service-Oriented Architecture) and the rise of
  the enterprise Solution Architect**: large enterprises building
  service-oriented, multi-vendor integration landscapes needed a role
  distinct from Enterprise Architecture (company-wide standards) and
  Technical/Application Architecture (single-system depth) — Solution
  Architecture emerged to own the cross-system, single-initiative slice in
  between. TOGAF (The Open Group Architecture Framework), first published in
  1995, formalized much of this vocabulary.
- **2000s-2010s — Agile pushback against "ivory tower" architecture**: as
  Agile and Scrum spread, many organizations reacted against architects who
  produced designs disconnected from delivery teams, pushing toward
  architects embedded in or close to the teams building the system.
- **2010s — Cloud and the vendor-certified "Solutions Architect"**: AWS (2013),
  Azure, and Google Cloud Platform (GCP) all created "Solutions Architect"
  certification tracks and job families, popularizing a narrower,
  cloud-infrastructure-flavored version of the title alongside the older
  enterprise-software meaning — a major reason the title now means different
  things at different companies.
- **2010s-2020s — Convergence with Staff/Principal Engineering**: many
  product engineering organizations folded architectural accountability into
  senior individual-contributor engineering ladders (Staff Engineer,
  Principal Engineer) rather than a separate non-coding "Architect" title,
  while other organizations (especially large enterprises, consultancies, and
  regulated industries) kept Solution Architect as a distinct role. Both
  patterns coexist today, and this chapter treats them as the same underlying
  job function wearing different titles.

## 3. Why It Exists

A system's requirements arrive from product managers, business stakeholders,
compliance teams, and operations — each speaking a different vocabulary, each
optimizing for a different concern (time to market, cost, risk, reliability).
No single delivery team, focused on its own service, is well positioned to
resolve conflicts *between* those concerns at the level of an entire solution
that spans multiple teams, systems, and organizational boundaries. Without a
role accountable for that cross-cutting view, three failure modes recur
predictably: technical decisions get made locally and inconsistently (every
team picks its own message queue, ID format, or auth scheme), non-functional
requirements (NFRs) such as availability, security, and performance get
dropped because no one owns them across team boundaries, and organizational
knowledge about *why* a decision was made evaporates the moment the engineer
who made it changes teams. The Solution Architect role exists to hold that
cross-cutting accountability explicitly, so it does not silently fall through
the gaps between teams, and to make the resulting decisions — and their
rationale — visible and durable rather than tribal knowledge.

## 4. Core Concepts

- **Scope of accountability**: a Solution Architect owns the technical
  solution for a defined scope — one product, one platform, or one program —
  spanning multiple services/teams but narrower than an entire enterprise.
  This is the key distinction from adjacent titles:
  - **Enterprise Architect**: company-wide standards, technology strategy,
    and portfolio-level rationalization across *many* solutions (see
    [Enterprise Architecture](../18_Enterprise_Architecture/PART_OVERVIEW.md)).
  - **Technical/Application/Staff Engineer**: deep, single-system or
    single-team ownership, often still hands-on with code.
  - **Cloud Architect**: infrastructure- and platform-focused, concentrated
    on cloud provider services, landing zones, and infrastructure patterns.
  - **Security Architect**: security-control design and threat modeling
    across solutions, usually consulted by the Solution Architect rather than
    replacing them.
  - **Data Architect**: data model, data flow, and data platform design
    across solutions.
- **Advisory vs. decision-making authority**: some organizations give
  Solution Architects direct sign-off authority (a design cannot ship without
  their approval); others make the role purely advisory, with delivery teams
  retaining final say. Neither is universally correct — the right balance
  depends on organizational maturity and risk tolerance (see Section 7).
- **The technical-business bridge**: translating a business goal ("reduce
  checkout abandonment") into technical requirements (latency budget,
  availability target, data residency constraints) and translating technical
  constraints back into business terms (cost, risk, delivery timeline) for
  non-technical stakeholders — in both directions, continuously, not as a
  one-time handoff.
- **RACI matrix (Responsible, Accountable, Consulted, Informed)**: the
  standard tool for making a Solution Architect's authority explicit and
  visible to the rest of the organization. For any significant technical
  decision, the RACI matrix names who is *Responsible* (does the analysis),
  *Accountable* (owns the final call — often the Solution Architect or the
  engineering lead, never both for the same decision), *Consulted* (domain
  experts whose input is sought before deciding), and *Informed* (stakeholders
  told after the decision is made). Ambiguity here — several people believing
  they are Accountable, or no one believing they are — is one of the most
  common sources of architecture dysfunction in practice.
- **Architecture Decision Record (ADR)**: producing and maintaining ADRs
  (or an equivalent decision log) is one of the Solution Architect's core
  recurring work products — see
  [Architecture Thinking](CH03_Architecture_Thinking.md#4-core-concepts) for
  the format, template, and a worked example; this chapter focuses only on
  *when in the role's workflow* an ADR gets written and who is accountable
  for it (RACI, above).
- **Architecture Review Board (ARB)**: a recurring governance forum —
  sometimes a standing committee, sometimes a lightweight async review —
  where proposed designs above a certain risk/scope threshold are reviewed
  before implementation begins. Whether an organization has a formal ARB, an
  informal peer-review norm, or nothing at all is one of the biggest
  practical differences between how the Solution Architect role plays out
  day to day across companies (see Section 7).

## 5. Internal Working

The mechanics of how a Solution Architect actually spends their time and
exercises their accountability follow a recognizable, repeatable workflow
regardless of company:

1. **Intake** — a new initiative, a scaling problem, or a cross-team
   integration need arrives, usually from a product manager, engineering
   manager, or another architect, framed first in business/product terms.
2. **Framing** — the architect restates the problem as a set of concrete
   technical requirements and constraints: functional scope, NFRs (latency,
   availability, data volume, security/compliance constraints), existing
   systems that must be integrated with or migrated from, and the delivery
   timeline/budget envelope.
3. **Options analysis** — the architect (often with input from senior
   engineers on the affected teams — this is the "Consulted" role in the RACI
   sense) identifies 2-4 realistic options, not an exhaustive theoretical
   list, and evaluates each against the framed requirements using the
   trade-off reasoning covered in
   [Architecture Thinking](CH03_Architecture_Thinking.md).
4. **Decision and documentation** — a decision is made, an ADR (or
   equivalent) is written capturing the chosen option, the rejected
   alternatives, and *why*, and the decision is socialized with the teams who
   must implement it — ideally before it is finalized, not after, to catch
   objections while they are still cheap to act on.
5. **Review** — for decisions above the organization's risk threshold, the
   design goes through whatever review mechanism the organization uses (a
   formal ARB, a design-doc comment period, a pairing session with a peer
   architect) before implementation begins.
6. **Implementation support** — the architect stays engaged through build,
   answering the inevitable questions that arise once a design meets real
   code, rather than treating delivery as someone else's problem after
   handoff.
7. **Feedback loop** — after launch, the architect tracks whether the
   decision held up in production (see Sections 11 and 14) and feeds that
   evidence back into the next round of decisions, closing the loop that
   distinguishes a Solution Architect from someone who only produces
   one-off designs.

See the workflow as a diagram:
[diagrams/sequence/architecture-decision-workflow.md](../diagrams/sequence/architecture-decision-workflow.md).

## 6. Design Principles

These are principles the Solution Architect applies to *their own practice*,
distinct from the principles applied to the systems they design (which belong
to [Architecture Thinking](CH03_Architecture_Thinking.md)):

- **Decisions over documents**: an ADR is valuable because it captures a
  decision that was made and acted on, not because it exists — a folder of
  unused design documents is a symptom, not an achievement.
- **Preserve optionality until forced to decide**: commit to the decisions
  that must be made now (they block delivery) and explicitly defer the ones
  that don't, rather than resolving every open question up front out of a
  desire for completeness.
- **Communicate in the audience's vocabulary**: the same decision is framed
  in terms of latency budgets and failure modes for engineers, and in terms
  of cost, risk, and delivery date for business stakeholders — the
  underlying reasoning doesn't change, but the framing must.
- **Lead without relying on positional authority**: in most organizations the
  Solution Architect does not manage the engineers implementing the design,
  so influence comes from the quality of the reasoning, the trust built with
  delivery teams, and timely, honest communication — not from a title.
- **Stay close enough to implementation to remain credible**: an architect
  who has not personally validated that a design works against real
  constraints (a spike, a prototype, reading the actual code) loses the
  standing to make the call when a team pushes back — see the "ivory tower"
  anti-pattern in Section 19.
- **Evidence-based over opinion-based decisions**: prefer a benchmark, a
  spike, or production data over "I've always done it this way" — and be
  explicit when a decision genuinely is a judgment call under uncertainty
  rather than dressing up an opinion as settled fact.

## 7. Architecture Patterns

These are patterns for how the Solution Architect role itself is structured
inside an organization — not patterns for the systems being architected:

- **Centralized architecture team**: a dedicated team of architects, separate
  from delivery teams, who review and approve designs across the
  organization. Strongest guarantee of consistency; highest risk of becoming
  a bottleneck and of architects losing touch with delivery reality (see
  Section 15).
- **Embedded architect model**: each Solution Architect is attached to one
  product area or program and works day-to-day alongside its delivery teams,
  often holding both architecture accountability and some hands-on
  implementation role. Best context and trust with delivery teams; weakest
  built-in mechanism for cross-program consistency, since embedded architects
  can drift toward local optimization.
- **Federated / architecture guild model**: architects remain embedded in
  their own product areas but meet regularly as a peer group (a "guild" or
  "chapter") to align on cross-cutting standards, share decisions, and
  jointly review the highest-risk designs — attempting to capture the
  consistency benefit of centralization and the context benefit of embedding.
- **Architecture Review Board (ARB) as a gate**: a standing committee that
  must approve designs above a defined risk/cost/scope threshold before
  implementation starts — common in regulated industries (finance,
  healthcare) where the cost of a wrong architectural decision is unusually
  high and auditable governance is a compliance requirement, not just a
  preference.
- **Lightweight/asynchronous review**: instead of a standing board, designs
  are shared as documents with a defined comment period and a named
  approver, closer to a code-review norm than a committee meeting — lower
  overhead, but relies on a strong writing/review culture to catch problems
  that a synchronous discussion might surface faster.

## 8. Production Architecture

Where the role sits relative to other functions, in a representative
mid-size product engineering organization:

```text
                         CTO / VP Engineering
                                 |
                 -------------------------------------
                 |                                   |
        Enterprise Architecture                Engineering Managers
      (company-wide standards,                        |
       portfolio, tech strategy)           -------------------------
                 |                         |                       |
                 |  (consulted on cross-  Solution Architect   Solution Architect
                 |   solution standards)   (Product A)          (Product B)
                 |                                |                       |
                 -------------------->  ----------------------------------
                                        |         |          |
                                   Tech Lead   Tech Lead   Tech Lead
                                        |         |          |
                                   Dev Team   Dev Team   Dev Team
```

The Solution Architect typically reports into engineering leadership (not
Enterprise Architecture) but maintains a strong dotted-line relationship with
Enterprise Architecture for company-wide standards, and a peer relationship
with Product Management for scope and priority trade-offs. A fuller version
of this org placement, including the Security and Data Architect
relationships, is diagrammed here:
[diagrams/org/solution-architect-org-placement.md](../diagrams/org/solution-architect-org-placement.md).

## 9. Implementation

Standing up the Solution Architect function in an organization that doesn't
yet have it (or fixing one that isn't working) generally requires four
concrete steps, in this order:

1. **Write the charter**: a short document naming the role's scope
   (which programs/products it covers), its authority (advisory vs.
   sign-off — see Section 4), and its RACI position relative to Engineering
   Managers, Tech Leads, and Enterprise Architecture. Skipping this step is
   the single most common root cause of the role failing later — see
   Section 15.
2. **Define the decision-visibility mechanism**: pick one — an ADR
   repository, a design-doc wiki with a required review, a lightweight ARB —
   and make it the default path for any decision above an agreed threshold,
   rather than leaving that threshold to individual judgment from day one.
3. **Set the review cadence and threshold**: define, in writing, what kind of
   decision requires architect involvement at all (e.g., "introducing a new
   externally-facing dependency" or "any change with a data-migration
   component") — without a threshold, either everything gets escalated
   (bottleneck) or nothing does (the charter is ignored).
4. **Onboard against real work, not a theoretical backlog**: a new architect
   should shadow or co-own an in-flight decision within their first few
   weeks rather than starting with a clean-slate strategy document — this
   builds the delivery-team trust described in Section 6 far faster than a
   standalone onboarding deck.

## 10. Complete Code Examples

Because this chapter is about a role rather than a technology, its practical
artifact is a governance template rather than a runnable program — a RACI
matrix template, usable as-is (for the ADR template and a worked example,
see [Architecture Thinking, Section 10](CH03_Architecture_Thinking.md#10-complete-code-examples)):

- [code/templates/role-chapter/raci-matrix-template.csv](../code/templates/role-chapter/raci-matrix-template.csv)

## 11. Performance

"Performance" for a role, rather than a system, means how efficiently and
effectively the architecture function operates — measured through:

- **Decision cycle time**: how long it takes from an initiative being framed
  (Section 5, step 2) to a documented, socialized decision — a rising trend
  usually indicates the review mechanism (Section 7) has become a
  bottleneck, not that decisions have gotten harder.
- **Rework rate**: how often an implemented design has to be materially
  revisited within, say, 6 months of shipping — a proxy for decision
  quality, though some rework is healthy (evidence of learning, not
  necessarily a mistake).
- **Standards adoption rate**: what fraction of new services actually follow
  the architect-recommended patterns (as opposed to technically-compliant
  documentation that delivery teams route around) — low adoption is a strong
  signal that decisions aren't being made *with* delivery teams, only handed
  to them (see Section 15).

## 12. Scalability

A single Solution Architect can meaningfully engage with a limited number of
concurrent initiatives — in practice, most organizations find that ratio
degrades noticeably above roughly one architect per 25-40 engineers,
depending on how much of the architect's time is protected from ad hoc
firefighting. As an organization grows past what one architect (or one
centralized team) can cover, the scaling options are the same organizational
patterns from Section 7: add embedded architects per product area, formalize
a federated guild to keep them aligned, and push routine/low-risk decisions
down to a documented "paved road" (a pre-approved, self-service set of
default technology choices) so that the architect's attention is reserved for
genuinely novel or high-risk decisions rather than repeatedly re-approving
already-settled ones.

## 13. Security

The Solution Architect is rarely the security control expert (that role
belongs to a Security Architect — see
[Security](../15_Security/PART_OVERVIEW.md), which owns threat modeling, the
OWASP (Open Worldwide Application Security Project) Top 10, and control
design in depth), but is typically the person accountable for making sure
security is considered *at all* during design, specifically:

- Ensuring every design that crosses a trust boundary (public internet to
  internal network, one tenant's data to another's) is explicitly reviewed
  by or with a Security Architect before implementation, rather than as a
  pre-launch afterthought.
- Owning the data-flow diagram for a solution well enough to answer "where
  does this data live, and who/what can reach it" without having to ask the
  implementing team — a question regulators, auditors, and incident
  responders will all eventually ask.
- Making the trade-off between security control cost and business risk
  explicit and visible to the accountable business stakeholder, rather than
  the architect unilaterally deciding it on the business's behalf.

## 14. Observability

An organization observes the health of its architecture function through
artifacts, not vibes:

- A living decision log (the accumulated set of ADRs) that is actually
  referenced in later decisions and onboarding, not a write-only archive.
- A lightweight periodic review (quarterly is common) of decisions made in
  the prior period against what actually happened in production — did the
  latency budget hold, did the chosen vendor's pricing model scale as
  assumed.
- Direct signals from delivery teams — satisfaction surveys, retro feedback —
  on whether the architecture function is helping or slowing them down; a
  Solution Architect who never hears this feedback has no way to detect
  Section 15's failure modes before they become serious.

## 15. Failure Scenarios

- **The ivory tower architect**: designs are produced without engineering
  input, handed down as a fait accompli, and delivery teams either quietly
  route around them or implement them without conviction — usually traceable
  back to a missing or ignored charter (Section 9) and a violation of
  Section 6's "stay close enough to implementation" principle.
- **The bottleneck architect/ARB**: every decision, regardless of risk, must
  pass through one person or committee, and decision cycle time (Section 11)
  balloons — usually a missing review threshold (Section 9, step 3).
- **The PowerPoint architect**: an architect who has drifted far enough from
  implementation that their designs are no longer technically credible,
  losing the standing described in Section 6 and provoking the exact
  Agile-era backlash described in Section 2.
- **Decision amnesia**: without ADRs or an equivalent record, the same
  question ("why don't we just use X?") gets re-litigated repeatedly because
  no one can produce the original reasoning — an entirely avoidable failure
  given Section 4's ADR practice.
- **Diffused accountability**: no RACI clarity (Section 4) means multiple
  people believe they have final say on a decision, surfacing as conflict
  only after significant work has been invested in incompatible directions.

## 16. Testing

Architectural decisions are "tested" differently than code, but the
discipline is the same — validate before betting the whole solution on an
assumption:

- **Spikes/proof of concept (PoC)**: a small, time-boxed implementation that
  tests the riskiest assumption in a design (e.g., "can this database handle
  our write volume") before committing the full team to the direction.
- **Architecture fitness functions**: automated checks that continuously
  verify a system still satisfies an architectural constraint (e.g., a
  dependency-direction rule, a latency budget) as it evolves — full coverage
  of this technique belongs to
  [Architecture Patterns](../20_Architecture_Patterns/PART_OVERVIEW.md); the
  Solution Architect's role is deciding which constraints are worth
  encoding this way.
- **Staged/canary rollout of new patterns**: introducing a new pattern (a
  new messaging library, a new data-access convention) on one team or one
  service first, and validating it in production before mandating it more
  broadly.

## 17. Common Mistakes

- **Over-engineering for hypothetical future scale** instead of the scale
  the business actually needs in the realistic planning horizon, driven by
  a desire to look thorough rather than by evidence.
- **Producing a design without validating it against the team that has to
  build it**, discovering the gap only once implementation is already
  underway.
- **Treating every decision as equally important**, spending as much
  ceremony on a low-risk internal library choice as on a data-residency
  decision with regulatory consequences.
- **Avoiding unpopular but necessary calls** to preserve consensus, leaving a
  decision unmade until circumstances force a worse, rushed version of it.
- **Losing hands-on technical depth** over time and defaulting to whatever
  worked at a previous company, rather than validating against current
  constraints.

## 18. Best Practices

- Write an ADR (or equivalent) for every decision that would be expensive to
  reverse, and skip the ceremony for decisions that wouldn't.
- Socialize a decision with the implementing team *before* it's finalized,
  not as a review of a fait accompli.
- Keep a standing, protected block of hands-on time (code review, a spike, an
  on-call rotation) to preserve the technical credibility described in
  Section 6.
- Make the RACI for any significant decision explicit in writing before
  starting the options analysis, not after a disagreement has already
  surfaced.
- Track the outcomes of past decisions (Section 14) and be willing to revise
  a documented decision publicly when the evidence changes — this builds
  more credibility than being right the first time.

## 19. Anti-Patterns

- **Architecture-by-committee**: every decision requires unanimous sign-off
  from a large group, producing lowest-common-denominator designs that
  satisfy no one's actual requirements well.
- **Resume-driven architecture**: choosing a technology because it's
  interesting to have used, not because it's the best fit for the problem
  and the team that will operate it.
- **The single point of approval bottleneck**: described fully in Section 15,
  listed here because it is common enough to also count as a named
  anti-pattern rather than only a failure scenario.
- **Big Design Up Front (BDUF) without validation**: producing an
  exhaustive design before any part of it has been prototyped or challenged
  by the team that has to build it, common in centralized-team models
  (Section 7) that lack a feedback loop back to delivery.

## 20. Trade-off Analysis

| Decision | Benefit | Cost |
|---|---|---|
| Centralized architecture team vs. embedded architects | Stronger cross-solution consistency | Slower decisions, higher risk of losing delivery-team context |
| Formal ARB gate vs. lightweight async review | Auditable governance, strong for regulated industries | Higher process overhead, risk of becoming a bottleneck |
| Advisory authority vs. sign-off authority | Preserves delivery-team ownership and buy-in | Decisions can be overridden or ignored without consequence |
| Architect embedded full-time in one product vs. covering several | Deep context, faster trust-building | Weaker enforcement of cross-product consistency |

## 21. Comparison Table

| Role | Primary Scope | Typical Time Horizon | Hands-on Coding | Reports Into |
|---|---|---|---|---|
| Solution Architect | One product/platform/program, cross-team | Weeks to ~2 years | Often, partially | Engineering leadership |
| Enterprise Architect | Whole company/portfolio | 1-5+ years | Rarely | CTO/CIO office |
| Technical/Staff/Principal Engineer | One system or team, deep | Days to ~1 year | Primarily | Engineering management |
| Cloud Architect | Infrastructure/platform across solutions | Months to ~2 years | Often (IaC) | Platform/Infrastructure engineering |
| Security Architect | Security controls across solutions | Ongoing/continuous | Sometimes | Security/CISO office |

## 22. Real-World Case Study

A mid-size fintech scaleup grew from 40 to 220 engineers over two years with
a single centralized Architecture Review Board that had signed off on every
production change since the company's early days. Decision cycle time
(Section 11) grew from under a week to over six weeks, and delivery teams
began quietly shipping smaller changes without going through the board at
all, defeating its purpose while leaving the illusion of governance intact.
The fix, driven by a newly hired Head of Architecture, was not to remove
governance but to re-scope it: the company moved to the federated guild model
(Section 7), embedding one Solution Architect per major product line,
defining a written risk threshold so that only genuinely high-risk changes
(new external data flows, anything touching payment settlement) still
required the full board, and converting everything else to an async
ADR-with-comment-period process. Decision cycle time for routine changes
dropped to days, the board's remaining reviews became meaningfully higher
signal because they were no longer diluted by routine approvals, and
"shadow" unreviewed changes stopped because the lightweight path was now
faster than skipping review altogether.

## 23. Interview Questions

1. Tell me about a time you made an architectural decision that the
   implementing team disagreed with. How did you resolve it, and what would
   you do differently?
2. How do you decide which decisions need a full design review versus which
   ones a team should just make on their own?
3. Describe how you would introduce architectural governance into a team
   that has never had any and is skeptical of the idea.
4. How do you keep your technical judgment credible if you're not writing
   production code full-time anymore?
5. Walk me through the RACI for a recent significant decision you were
   involved in — who was Accountable, and how was that decided?

## 24. Hands-on Exercises

Using the [ADR template](../code/templates/role-chapter/adr-template.md),
write a real ADR for a technical decision you are currently facing (or have
recently made) at work — include at least two genuinely considered
alternatives and the specific evidence (a benchmark, a cost estimate, a prior
incident) that drove the final choice, not just a stated preference.

## 25. Design Exercises

Design the architecture governance model for a 200-engineer product
organization that is growing toward 800 engineers over the next two years and
currently has no formal architecture function at all. Produce: a charter
(scope and authority per Section 9), a RACI matrix for a representative
cross-team decision, and the review-threshold criteria that decide which
decisions require architect involvement. Evaluation criteria: whether the
proposed model scales past 800 engineers without becoming either a bottleneck
or ineffective, and whether the RACI resolves ambiguity rather than
introducing new overlap.

## 26. Architecture Review Questions

Use these to assess the health of an architecture *function* itself, not a
specific system design:

- Is there a written charter defining the Solution Architect's scope and
  authority, and do delivery teams actually know what it says?
- Is there a documented, followed decision-visibility mechanism (ADR log,
  design-doc process, ARB), and is it referenced later, or only written and
  forgotten?
- Is there an explicit, risk-based threshold for which decisions require
  architect involvement, or is that left to ad hoc judgment call each time?
- Is there a feedback loop from production outcomes and delivery-team
  sentiment back into how the architecture function operates?
- Could a new hire explain, within their first month, who has final say on
  a disputed technical decision in their area?

## 27. Summary

A Solution Architect's job is to hold cross-team technical accountability
explicitly — for the decisions themselves, for their documented rationale,
and for how they play out after delivery — so that accountability doesn't
silently fall through the gaps between teams and vocabularies (product,
engineering, security, operations). The role is defined less by a fixed set
of technical skills than by how it is scoped (Section 4), how it operates day
to day (Section 5), and how it is organized within a company (Section 7) —
get those wrong, and even a technically excellent architect will fail in the
ways described in Section 15. This chapter covered the role as a job
function; how to reason through the trade-offs the role is accountable for is
the subject of [Architecture Thinking](CH03_Architecture_Thinking.md), and
what architecture itself fundamentally is, is covered in
[What is Software Architecture?](CH01_What_is_Software_Architecture.md).

**Further reading**: [What is Software Architecture?](CH01_What_is_Software_Architecture.md) ·
[Architecture Thinking](CH03_Architecture_Thinking.md) ·
[Enterprise Architecture](../18_Enterprise_Architecture/PART_OVERVIEW.md) ·
[Architecture Documentation](../21_Architecture_Documentation/PART_OVERVIEW.md) ·
[Soft Skills](../23_Soft_Skills/PART_OVERVIEW.md)
