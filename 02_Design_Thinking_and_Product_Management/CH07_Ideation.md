# Chapter: Ideation

Part: [02 - Design Thinking and Product Management](PART_OVERVIEW.md) - Subsection: Design Thinking - Status: Drafted

## 1. Introduction

Ideation is the disciplined transition from a clearly framed problem to a
broad, testable space of possible solutions. It is the **Ideate** stage of
the design-thinking process introduced in [Empathy](CH01_Empathy.md): after a
team has built evidence about people and context, and after that evidence has
been converted into a bounded design question, Ideation deliberately expands
optionality before any one option is allowed to dominate.

This chapter's scope is specific: it owns ideation technique and facilitation
mechanics. That includes divergence and convergence behavior, idea-generation
method families, candidate-selection funnels, and anti-premature-convergence
practices that keep a room from anchoring on the first plausible solution.
It does not own prototype fidelity, experiment cadence, or prototype
instrumentation in depth (those belong to the forthcoming Rapid Prototyping
chapter), and it does not own screen-structure composition craft (that belongs
to the forthcoming Wireframing chapter). Ideation generates and narrows
solution hypotheses; it does not finalize interface layouts or run validation
experiments itself.

Inputs are consumed, not re-taught:

- [Empathy](CH01_Empathy.md) owns empathy-map construction and stakeholder
  empathy technique.
- [Research](CH02_Research.md) owns research methodology and synthesis.
- [Personas](CH03_Personas.md) owns persona construction and governance.
- [Journey Mapping](CH05_Journey_Mapping.md) owns pain-point sequencing and
  emotional-curve diagnosis.
- [Problem Framing](CH06_Problem_Framing.md) owns Point-of-View (POV)
  statement and How-Might-We (HMW) statement construction.

Ideation starts from those artifacts and asks a different question: given this
specific user, this specific context, and this specific framed opportunity,
what are many materially different ways we could respond, and which few are
worth carrying forward to prototype and test?

For a Solution Architect, Ideation is not a soft prelude to "real" technical
work. It is a risk-management mechanism against architectural lock-in.
Selecting an implementation path before generating alternatives often embeds
irreversible cost structure (integration assumptions, data model choices,
operational burden) before the team has even explored the design space.
Disciplined ideation delays that lock-in just long enough to improve the odds
that the chosen path is both user-valid and technically proportionate.

## 2. Historical Evolution

- **1940s-1950s - Creative problem-solving research**: Alex Osborn's early
  work in advertising formalized group idea generation and popularized the
  term "brainstorming" (not yet the modern workshop discipline, but a first
  explicit attempt to separate idea generation from evaluation).
- **1960s - Divergent/convergent language enters design education**:
  creativity and systems-design literature began naming two distinct cognitive
  modes: generating many options first, then reducing them through criteria.
  This framing became the core control loop of modern facilitation.
- **1970s - Design Methods movement**: practitioners such as Christopher
  Alexander and John Christopher Jones advanced structured design methods,
  pushing design away from pure intuition and toward explicit process,
  including option-generation and option-reduction patterns.
- **1980s - Lateral thinking practice spreads**: Edward de Bono's lateral
  thinking techniques increased mainstream use of deliberate reframing,
  provocation, and analogy as mechanisms for escaping linear, first-answer
  solutioning.
- **1991 - IDEO's multidisciplinary facilitation model**: cross-functional
  ideation sessions became institutionalized in product and service design,
  with explicit facilitator roles, visual externalization, and time-boxed
  exercises as repeatable operating practice.
- **2000s - Service design and co-creation workshops**: ideation expanded
  from designer-only rooms to sessions that included engineers, operators,
  support staff, and business stakeholders, improving implementability and
  reducing handoff rework.
- **2005 onward - Stanford d.school teaching patterns**: methods such as
  "How Might We" prompts, structured brainstorming variants, and sketch-first
  collaborative ideation became widely adopted in engineering organizations.
- **2010s - Lean and Agile integration**: ideation moved from one-time
  upfront events to recurring discovery cadences, with smaller sessions tied
  to evolving evidence and delivery constraints.
- **2020s - Remote-first facilitation and asynchronous ideation**: distributed
  teams normalized digital whiteboards, asynchronous brainwriting, and
  pre-read problem framing to preserve divergence quality across time zones.
- **2020s - Artificial Intelligence (AI)-assisted expansion**: language-model
  tools began supporting prompt-driven idea expansion and clustering. Mature
  teams treat these tools as augmentation for breadth, while retaining human
  judgment for relevance, ethics, and viability filtering.

## 3. Why It Exists

Ideation exists because the default behavior of most delivery teams under time
pressure is premature convergence: hear one pain point, propose one solution,
and begin implementation. That behavior is efficient only when the first
solution is already near-optimal, which is uncommon in ambiguous or
cross-functional problem spaces.

Several failure modes motivate a distinct Ideation stage:

- **Anchoring on first plausible ideas**: the earliest suggestion in a room
  sets a reference point that subsequent discussion clusters around,
  especially when proposed by a senior participant.
- **Functional fixedness**: teams reuse known mechanisms from their current
  architecture even when the framed problem might be better solved by a
  different interaction model or service boundary.
- **Local optimization**: each function proposes options that are easy inside
  its own constraints, producing a globally weak outcome across user value,
  technical sustainability, and business viability.
- **Invisible option cost**: if alternatives are never generated, decision
  makers cannot compare trade-offs; they can only justify the path already
  selected.

Ideation creates intentional option volume and option diversity before
selection. It is not volume for its own sake. The objective is to raise the
probability that at least one candidate in the explored set achieves a better
trade-off profile than the team's default first answer.

## 4. Core Concepts

### 4.1 Recap: Define-stage outputs as Ideation inputs

A short recap, not re-teaching: [Problem Framing](CH06_Problem_Framing.md)
owns how POV and HMW statements are built. Ideation consumes those outputs as
its session boundary. A high-quality ideation session starts with one explicit
framed prompt and explicit non-goals; otherwise the room diverges into loosely
related topics and produces ideas that cannot later be evaluated against a
shared question.

In practice, this means ideation quality is mostly decided before the workshop
starts. If the input HMW is vague (for example, "How might we improve
onboarding?"), teams tend to generate ideas at incompatible scales: some ideas
target a single field label, others propose an account-model rewrite. A tighter
prompt (for example, "How might we reduce first-time admin setup drop-off in
the first 10 minutes without adding manual support?") constrains idea scale,
keeps options comparable, and improves convergence quality.

One useful pre-session check is to force every stakeholder to restate the
problem in one sentence. If three people produce three different problem
statements, the team is not ready for ideation yet and should return to Problem
Framing first.

### 4.2 Divergent and convergent thinking as separate operating modes

Ideation alternates between two modes that must be operationally separated:

- **Divergence**: maximize quantity and diversity of plausible responses
  without judging them yet.
- **Convergence**: apply explicit criteria to reduce the option set.

Mixing these modes in the same minute (for example, criticizing each idea as
soon as it appears) collapses divergence quality. The practical implication:
facilitators should time-box divergence and block evaluation language until the
convergence phase starts.

The reason this separation works is cognitive, not procedural. Divergence asks
for expansive associative thinking, while convergence asks for analytical
comparison against constraints. Human groups switch poorly between those modes
in rapid alternation; evaluation comments in a divergence window do not just
evaluate one idea, they reduce risk-taking for all subsequent ideas.

A reliable operating pattern is:

1. Divergence window with no ranking vocabulary allowed.
2. Clustering pass that groups similar ideas without judging value.
3. Convergence pass with explicit criteria and explicit decision ownership.

Without this order, teams often believe they "brainstormed broadly" while
actually selecting the earliest politically safe option.

### 4.3 Idea quality dimensions

In this chapter, convergence evaluates ideas across four dimensions:

- **Desirability**: does this solve the target persona's problem in a way they
  would actually adopt?
- **Feasibility**: can we implement and operate this with available
  capabilities and constraints?
- **Viability**: does this support business outcomes and policy constraints?
- **Differentiation**: does this create meaningful improvement versus current
  state and obvious alternatives?

These dimensions are intentionally pre-prioritization. They are not a roadmap
framework such as Reach-Impact-Confidence-Effort (RICE) or MoSCoW
(Must-Should-Could-Won't), which belong to Product Management chapters later
in this part.

The key discipline is to evaluate each idea across all four dimensions before
arguing for a favorite. Teams naturally overweight feasibility because
feasibility arguments are easiest to articulate early; this can hide weak
desirability and create efficient delivery of low-value features. Conversely,
teams that overweight desirability can produce compelling concepts with
non-viable operational cost.

A practical scoring artifact is a short decision card per idea:

- one sentence of user value (desirability)
- primary implementation constraint (feasibility)
- expected business effect and measurement signal (viability)
- reason this is meaningfully different from baseline (differentiation)

If any field cannot be filled with specific language, the idea is not yet
mature enough to enter the selection funnel.

### 4.4 Ideation method families

Methods differ by the cognitive move they induce:

- **Association methods**: free brainstorming, round-robin, lightning rounds.
- **Constraint methods**: "what if we had half the budget," "no new backend
  services," "mobile-only," forcing novel recombination.
- **Inversion methods**: "worst possible idea" then reverse extraction of
  design principles.
- **Analogy methods**: transfer structures from other domains (air-traffic
  control, emergency medicine, logistics) to surface non-obvious patterns.
- **Morphological methods**: decompose the problem into dimensions and combine
  alternatives per dimension.
- **Visual rapid ideation methods**: sketch-based bursts such as Crazy 8s for
  option multiplicity, while leaving fidelity decisions to Rapid Prototyping
  and Wireframing chapters.

Method choice should match uncertainty type. If uncertainty is "we have too
few solution directions," association and analogy methods are most useful. If
uncertainty is "we have too many obvious but similar options," inversion and
constraint methods create structural variation. Morphological methods are most
useful when the problem can be decomposed into stable dimensions (for example,
auth method, data visibility mode, exception-handling strategy) that can be
recombined.

Teams often run one familiar technique repeatedly and conclude ideation is
low-value. The issue is usually not ideation itself but method monotony. Rotating
method families across sessions increases option diversity and reduces process
fatigue.

### 4.5 Selection funnel mechanics

A robust convergence sequence usually has three filters:

1. **Signal filter**: remove duplicates and ideas outside scope.
2. **Criteria filter**: score candidates against shared dimensions.
3. **Portfolio filter**: ensure the selected set is not monoculture (for
   example, all low-risk incremental options).

The output is typically a small portfolio, not one "winner":

- one near-term, low-risk candidate,
- one medium-complexity candidate,
- one higher-uncertainty but higher-upside candidate.

This preserves optionality into prototyping without overloading downstream
execution.

The portfolio step is critical and often skipped. When teams choose only one
idea at this stage, they tend to select the least controversial option rather
than the best learning option. Carrying a deliberate portfolio into Rapid
Prototyping gives teams parallel learning paths: one low-risk baseline, one
challenger that could materially outperform baseline, and one strategic bet
that might fail quickly but cheaply.

Selection should also log why high-scoring ideas were not selected. This makes
later revisit decisions explicit when constraints change, instead of forcing
the team to rediscover prior reasoning from memory.

### 4.6 Anti-premature-convergence controls

Facilitation controls that materially improve outcome quality:

- Silent idea generation before group discussion (reduces dominance effects).
- Equalized turn-taking during first share-out round.
- Explicit "no evaluation" language in divergence windows.
- Deferred naming of favorites until criteria are agreed.
- Separate sponsor-review gate after first convergence to prevent authority
  override during generation.

These controls work only when enforced as explicit rules, not suggestions. A
facilitator should treat violations (for example, senior participant evaluating
ideas during divergence) as process defects and reset the phase. If the team
cannot enforce phase purity, output quality degrades regardless of individual
talent.

In distributed sessions, process controls need tool support: simultaneous
silent entry periods, delayed reveal, and anonymous first-pass clustering can
reduce hierarchy effects that are stronger in remote settings.

### 4.7 Cognitive biases specific to ideation rooms

A facilitator should actively monitor and counter:

- **Anchoring bias**: first idea becomes gravitational center.
- **Authority bias**: senior voices compress alternative exploration.
- **Groupthink**: harmony pressure suppresses dissenting options.
- **Availability bias**: recent incidents over-influence option generation.
- **Novelty bias**: unusual ideas are overvalued despite weak fit.
- **Feasibility tunnel vision**: engineering constraints dominate before user
  value is explored.

Bias control is most effective when instrumented, not merely discussed. Useful
instrumentation includes:

- idea-origin tracking (how many options came from each participant role)
- evaluation-sequence tracking (which criteria dominated first-pass filtering)
- dissent-capture prompts (one required counter-argument per shortlisted idea)

This creates an auditable record of how options were narrowed and helps teams
spot recurring structural bias patterns over multiple sessions.

### 4.8 Idea articulation granularity

Ideas should be recorded at a consistent abstraction level. Over-abstract
entries ("make it easier") are not evaluable; over-specified entries
("add button X to panel Y") can lock teams into implementation detail too
early. A useful pattern is:

- one-sentence concept,
- target persona/context,
- expected user outcome,
- primary mechanism,
- key risk or assumption.

Granularity discipline matters because downstream teams inherit whatever level
of ambiguity ideation produces. If ideas are too abstract, Rapid Prototyping
must spend cycles translating intent. If ideas are too implementation-heavy,
teams lock into architecture before validating value.

A useful calibration test is interchangeability: replace one noun in the idea
statement (for example, "dashboard" to "report page") and see whether meaning
changes. If meaning does not change, the statement is too abstract. If the
statement already names internal classes, schemas, or vendor products, it is
usually too concrete for ideation stage output.

## 5. Internal Working

A production-quality ideation cycle follows a repeatable sequence:

1. **Frame intake**: facilitator validates the problem prompt, persona, and
   evidence pack from prior chapters.
2. **Session architecture**: choose method mix based on uncertainty type
   (behavioral ambiguity, workflow ambiguity, technical ambiguity).
3. **Divergence round 1**: silent individual generation.
4. **Divergence round 2**: combinational or analogical expansion from round-1
   seeds.
5. **Clustering**: merge near-duplicates; retain distinct mechanisms.
6. **Criteria declaration**: agree evaluation dimensions before seeing scores.
7. **Convergence pass**: independent scoring, then facilitated discussion.
8. **Portfolio selection**: select a balanced candidate set.
9. **Risk annotation**: capture assumptions and failure conditions per
   selected idea.
10. **Handoff package**: package selected ideas for downstream prototyping.

The key invariant is phase purity: no criteria scoring until divergence closes.

## 6. Design Principles

- **Evidence before imagination**: ideas should respond to documented user
  evidence, not detached inspiration.
- **Quantity creates quality probability**: minimum idea-count thresholds are a
  control against first-answer lock-in.
- **Diversity over redundancy**: ten variants of one mechanism are less useful
  than five distinct mechanisms.
- **Mechanism clarity**: each candidate should express how it creates value,
  not only what it looks like.
- **Bias-aware facilitation**: process should compensate for predictable human
  bias rather than assuming neutrality.
- **Explicit non-goals**: convergence quality improves when out-of-scope
  classes are named in advance.
- **Reversibility preference**: when uncertainty is high, favor ideas that can
  be tested and reversed cheaply in the next stage.

## 7. Architecture Patterns

Ideation operations usually adopt one of these organizational patterns:

- **Central facilitated lab**: a specialist facilitation team runs ideation
  for many squads. Benefit: process consistency. Cost: scheduling bottlenecks.
- **Embedded facilitator model**: each product trio includes ideation
  capability. Benefit: context proximity and speed. Cost: method variance.
- **Hub-and-spoke model**: central standards and coaching with embedded
  session ownership in squads. Benefit: scale with governance.
- **Asynchronous-first distributed model**: structured pre-work and
  time-windowed idea boards for multi-time-zone teams. Benefit: participation
  breadth. Cost: weaker real-time synthesis unless carefully orchestrated.

For most mid-size organizations, hub-and-spoke is a practical default because
it balances rigor with delivery velocity.

## 8. Production Architecture

Treat ideation as a capability with artifacts, not a one-off workshop:

- **Inputs repository**: linked problem frames, personas, journey-map slices,
  and research citations.
- **Session records**: method used, participant mix, raw idea set, clustering
  outputs, scoring sheets, selected portfolio.
- **Decision lineage**: trace from framed problem to selected hypotheses.
- **Governance metadata**: owner, date, confidence level, known assumptions,
  planned validation path.

A lightweight repository structure might include:

- `/ideation/inputs/<topic>/`
- `/ideation/sessions/<date>-<topic>/`
- `/ideation/portfolio/<topic>/`
- `/ideation/archive/`

This structure supports auditable progression into prototyping and testing.

## 9. Implementation

A practical rollout plan for a team without a mature ideation practice:

1. **Define the standard workshop contract**
   Duration, participant roles, minimum input artifacts, and expected outputs.
2. **Create facilitation playbooks**
   Two or three method recipes for common problem shapes (workflow friction,
   trust/compliance friction, operational handoff friction).
3. **Train cross-functional facilitators**
   Product manager, designer, and engineer each run sessions with peer review.
4. **Instrument basic quality metrics**
   Option count, option diversity, selection rationale completeness,
   downstream carry-through to prototyping.
5. **Run a 6-week pilot across multiple problem types**
   Compare ideation outputs and downstream outcomes against prior baseline.
6. **Institutionalize repository and review cadence**
   Monthly quality review of selected sessions; method adjustments based on
   observed failure modes.

## 10. Complete Code Examples

This chapter's reusable assets are templates and small utilities:

- [code/templates/ideation-chapter/ideation-session-canvas.md](../code/templates/ideation-chapter/ideation-session-canvas.md)
  session setup template: prompt, constraints, participant roles, method plan.
- [code/templates/ideation-chapter/idea-capture-sheet.md](../code/templates/ideation-chapter/idea-capture-sheet.md)
  normalized idea format for comparable evaluation.
- [code/json/ideation-chapter/selection-rubric.schema.json](../code/json/ideation-chapter/selection-rubric.schema.json)
  schema for desirability/feasibility/viability/differentiation scoring.
- [code/python/ideation-chapter/cluster_and_score.py](../code/python/ideation-chapter/cluster_and_score.py)
  lightweight script to deduplicate similar idea statements and compute
  aggregate scores with confidence flags.
- [code/node/ideation-chapter/idea-portfolio-report.js](../code/node/ideation-chapter/idea-portfolio-report.js)
  generates a markdown report with selected portfolio and risk annotations.

## 11. Performance

Ideation performance is not "number of sticky notes." Useful performance
indicators include:

- **Option throughput**: count of non-duplicate candidates per session hour.
- **Diversity index**: degree of mechanism variation in candidate set.
- **Decision latency**: time from framed prompt to selected portfolio.
- **Downstream survival rate**: percent of selected ideas that remain viable
  through first prototype review.
- **Rework rate**: frequency of returning to ideation because options were
  under-explored.

A fast session with low diversity can be slower overall once downstream rework
is counted.

## 12. Scalability

As ideation scales across squads, common breakdowns appear:

- inconsistent facilitation quality,
- prompt ambiguity from weak framing handoffs,
- repository entropy (artifacts not searchable),
- repeated rediscovery of already-explored options.

Scaling controls:

- shared method library with context cues,
- facilitator calibration sessions using recorded outputs,
- canonical artifact schema,
- reusable idea-pattern catalog with anti-copy warning (adapt, do not clone).

Remote and global teams often need asynchronous divergence windows (24-48
hours) plus a shorter synchronous convergence session.

## 13. Security

Ideation artifacts can contain sensitive data and strategic intent:

- user evidence snippets may include personally identifiable information
  (PII),
- ideas may expose unreleased strategy,
- constraints may include compliance or legal interpretations.

Required controls:

- role-based access to session repositories,
- redaction standards for participant quotes,
- explicit data-retention policy for raw workshop boards,
- audit log for who accessed or exported ideation packages.

When ideation includes regulated domains (healthcare, finance, public sector),
compliance review should occur before artifacts are shared outside the core
team.

## 14. Observability

Ideation quality can be observed with lightweight telemetry:

- **Convergence ratio**: selected ideas divided by total distinct ideas.
- **Source traceability**: percentage of selected ideas linked to specific
  evidence inputs.
- **Bias signals**: speaking-time skew, early-suggestion adoption rate,
  authority-origin concentration.
- **Portfolio balance**: distribution of low/medium/high uncertainty options.
- **Outcome linkage**: proportion of selected ideas that receive explicit
  prototype/test outcomes later.

A mature practice treats these as process health signals, not individual
performance scores.

## 15. Failure Scenarios

- **Premature convergence at minute ten**: team agrees on one familiar
  mechanism before divergent exploration; later testing reveals hidden user
  constraints that alternate ideas would have handled.
- **Loudest-voice capture**: high-status participant shapes idea set despite
  weak evidence fit.
- **Method mismatch**: using free brainstorming for a tightly constrained
  compliance problem where morphological decomposition would perform better.
- **Novelty theater**: selecting surprising ideas without feasibility
  grounding, then abandoning them during prototyping.
- **Artifact loss**: no traceable session output; team cannot explain why
  option A was chosen over B.
- **Scope drift**: session shifts from framed problem to adjacent strategic
  debates, producing non-actionable output.

## 16. Testing

Testing in this chapter means validating ideation process quality, not user
prototype outcomes (owned by later chapters):

- **Facilitation dry-runs**: rehearsal with internal participants to detect
  unclear prompts and timing failures.
- **Rubric reliability checks**: two independent scorers evaluate sample ideas;
  low agreement indicates ambiguous criteria.
- **Method A/B trials**: compare method mixes on similar prompts to determine
  which yields better diversity and downstream survival.
- **Retrospective audits**: periodically inspect closed sessions and verify
  whether selected ideas were traceable, balanced, and hypothesis-ready.

## 17. Common Mistakes

- Treating ideation as unstructured discussion rather than an engineered
  process.
- Entering sessions without a crisp framed prompt and non-goals.
- Allowing evaluation language during divergence.
- Mistaking quantity for diversity.
- Converging to a single winner too early.
- Handing off selected ideas without explicit assumptions and risks.
- Confusing ideation outputs with finished product designs.

## 18. Best Practices

- Start each session with a one-slide recap of persona, journey pain point,
  and HMW prompt.
- Use silent generation first to increase inclusion quality.
- Require a minimum number of distinct mechanisms before convergence begins.
- Separate facilitator and decision sponsor roles when possible.
- Use independent pre-discussion scoring to reduce herd effects.
- Select a small portfolio of candidates, not only one.
- Capture rationale and assumptions in a durable repository.
- Schedule immediate downstream handoff to prototyping while context is fresh.

## 19. Anti-Patterns

- **Brainstorming theater**: energetic workshop with no selection rigor and no
  traceable outcomes.
- **Idea beauty contest**: selecting based on presentation polish rather than
  evidence fit.
- **Constraint denial**: ignoring technical, legal, or operational boundaries
  until late-stage failure.
- **Constraint tyranny**: letting current architecture block exploration before
  user value options are generated.
- **Monoculture portfolio**: selecting only low-risk incremental ideas,
  eliminating upside learning.
- **Authority pre-vote**: sponsor signals preference before scoring, collapsing
  independent judgment.

## 20. Trade-off Analysis

| Decision | Benefit | Cost |
|---|---|---|
| Broad divergence window vs. short divergence window | Higher option diversity and lower anchoring risk | More facilitation time and higher synthesis effort |
| Synchronous workshop vs. asynchronous-first ideation | Faster real-time momentum and clarification | Time-zone exclusion risk; dominance bias risk |
| Anonymous silent generation vs. open verbal generation | Better inclusion and reduced authority bias | Less spontaneous combinational riffing |
| Single-idea selection vs. portfolio selection | Simpler planning and resource focus | Higher risk of missing better alternatives |
| Strict feasibility gate early vs. delayed feasibility gate | Reduces downstream dead ends | Can suppress high-upside concepts too early |

## 21. Comparison Table

| Artifact / Technique | Primary Purpose | Typical Output | Owning Chapter |
|---|---|---|---|
| Point-of-View (POV) statement | Define user, need, and insight in a bounded frame | Structured statement | [Problem Framing](CH06_Problem_Framing.md) |
| How-Might-We (HMW) statement | Convert framed problem into generative prompt | Question prompt set | [Problem Framing](CH06_Problem_Framing.md) |
| Ideation session (divergence/convergence) | Generate and narrow multiple solution hypotheses | Candidate portfolio with rationale | This chapter |
| Rapid prototype | Make selected hypotheses testable quickly | Low-to-medium fidelity artifact and test plan | [Rapid Prototyping](CH08_Rapid_Prototyping.md) |
| Wireframe | Define structural screen composition and flow details | Interface skeletons and navigation structure | [Wireframing](CH09_Wireframing.md) |
| Prioritization framework (for roadmap) | Sequence validated opportunities for delivery investment | Ranked backlog or roadmap decision | [PART_OVERVIEW.md](PART_OVERVIEW.md) (Product Management, not yet drafted) |

## 22. Real-World Case Study

A business-to-business (B2B) Software as a Service (SaaS) operations platform
faced chronic onboarding abandonment in enterprise accounts. Prior work had
already produced clear inputs: personas from account-admin and operator roles,
a current-state journey map showing a sharp emotional low during initial
integration setup, and a Problem Framing output centered on an HMW prompt:
"How might we reduce first-week integration anxiety for account admins without
increasing long-term operational burden?"

The team's first instinct was a familiar solution: add more setup wizard steps
and inline help text. Instead, they ran a structured ideation cycle with three
controls: silent brainwriting first, forced method shift (analogy plus
inversion after initial round), and portfolio-based convergence rather than a
single winner.

Divergence produced 64 raw ideas, clustered to 19 distinct mechanisms. After
criteria scoring and risk annotation, the selected portfolio included:

- an incremental candidate: progressive disclosure in setup,
- a medium candidate: guided "import known-good configuration" templates,
- a high-uncertainty candidate: operator-sandbox "safe failure" mode that
  simulates integration errors before production activation.

The high-uncertainty candidate had not appeared in the first ten minutes and
would have been missed under premature convergence. In downstream work, that
candidate produced the largest reduction in support escalations during week one
and improved activation completion for complex accounts. The lesson was not
that one method is always superior; it was that anti-convergence facilitation
created the conditions for materially different options to surface before
selection pressure narrowed the set.

## 23. Interview Questions

1. Why must divergence and convergence be operationally separated in a strong
   ideation process?
2. How would you detect that a session was captured by authority bias even if
   everyone reports the workshop "felt collaborative"?
3. Explain the difference between an ideation selection funnel and a Product
   Management prioritization framework.
4. What is a practical way to prevent a team from selecting only low-risk,
   incremental options?
5. How would you design ideation mechanics differently for a regulated-domain
   problem versus a consumer-interface friction problem?
6. Which ideation anti-pattern most often causes downstream prototype rework,
   and why?

## 24. Hands-on Exercises

Take one completed problem frame from [Problem Framing](CH06_Problem_Framing.md)
and run a 90-minute ideation session with at least four participants across
product, design, and engineering.

Deliverables:

- framed prompt and non-goals,
- raw idea set,
- clustered distinct mechanisms,
- scored selection sheet,
- three-idea portfolio with assumptions and key risks.

Success criteria:

- at least 15 distinct mechanisms after deduplication,
- explicit evidence link for each selected idea,
- at least one selected idea categorized as medium or high uncertainty.

## 25. Design Exercises

Design an ideation operating model for a 12-squad organization where discovery
quality is inconsistent and teams frequently jump from journey-map findings
directly into implementation.

Your design should include:

- facilitation topology (centralized, embedded, or hub-and-spoke) and why,
- minimum artifact contract for every ideation session,
- anti-bias controls that can be audited,
- portfolio-selection rule,
- repository structure and observability metrics.

Evaluation focus: whether the model can improve option diversity without
slowing decision velocity beyond acceptable delivery limits.

## 26. Architecture Review Questions

Use these questions to review the health of ideation practice:

- Is every ideation session anchored to a documented frame (persona, evidence,
  HMW prompt, non-goals)?
- Are divergence and convergence phases explicitly separated in facilitation?
- Does the selected set preserve option diversity or collapse into one class
  of ideas?
- Are selection criteria declared before scoring starts?
- Can the team trace each selected idea back to specific evidence?
- Are key assumptions and failure conditions documented for downstream work?
- Is there measurable bias skew in participation or selection origin?
- Do ideation outputs reliably transition into prototyping and testing rather
  than stalling as workshop artifacts?

## 27. Summary

Ideation is the deliberate engine between problem framing and prototyping: it
expands and then narrows the solution space using explicit facilitation
mechanics rather than intuition alone. Its core value is not creativity
performance in isolation; it is reducing premature lock-in by generating
materially different options, evaluating them through shared criteria, and
handing forward a balanced portfolio of hypothesis-ready candidates.

This chapter owns that mechanics layer: divergence/convergence behavior,
method-family selection, candidate funnels, and anti-premature-convergence
controls. It consumes framed prompts and user evidence from
[Empathy](CH01_Empathy.md), [Research](CH02_Research.md),
[Personas](CH03_Personas.md), [Journey Mapping](CH05_Journey_Mapping.md), and
[Problem Framing](CH06_Problem_Framing.md), and then passes selected ideas to
Rapid Prototyping and Wireframing for materialization and structural design.

**Further reading**: [Empathy](CH01_Empathy.md) -
[Research](CH02_Research.md) - [Personas](CH03_Personas.md) -
[User Interviews](CH04_User_Interviews.md) -
[Journey Mapping](CH05_Journey_Mapping.md) -
[Problem Framing](CH06_Problem_Framing.md) -
[PART_OVERVIEW.md](PART_OVERVIEW.md) (Rapid Prototyping, Wireframing, and
Product Management prioritization chapters not yet drafted).
