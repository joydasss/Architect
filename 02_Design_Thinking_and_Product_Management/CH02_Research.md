# Chapter: Research

Part: [02 — Design Thinking and Product Management](PART_OVERVIEW.md) · Status: Drafted

## 1. Introduction

Every architecture decision in this handbook rests on an unstated
assumption: that someone correctly understood what problem was worth
solving in the first place. Research is the discipline that earns that
assumption instead of hoping it happens to be true. It is the set of
methods a product team uses to replace opinion, hierarchy, and internal
consensus with evidence gathered from the people who will actually use — or
refuse to use — what gets built.

This chapter is chapter two of Part 02 — Design Thinking and Product
Management, sitting between [Empathy](CH01_Empathy.md), which builds the
mindset and ethical stance of taking users seriously as people rather than
requirements sources, and [Personas](CH03_Personas.md), which takes the raw
material research produces and compresses it into a usable design artifact.
This chapter's job is narrower than either: it covers **research
methodology** — how a team decides what to find out, which method will
actually answer that question, how to run the study without contaminating
its own results, and how to turn a pile of transcripts, survey responses, or
usage logs into a small number of defensible findings. It deliberately does
**not** teach the mechanics of running a single one-on-one interview
(question wording, rapport-building, moderation technique) in depth — that
is owned by the forthcoming [User Interviews](CH04_User_Interviews.md)
chapter, since interviewing deserves its own focused treatment as the single
most commonly used generative method. It also does not teach how to
construct a persona once research is synthesized — that is owned by
[Personas](CH03_Personas.md). What this chapter owns is everything upstream
and downstream of any single method: the taxonomy of research types,
choosing the right method for a given question, planning and recruiting for
a study, running it without bias, synthesizing raw data into findings, and
operating research as a repeatable capability inside a product organization
rather than a one-off event.

For the Solution Architect audience of this handbook specifically: research
is the mechanism that turns a business stakeholder's assertion ("users want
a dashboard") into an Architecturally Significant Requirement (ASR) you can
actually design against — see [What is Software
Architecture? § Core Concepts](../01_Architecture_Mindset/CH01_What_is_Software_Architecture.md#4-core-concepts)
for the ASR concept itself. An architecture that is technically excellent
but built against an unvalidated assumption about what users need is not a
successful architecture — it is an expensive, well-engineered mistake. An
architect who understands research methodology can tell the difference
between "three customers mentioned this in passing" and "we ran a study
designed to detect this pattern and it held across a representative sample"
— and can push back on requirements accordingly, the same way they would
push back on an unvalidated performance or security assumption.

## 2. Historical Evolution

User research did not originate in software; it was assembled from several
older disciplines, each contributing a different piece of the toolkit this
chapter describes.

- **1920s-30s — market research and the survey.** Commercial market
  research (Nielsen's founding in 1923, George Gallup's polling
  methodology in the 1930s) established the statistical apparatus of
  sampling, questionnaire design, and representativeness that quantitative
  user research still borrows from directly.
- **1940s-50s — human factors and ergonomics.** World War II cockpit and
  equipment design failures drove the founding of human factors engineering
  — the first discipline to systematically observe how real humans
  interacted with a designed artifact, rather than assuming a rational,
  idealized operator.
- **1970s-80s — ethnography enters the corporation.** Xerox PARC (Palo
  Alto Research Center) hired anthropologists (notably Lucy Suchman) to
  study how office workers actually used photocopiers and documents in
  their natural work context, rather than in a lab. This was the first
  large-scale corporate application of **contextual, observational**
  research to product design, and it is the direct ancestor of what this
  chapter calls generative research.
- **1990s — usability engineering formalizes evaluative research.** Jakob
  Nielsen and Rolf Molich's usability heuristics (1990) and Nielsen's
  discount usability engineering movement made structured usability
  testing cheap and routine rather than an academic exercise, popularizing
  the small-sample qualitative testing practice this chapter revisits in
  Section 4.5.
- **1991 — IDEO founded; 2005 — the Stanford d.school formalizes design
  thinking's teaching model.** IDEO's human-centered design practice and the
  Stanford d.school's five-stage Empathize-Define-Ideate-Prototype-Test
  model (the process this whole part of the handbook is organized around —
  see [Empathy](CH01_Empathy.md)) packaged ethnographic fieldwork,
  synthesis, and rapid iteration into what's now called "design thinking."
  A related but distinct model, the UK Design Council's 2005 "Double
  Diamond" (Discover, Define, Develop, Deliver), covers similar ground with
  a different stage grouping; this chapter and its siblings use the
  Stanford five-stage framing as their organizing spine, not the Double
  Diamond. Research became the formalized "Empathize" and early "Define"
  work of that process.
- **2001 — the Nielsen Norman Group's research methods landscape.** Christian
  Rohrer's later 2014/2022 NN/g (Nielsen Norman Group) article formalized
  the attitudinal/behavioral × qualitative/quantitative framing this chapter
  uses in Section 4.3 as the standard way to map the entire methods
  landscape onto one comparable grid.
- **2011 — Lean Startup and the build-measure-learn loop.** Eric Ries's
  *The Lean Startup* imported the scientific method's hypothesis-testing
  discipline into product development, reframing research as continuous
  falsification of assumptions rather than an up-front phase that happens
  once before "real work" begins.
- **2013 — Lean UX.** Jeff Gothelf and Josh Seiden's *Lean UX* fused Lean
  Startup's validated-learning loop with design thinking's qualitative
  methods, popularizing lightweight, continuous research embedded directly
  in Agile delivery cycles rather than run as a separate up-front phase —
  the organizational pattern this chapter returns to in Section 7 as dual-
  track agile.
- **2015-2018 — the rise of ResearchOps.** As research scaled beyond a
  handful of practitioners per company, a distinct operational discipline
  emerged — the ResearchOps Community was founded in 2018 — covering
  recruiting logistics, consent and data governance, tooling, and shared
  insight repositories (Section 7), treating research infrastructure as a
  first-class investment rather than each researcher improvising their own.
- **2020s — remote-first research and AI-assisted synthesis.** The
  pandemic-era shift to remote moderated sessions (via video conferencing)
  and unmoderated remote testing platforms removed geography as a
  recruiting constraint; more recently, large language model-assisted
  transcription and thematic coding have sharply cut the time cost of
  synthesis (Section 5), though the judgment calls about what a theme
  *means* remain a human responsibility, not an automatable one.

## 3. Why It Exists

Research exists because building the wrong thing well is one of the most
expensive and most common failure modes in software product development,
and because human intuition about what other people want is systematically
unreliable in specific, well-documented ways.

- **The build-the-wrong-thing cost curve.** Architecture has its own
  cost-of-change curve — a wrong structural decision compounds the longer
  it goes uncaught (see [What is Software
  Architecture? § Why It Exists](../01_Architecture_Mindset/CH01_What_is_Software_Architecture.md#3-why-it-exists)).
  Research addresses the layer above that: a *perfectly well-architected*
  system built to solve a problem users don't actually have is a total
  loss, not a partial one — there is no refactor that recovers the cost of
  building the wrong feature. Discovering that a feature solves nothing
  before writing the first line of production code is categorically
  cheaper than discovering it after a launch, a marketing push, and a
  support team trained on it.
- **The say-do gap.** Decades of behavioral research (and the entire
  discipline of behavioral economics) show that what people say they will
  do and what they actually do under real conditions frequently diverge —
  people overstate their willingness to pay, their interest in features
  that sound good in the abstract, and their tolerance for friction they
  will not actually accept in practice. A research methodology exists
  specifically to structure around this gap: attitudinal methods (Section
  4.3) capture what people say; behavioral methods capture what people
  actually do; neither alone is trustworthy, which is why triangulation
  (Section 4.6) is a design principle, not an optional nicety.
- **Systematic cognitive bias inside the building.** Confirmation bias,
  the false-consensus effect (assuming others share your own preferences
  and mental models), and the "HiPPO" (Highest Paid Person's Opinion)
  phenomenon all push internal stakeholders toward decisions that feel
  obviously correct from inside the company and are frequently wrong from
  outside it. Structured research is the mechanism a team uses to
  deliberately expose its own assumptions to falsification by an external,
  representative source of evidence, rather than by internal debate alone.
- **Different questions require categorically different evidence.**
  "Should we build this at all" (a generative question) and "does this
  specific screen work" (an evaluative question) cannot be answered by the
  same method, and answering the wrong type of question with the wrong
  type of method is a leading cause of research that produces confident,
  wrong conclusions (Section 15). A large part of what research methodology
  teaches is matching the method to the question, not defaulting to
  whichever method the team already knows how to run.

## 4. Core Concepts

### 4.1 Generative vs. evaluative research

This is the single most important distinction in the field, and the axis
every other decision in this chapter hangs off of.

- **Generative research** (also called exploratory or discovery research)
  is run *before* a solution exists, to understand a problem space: who the
  users are, what they are actually trying to accomplish, what currently
  gets in their way, and what workarounds they have already invented.
  Generative research produces raw material — observations, quotes, usage
  patterns — that later gets synthesized into personas
  ([Personas](CH03_Personas.md)), journey maps, and problem statements
  (owned by chapters later in this part). It answers "what should we build,
  and for whom," not "does the thing we built work."
- **Evaluative research** is run *against* something that already exists —
  a prototype, a wireframe, a live feature, a competitor's product — to
  measure whether it achieves its intended effect: can users complete the
  task, do they understand the interface, does the feature move a metric.
  It answers "does this work," not "should this exist."
- The two are not a one-time sequence; in a healthy continuous-discovery
  process (Section 7) a team runs both in parallel indefinitely — generative
  research keeps feeding the backlog with new problems worth solving while
  evaluative research keeps validating whether solutions to already-known
  problems actually land.
- A common and costly confusion: running an evaluative method (a usability
  test on a prototype) to answer a generative question ("should we build
  this at all"), which only tests whether the interface is operable, not
  whether the underlying idea has any demand — or the reverse, running
  open-ended generative interviews to "validate" a specific screen design,
  which produces opinions about a mock-up rather than evidence about
  real-world behavior.

### 4.2 Qualitative vs. quantitative research

The second axis is about the *shape* of the data collected, independent of
whether the research is generative or evaluative.

- **Qualitative research** produces rich, non-numeric data — words,
  observed behaviors, screen recordings, artifacts — from a small number of
  participants (commonly single digits to a few dozen). It answers *why*
  and *how*: why a user abandoned a checkout flow, how they reason about a
  pricing page. Its strength is depth and explanatory power; its weakness
  is that small samples cannot support claims about prevalence ("how many
  users experience this") without additional quantitative confirmation.
- **Quantitative research** produces numeric data — survey responses,
  analytics events, A/B test conversion rates — from a large enough sample
  to support statistical claims. It answers *how many* and *how much*: what
  percentage of users hit a given error, which of two designs converts
  better. Its strength is generalizability and statistical confidence; its
  weakness is that it tells you *what* is happening in aggregate but rarely
  *why* any individual user behaves the way they do.
- Neither is inherently "more rigorous" than the other — they answer
  different classes of question, and treating quantitative data as
  automatically more objective is itself a bias: a beautifully powered
  survey built on badly worded, leading questions (Section 6) produces
  precise, confidently wrong numbers.
- **Primary vs. secondary research** is an orthogonal, simpler distinction
  worth naming here: primary research is data your own team collects
  directly (interviews, surveys, usability tests you run); secondary
  research is synthesizing data someone else already collected (published
  industry studies, competitor teardown analyses, prior internal research
  reports, analyst reports). Secondary research is cheap and fast and
  should usually happen first to avoid re-discovering already-published
  findings, but it cannot answer questions specific to your own product and
  user base.

### 4.3 The research methods landscape (attitudinal/behavioral × qualitative/quantitative)

The two axes above combine into a four-quadrant map (the standard framing
popularized by the Nielsen Norman Group) that is worth internalizing well
enough to place any method on it without looking it up — see the diagram at
[diagrams/matrix/research-methods-quadrant.md](../diagrams/matrix/research-methods-quadrant.md).
A third useful axis crosses both of the above: **attitudinal** methods
capture what people *say* (opinions, preferences, self-reported behavior);
**behavioral** methods capture what people *do* (observed actions, real
usage). Placing common methods on this combined grid:

| | Qualitative | Quantitative |
|---|---|---|
| **Attitudinal** | Generative interviews, contextual inquiry (recap: interviewing technique owned by [User Interviews](CH04_User_Interviews.md)) | Attitude/preference surveys, Net Promoter Score (NPS), desirability studies |
| **Behavioral** | Usability testing, diary studies, field studies | Analytics/telemetry, A/B testing (owned by a future Experimentation/A-B Testing chapter, see [PART_OVERVIEW.md](PART_OVERVIEW.md)), card-sort quantitative aggregation |

Reading this grid correctly means recognizing that a method's position is
fixed by *what kind of data it produces*, not by how it "feels" — a survey
that asks "would you use this feature" is attitudinal even though it
produces quantitative-looking numbers, and those numbers are still subject
to the say-do gap (Section 3): a large, statistically clean survey sample
does not fix an attitudinal method's fundamental limitation of measuring
stated intent rather than real behavior.

### 4.4 Research questions vs. interview/survey questions

A research question is the internal question the *team* needs answered
("do users understand the pricing tiers well enough to self-select the
right plan?"); an interview or survey question is what you actually ask a
participant, and it is never a direct restatement of the research question
— asking a participant "do you understand our pricing tiers?" invites a
polite, socially desirable "yes" (Section 6) rather than evidence. Every
research plan (Section 9) should separate these explicitly: one or more
research questions the study exists to answer, and a distinct instrument
(discussion guide, survey, usability task list) designed to surface
evidence for those questions indirectly, through observed behavior and
concrete recent examples rather than direct self-assessment. The craft of
turning a research question into well-worded, non-leading interview
questions is owned in depth by [User Interviews § Core
Concepts](CH04_User_Interviews.md#4-core-concepts); this chapter's
responsibility stops at making sure the distinction exists and is respected
in planning.

### 4.5 Sample size and saturation

How many participants is "enough" depends entirely on which quadrant
(Section 4.3) the study sits in:

- **Qualitative studies rely on saturation, not statistical power.**
  Jakob Nielsen and Tom Landauer's much-cited (and often over-applied)
  finding is that five participants in a single round of usability testing
  typically surface roughly 85% of a product's usability problems, because
  usability issues recur across users rather than being independently
  distributed — additional participants mostly re-surface problems already
  found rather than new ones. The generalizable underlying concept is
  **thematic saturation**: the point in a qualitative study where
  additional participants stop producing new themes and start repeating
  existing ones. The "5±2" figure is a reasonable planning default for a
  single-persona, single-task usability round; it is not a universal law,
  and studies covering multiple distinct user segments need roughly that
  many participants *per segment*, not in total.
- **Quantitative studies rely on statistical power.** A survey or A/B test
  needs a sample size calculated from the effect size you need to detect,
  the variance in the underlying metric, and your acceptable false-positive
  rate — the same statistical machinery used in experimentation more
  broadly (full treatment owned by a future Experimentation chapter, see
  [PART_OVERVIEW.md](PART_OVERVIEW.md)). A common and serious mistake
  (Section 15) is running a qualitative-sized study (5-10 responses) and
  reporting percentages from it as if it had quantitative statistical
  power — five out of seven participants preferring an option is a
  qualitative signal worth investigating further, not a 71% preference
  finding.
- Saturation and power are both, ultimately, arguments about *diminishing
  returns on additional data collection* — the practical skill is noticing
  when you have crossed that point for the question you are actually
  asking, in either direction (stopping too early and generalizing from too
  little, or over-recruiting past the point where new data changes your
  conclusion).

### 4.6 Bias, validity, and triangulation

Every research method is vulnerable to systematic distortion, and knowing
the common failure modes by name is what lets you design around them:

- **Confirmation bias**: unconsciously interpreting ambiguous evidence as
  support for what you already believed, both during fieldwork
  (over-weighting the one quote that confirms the hypothesis) and during
  synthesis (Section 5).
- **Leading questions**: phrasing a question so it signals the "expected"
  or socially preferred answer ("don't you think this would be easier?")
  rather than leaving room for genuine disagreement.
- **Social desirability bias**: participants answering in the way they
  believe makes them look good or is polite toward the researcher/company,
  rather than what they actually think or do — a major driver of the
  say-do gap (Section 3).
- **Recency and primacy effects**: participants over-weighting their most
  recent experience or their very first impression when asked to generalize
  about "typical" usage.
- **Sampling bias**: recruiting participants who are disproportionately
  easy to reach (existing power users, colleagues' friends and family,
  people who reply fastest to a recruiting email) rather than
  representative of the actual target population.
- **Triangulation** is the general countermeasure to all of the above:
  deliberately combining multiple methods, data sources, or researchers to
  see whether they converge on the same conclusion. A finding that shows up
  independently in usage analytics (behavioral, quantitative), a usability
  test (behavioral, qualitative), and support tickets (secondary,
  qualitative) is far more trustworthy than the same finding from any one
  source alone, precisely because each source has a different bias profile
  and they are unlikely to all be wrong in the same direction simultaneously.

## 5. Internal Working

The mechanics of a research study, regardless of which specific method is
used, follow the same six-stage lifecycle — see the diagram at
[diagrams/flow/research-lifecycle.md](../diagrams/flow/research-lifecycle.md):

**Plan → Recruit → Conduct → Synthesize → Share → Act**

1. **Plan**: define the research question(s) (Section 4.4), choose the
   method (Section 4.3), and write the research plan artifact (Section 9)
   that ties both to a concrete recruiting profile and timeline.
2. **Recruit**: screen and schedule participants matching the target
   profile — the single most common point of silent failure (Section 15)
   is a screener loose enough to recruit people who resemble the target
   user demographically but don't actually have the underlying need or
   behavior being studied.
3. **Conduct**: run the sessions or field the instrument. For moderated
   qualitative methods this is where interviewing technique (owned by
   [User Interviews](CH04_User_Interviews.md)) and usability test
   moderation matter most; for unmoderated/quantitative methods this stage
   is mostly instrument deployment and monitoring for data-quality issues
   (straight-lining on surveys, abandoned sessions).
4. **Synthesize**: convert raw data into findings. This is the stage most
   often rushed or skipped under delivery pressure (Section 15), and it has
   its own internal technique, detailed below.
5. **Share**: package findings for the people who need to act on them —
   typically a short readout (key findings, supporting evidence, a clear
   recommendation) rather than a raw transcript dump, plus a permanent
   entry in the research repository (Section 7) so the finding remains
   discoverable after the immediate project ends.
6. **Act**: the actual point of the exercise — findings feed into problem
   framing, prioritization, or design decisions elsewhere in the product
   process. A study whose findings never change a decision was not
   research; it was theatre (Section 19).

### 5.1 Synthesis technique in detail

Synthesis is the least visible and most frequently under-invested stage, so
it is worth detailing the two dominant techniques:

- **Affinity diagramming**: each discrete observation (an atomic quote,
  behavior, or pain point — one per sticky note, physical or digital) is
  written down individually, then the full set is clustered bottom-up into
  groups based on similarity, with group labels emerging from the data
  rather than being decided in advance. Its strength is surfacing patterns
  the researcher did not anticipate; it is typically run collaboratively
  with the wider team (designers, PMs, engineers) rather than solely by the
  researcher, which also builds shared ownership of the findings (Section
  18) and is a countermeasure against a team dismissing findings it wasn't
  present for.
- **Thematic analysis** (formalized by Braun and Clarke's widely used
  six-phase model) is a more structured alternative better suited to larger
  qualitative datasets or when consistency across multiple researchers
  matters: (1) familiarization — reading/watching all raw data before
  coding anything; (2) generating initial codes — short labels tagging
  segments of data (a process also called **open coding**); (3) searching
  for themes — grouping related codes into candidate themes (**axial
  coding**, relating codes to each other); (4) reviewing themes against the
  full dataset to check they hold up; (5) defining and naming themes
  precisely; (6) producing the write-up. The coding vocabulary (open,
  axial, and — in the fullest version of this method, grounded theory —
  selective coding, which identifies one or more core categories the other
  themes relate to) is worth knowing even applied informally, because it
  gives synthesis a defensible, repeatable structure instead of "read the
  transcripts and write down what feels important."
- Both techniques share one non-negotiable discipline: separating
  **observation** (what was directly seen or heard, stated as fact) from
  **interpretation** (what the researcher believes it means) at every
  stage, and labeling which is which. Collapsing the two prematurely is how
  confirmation bias (Section 4.6) enters synthesis undetected — a
  participant saying "I usually just export to a spreadsheet" is an
  observation; "users don't trust the reporting feature" is an
  interpretation of that observation, and a defensible finding shows its
  work by keeping both visible.

## 6. Design Principles

- **Match the method to the question, not to convenience.** Choose a
  position on the generative/evaluative and qualitative/quantitative grid
  (Sections 4.1-4.3) *before* choosing a specific method, based on what kind
  of evidence would actually change the decision at hand.
- **Ask about the past and the specific, not the future and the general.**
  "Tell me about the last time you did X" produces far more reliable
  evidence than "would you use a feature that does X" (Section 3), because
  it asks for a memory rather than a prediction.
- **Recruit for the behavior or segment that matters, not for
  availability.** A screener's job is to exclude people who don't represent
  the target population, even when that makes recruiting slower and
  costlier — a easy-to-reach but unrepresentative sample invalidates the
  study regardless of how well the rest of it is executed.
- **Separate observation from interpretation at the point of capture**, not
  after the fact — note-taking templates and transcript tagging should make
  it structurally difficult to blend the two (Section 5.1).
- **Triangulate before acting on a single source.** Treat any single
  finding, however compelling the supporting quote, as a hypothesis until a
  second, differently-biased source corroborates it (Section 4.6).
- **Prefer continuous, lightweight research over infrequent, heavyweight
  research**, where the question allows it — a five-user hallway test run
  weekly surfaces more usability problems over a quarter than one thirty-
  user study run once, because it catches issues while they are still cheap
  to fix (Section 3) and builds the muscle of acting on findings routinely
  (Section 7).

## 7. Architecture Patterns

This section covers organizational and process patterns for embedding
research capability into a product organization — the research-methodology
analogue of an architecture style.

- **Dual-track agile**: a discovery track (generative and evaluative
  research feeding a validated, right-sized backlog of problems and
  solution options) runs continuously and in parallel with a delivery track
  (building and shipping what discovery has already validated), rather than
  research being a distinct phase that gates delivery. The two tracks share
  the same team but operate on different, overlapping horizons — discovery
  is typically one to two sprints ahead of delivery, not months.
- **Continuous discovery habits**: popularized by Teresa Torres, the
  practice of running a small number of generative interviews (often
  described as a weekly touchpoint with a handful of customers) on a
  standing cadence rather than only when a specific project calls for it,
  so the team always has a current, evidence-based picture of user problems
  to draw on when prioritization decisions come up.
- **Research team topology**: analogous to (but a distinct concept from)
  the architecture team topologies covered in [Role of a Solution
  Architect § Core
  Concepts](../01_Architecture_Mindset/CH02_Role_of_a_Solution_Architect.md#4-core-concepts) —
  research capability is commonly organized as **centralized** (one research
  team serving the whole organization, maximizing rigor and cross-project
  pattern recognition but creating a request queue and bottleneck),
  **embedded** (a researcher dedicated to one product team, maximizing
  context and speed but risking inconsistent method quality and duplicated
  effort across teams), or a **hub-and-spoke ResearchOps model** (a small
  central team owns tooling, recruiting infrastructure, and methodological
  standards, while embedded or rotating researchers/designers/PMs run
  day-to-day studies against those shared standards) — the third pattern is
  the one most research-mature organizations converge on as they scale,
  for the same reason platform teams emerge in engineering organizations:
  it avoids both the bottleneck of full centralization and the
  inconsistency of full fragmentation.
- **The research repository pattern**: a single, searchable, permanent
  store of past findings (raw evidence and synthesized conclusions,
  tagged by topic, product area, and method) that persists past any single
  project's lifetime, letting a new question first check "has someone
  already learned something relevant to this" via secondary research
  (Section 4.2) before commissioning new primary research. Without this
  pattern, organizations routinely re-research the same question every
  time institutional memory turns over.
- **Diary studies and longitudinal research**: for behaviors that unfold
  over days or weeks (onboarding, habit formation, infrequent high-stakes
  tasks) rather than in a single session, participants log
  experiences/artifacts over an extended period, followed by a debrief
  interview — a pattern that trades higher participant effort and
  attrition risk for visibility into behavior no single-session method can
  observe.

## 8. Production Architecture

A mature research operation's tooling and information flow looks roughly
like this:

```text
Recruiting panel/CRM (screener, incentive management)
        |
        v
Scheduling + video/conferencing tooling
        |
        v
Session capture (recording, live transcription)
        |
        v
Synthesis workspace (tagging, affinity clustering, thematic coding)
        |
        v
Research repository (searchable, permanent, cross-project)
        |
        +--> Product/roadmap prioritization (Product Discovery, see PART_OVERVIEW.md)
        +--> Design (Personas, Journey Mapping — this part)
        +--> Analytics platform (behavioral quantitative cross-check)
```

In practice this is implemented with a mix of purpose-built research
platforms (participant recruiting panels, session-recording and
transcription tools, dedicated insight-repository products), general
collaboration tooling (shared documents, whiteboarding tools for affinity
diagramming), and the organization's existing product analytics platform
providing the behavioral-quantitative leg of triangulation (Section 4.6)
against qualitative findings. The specific vendor choices matter far less
than whether the pipeline actually terminates in a searchable, durable
repository (Section 7) rather than a folder of session recordings nobody
revisits.

## 9. Implementation

Running a defensible study, regardless of method, means producing a
concrete **research plan** artifact before recruiting a single participant.
At minimum it should specify:

- **Research questions**: the internal question(s) this study exists to
  answer (Section 4.4) — written as questions the team needs answered, not
  as questions to ask participants.
- **Method and rationale**: which quadrant (Section 4.3) and specific
  method, and *why* that method fits this question better than the
  alternatives — this is the research-plan analogue of an Architecture
  Decision Record's rationale clause (recap: ADRs are owned by
  [Architecture Thinking § Core
  Concepts](../01_Architecture_Mindset/CH03_Architecture_Thinking.md#4-core-concepts)).
- **Recruitment criteria and screener**: the target population and the
  specific screening questions used to exclude non-representative
  volunteers (Section 6) — a screener is itself a small research instrument
  and is subject to the same leading-question risk as any other.
- **Sample size and justification**: a number derived from saturation
  (qualitative) or power (quantitative) reasoning (Section 4.5), not a
  round number chosen for convenience.
- **Instrument outline**: for interviews/usability tests, a discussion
  guide or task list skeleton (full construction technique owned by
  [User Interviews](CH04_User_Interviews.md)); for surveys, the draft
  question set and response scales.
- **Logistics**: timeline, incentive structure, consent and recording
  policy (Section 13), and who on the team observes or participates
  live — live observation by the wider team measurably increases how much
  a finding actually changes downstream decisions, versus only reading a
  report afterward.
- **Analysis plan**: which synthesis technique will be used (Section 5.1)
  and who is responsible for producing the readout, decided in advance so
  synthesis doesn't silently get dropped under schedule pressure
  (Section 15).

A lightweight, single-page version of this plan is appropriate for a
continuous-discovery weekly touchpoint (Section 7); a fuller version is
warranted for a study whose findings will justify a significant, hard-to-
reverse product or architecture decision.

## 10. Complete Code Examples

Research produces more prose artifacts than code, but the quantitative side
of evaluative research benefits from small, reusable analysis scripts:

- Python — computing a System Usability Scale (SUS) score from a ten-item
  post-task questionnaire:
  [code/python/research-chapter/sus_score.py](../code/python/research-chapter/sus_score.py)
- Python — plotting a thematic-saturation curve (new codes discovered per
  additional transcript) to justify a qualitative study's stopping point
  quantitatively (Section 4.5):
  [code/python/research-chapter/thematic_saturation.py](../code/python/research-chapter/thematic_saturation.py)

## 11. Performance

The relevant "performance" metric for a research practice is **time to
insight** — how long it takes from a question being raised to an
evidence-backed answer reaching the people who need it. Continuous,
lightweight methods (Section 7) reduce this by running research on a
standing cadence rather than provisioning a new study from scratch each
time; a well-maintained research repository (Section 7) reduces it further
by answering some questions instantly from prior findings via secondary
research (Section 4.2) rather than commissioning new primary research at
all. Structured synthesis technique (Section 5.1) also affects throughput
directly — ad hoc "read the transcripts and see what jumps out" synthesis
does not scale past a handful of sessions before it becomes slower and less
reliable than structured coding.

## 12. Scalability

As a product organization grows, research demand grows faster than the
number of trained researchers, which is the core scaling problem this
discipline faces. The hub-and-spoke ResearchOps pattern (Section 7)
addresses this the way a platform team addresses infrastructure scaling in
engineering: a small central team invests in reusable infrastructure
(recruiting panels, tooling, a research repository, and a lightweight
methodology standard) so that designers, PMs, and engineers can run
well-scoped studies themselves (a pattern often called **research
democratization**) without every study requiring a dedicated researcher's
time, while the central team still owns training, quality bar enforcement,
and the studies too methodologically demanding for a non-specialist to run
alone (large quantitative studies, studies covering vulnerable populations,
or ones with significant ethical/compliance exposure, Section 13).

## 13. Security

Participant data is personal data, and research operations carry real
privacy obligations, not just methodological ones:

- **Informed consent**: participants must be told what data is collected
  (recordings, transcripts, screen captures), how it will be used, who will
  see it, and how long it is retained, before the session starts — and must
  be able to withdraw consent afterward.
- **Regulatory compliance**: recordings, transcripts, and any personally
  identifiable information (PII) collected during a study fall under the
  same data-protection regimes as any other personal data a company
  processes — GDPR (General Data Protection Regulation) in the EU, CCPA
  (California Consumer Privacy Act) in California, and equivalent regimes
  elsewhere — including data-subject access and deletion rights.
- **Anonymization and redaction**: research repositories (Section 7) should
  store findings and representative (redacted) quotes rather than raw,
  identifiable recordings by default, and access to raw recordings should
  be restricted and time-limited.
- **Secure storage and retention limits**: recordings and transcripts
  should be stored in access-controlled systems with a defined retention
  period, not left indefinitely in personal accounts or unmanaged shared
  drives.
- **B2B and NDA-covered participants**: research involving enterprise
  customers under existing non-disclosure agreements needs its own
  consent/handling process distinct from consumer research, since
  competitively sensitive information may surface incidentally during a
  session.

## 14. Observability

A research practice's health is itself worth instrumenting, not just
assumed to be working:

- **Study throughput**: number of studies run and questions answered per
  period, tracked against demand, to detect a growing backlog before it
  becomes a bottleneck (Section 12).
- **Insight reuse rate**: how often an existing repository entry (Section
  7) answers a new question via secondary research versus requiring new
  primary research — a low reuse rate suggests the repository is not
  actually being consulted, or its tagging/searchability is poor.
- **Research debt**: a running list of decisions made without supporting
  research (analogous to technical debt — recap: owned by [What is
  Software
  Architecture?](../01_Architecture_Mindset/CH01_What_is_Software_Architecture.md#3-why-it-exists)) —
  tracked deliberately so it can be paid down (retroactively validated)
  rather than silently accumulating as unvalidated assumptions baked into
  the product.
- **Coverage mapping**: which product areas or journeys have recent,
  meaningful research behind them versus which are running entirely on
  untested assumptions — surfaced periodically so investment can be
  redirected toward the highest-risk gaps.
- **Stakeholder confidence and finding-to-decision tracing**: whether
  decision-makers report actually using research findings, and whether
  individual findings can be traced forward to the decisions they informed
  — the direct check against research theatre (Section 19).

## 15. Failure Scenarios

- **Recruiting mismatch**: a loose screener (Section 6) recruits
  participants who superficially resemble the target user but lack the
  underlying need or behavior being studied, producing confident findings
  about the wrong population.
- **Leading-question contamination**: a poorly worded instrument (Section
  4.4) systematically nudges participants toward a particular answer,
  invalidating the study even with a perfect sample and correct method
  choice.
- **Under-powered quantitative claims**: a small qualitative-sized sample
  (Section 4.5) gets reported with precise percentages, lending false
  statistical authority to what is actually a qualitative signal.
- **Synthesis skipped or rushed**: raw sessions are run but never properly
  synthesized (Section 5) under delivery-schedule pressure, so the study's
  investment produces no durable finding — a very common and almost
  invisible failure, since the sessions themselves did happen.
- **Cherry-picked evidence overriding synthesis**: a stakeholder (often
  the HiPPO, Section 3) selects one memorable quote or session that
  supports a decision already made, bypassing the actual synthesized
  finding — the study existed, but its conclusion was overridden by a
  single anecdote.
- **Method/question mismatch**: running an evaluative method to answer a
  generative question or vice versa (Section 4.1), producing a technically
  well-executed study that cannot actually answer the question it was
  commissioned for.

## 16. Testing

Research instruments and processes need their own validation before being
trusted at scale:

- **Pilot testing the instrument**: running a discussion guide or survey
  with one or two participants (or internal colleagues unfamiliar with the
  study, for surveys) before full fieldwork, specifically to catch
  confusing wording, leading phrasing, or questions that don't produce
  usable answers — a pilot session's data is usually excluded from the
  final analysis.
- **Cognitive interviewing / question pretesting**: for surveys
  specifically, asking pilot respondents to think aloud about what a
  question means to them, to confirm it is interpreted consistently before
  fielding it at scale — a check on construct validity (whether the
  question actually measures the concept it's intended to measure).
- **Inter-rater reliability**: having two researchers independently code
  the same subset of transcripts (Section 5.1) and comparing results —
  low agreement signals the coding scheme is ambiguous and needs
  refinement before one researcher codes the rest of the dataset alone.
- **Triangulating before finalizing a finding**: treating a synthesized
  finding as provisional until corroborated by a second, differently-biased
  source (Section 4.6), rather than shipping a readout based on a single
  method's output.

## 17. Common Mistakes

- Asking participants to predict their own future behavior directly
  ("would you use this?") instead of asking about relevant past behavior,
  and then treating the answer as reliable (Section 3).
- Treating a five-to-seven-response convenience sample as if it had
  quantitative statistical power (Section 4.5).
- Choosing a method because the team already knows how to run it, rather
  than because it fits the research question (Section 4.1, Section 6).
- Conflating attitudinal data (what users say) with behavioral truth (what
  users do) without triangulating (Section 4.6).
- Skipping structured synthesis and going straight from raw sessions to a
  conclusion based on the most memorable moment rather than the full
  dataset (Section 5.1, Section 15).

## 18. Best Practices

- Write a research plan (Section 9), including sample-size justification,
  before recruiting begins.
- Separate observation from interpretation explicitly at every stage of
  note-taking and synthesis (Section 5.1).
- Triangulate across at least two independently-biased sources before
  treating a finding as decision-ready (Section 4.6).
- Involve the wider team (designers, PMs, engineers) in synthesis sessions,
  not just the researcher, to build shared ownership of findings and
  reduce the chance they get dismissed or overridden later (Section 5.1,
  Section 15).
- Maintain a searchable, permanent research repository (Section 7) so
  findings outlive the project that produced them.
- Calibrate sample size to the actual statistical or saturation requirement
  of the chosen method, not to convenience or budget alone (Section 4.5).

## 19. Anti-Patterns

- **Research theatre**: studies are run, readouts are produced, and nothing
  downstream ever changes as a result — research as a compliance ritual
  rather than a decision input (Section 14).
- **One-and-done big-bang research**: a single large study run once at
  project kickoff, disconnected from ongoing delivery, instead of
  continuous discovery (Section 7) that keeps pace with an evolving
  product.
- **Drive-by research**: a leader's single hallway conversation or one
  support ticket gets treated as decisive evidence, overriding or
  bypassing structured findings (Section 15) — the opposite failure mode
  from research theatre, but equally corrosive to research's credibility.
- **Leading the witness**: interview or survey questions that telegraph
  the "right" answer (Section 4.4, Section 6), producing data that
  confirms whatever the team already believed.
- **Survey-only "why" fishing**: relying on open-ended survey questions
  alone to understand *why* users behave a certain way, when a qualitative
  method (interviews, usability testing) would answer the question far
  more reliably (Section 4.2).

## 20. Trade-off Analysis

| Decision | Benefit | Cost |
|---|---|---|
| Generative research before build vs. skipping straight to build | Reduces risk of building something nobody needs | Adds time before delivery begins; can be perceived as slowing down "real work" |
| Qualitative vs. quantitative method for a given question | Qualitative: deep causal insight ("why"); Quantitative: generalizable prevalence ("how many") | Qualitative: small-sample findings can't be generalized alone; Quantitative: numbers without qualitative context can mislead on cause |
| Centralized vs. embedded vs. hub-and-spoke research team topology | Centralized: consistent rigor; Embedded: speed and context; Hub-and-spoke: balances both | Centralized: request-queue bottleneck; Embedded: inconsistent method quality; Hub-and-spoke: requires investment in shared tooling/standards |
| Moderated vs. unmoderated sessions | Moderated: can probe and follow up in real time; Unmoderated: scales to more participants, less scheduling overhead | Moderated: doesn't scale, costs researcher time per session; Unmoderated: no ability to clarify a confusing response in the moment |

## 21. Comparison Table

| Method | Type | Qual/Quant | Typical sample size | Best for |
|---|---|---|---|---|
| Generative interviews / contextual inquiry | Generative | Qualitative | 5-15 per segment (saturation) | Understanding problems, workflows, unmet needs |
| Diary study | Generative | Qualitative | 8-20 | Longitudinal/infrequent behavior over days-weeks |
| Usability testing | Evaluative | Qualitative | 5±2 per round (saturation) | Finding interaction/comprehension problems in a design |
| Attitude/preference survey | Either | Quantitative | Powered for effect size (often 100s) | Measuring prevalence of an opinion or preference |
| Card sorting | Generative | Qual (open) / Quant (closed, aggregated) | 15-30 | Validating information architecture / navigation grouping |
| Analytics/telemetry review | Evaluative | Quantitative | Full population (secondary data) | Measuring actual usage patterns and funnel drop-off |
| A/B testing | Evaluative | Quantitative | Powered for effect size (owned by a future Experimentation chapter) | Comparing conversion/behavioral impact of two variants |

## 22. Real-World Case Study

A fintech product team observed that budgeting-feature usage was flat
despite repeated feature requests for "better budgeting tools" in support
tickets — a classic setup for a method/question mismatch (Section 4.1):
the team's instinct was to jump straight to evaluative usability testing on
budgeting UI mockups. Instead, the research lead ran a small generative
study first: eight semi-structured interviews (recruiting and interviewing
technique per [User Interviews](CH04_User_Interviews.md)) combined with a
two-week diary study asking participants to log their financial worries as
they occurred. Synthesis via thematic analysis (Section 5.1) surfaced a
theme none of the "better budgeting" feature requests had named directly:
the dominant pain point was anxiety about *surprise* fees and unexpected
charges, not a lack of budgeting math — users already tracked spending
adequately in ad hoc spreadsheets, but had no early warning of upcoming
charges. This reframed the problem entirely (recap: problem framing
technique is owned by a later chapter in this part) away from a budgeting
calculator and toward a proactive alerting feature. A subsequent evaluative
round — a five-participant usability test (Section 4.5) on a low-fidelity
prototype of an alerting flow — caught a critical failure: three of five
participants missed the alert-configuration entry point entirely, a finding
the team would not have caught (or would have wasted a build cycle
discovering post-launch) without running the evaluative round before
shipping. The case illustrates both halves of this chapter working
together: generative research to find the *right* problem, evaluative
research to confirm the *solution* actually works, and triangulation
(support tickets, interviews, diary study, and later analytics) at every
stage rather than trusting any single source.

## 23. Interview Questions

1. What distinguishes generative research from evaluative research, and
   what happens when a team runs the wrong one for a given question?
2. Why is "would you use this?" a weak interview or survey question, and
   what would you ask instead to get at the same underlying concern?
3. How would you decide whether a finding needs 5 participants or 500,
   and what's the difference in reasoning between those two numbers?
4. Describe how you would triangulate a surprising usability-testing
   finding before presenting it as a confirmed conclusion to stakeholders.
5. What is the difference between open coding and axial coding during
   synthesis, and why does separating observation from interpretation
   matter at that stage?

## 24. Hands-on Exercises

1. Write a one-page research plan (Section 9) for understanding why a
   hypothetical app's onboarding flow has a 40% drop-off, including
   research question(s), method choice with rationale, screener, and
   sample-size justification.
2. Recruit five colleagues (or friends, with consent) unfamiliar with a
   product you use daily, and run a short moderated usability test on one
   of its core tasks; synthesize the sessions using affinity diagramming
   (Section 5.1) before drawing any conclusion.
3. Run the SUS-scoring script from Section 10 against a set of sample
   questionnaire responses and interpret the resulting score against
   published SUS benchmarks.

## 25. Design Exercises

Design a research program for a 0-to-1 product's first two quarters after
initial concept validation, choosing which methods (Sections 4.1-4.3, 21)
to run in which order and cadence, and how the findings from each phase
feed the next. Evaluation criteria: correct generative-before-evaluative
sequencing where appropriate, sample-size justification for each method
chosen, an explicit triangulation plan rather than relying on any single
method, and a concrete plan for how findings will be captured in a
repository (Section 7) rather than lost after each round.

## 26. Architecture Review Questions

- Does this study have an explicit research question, and does the chosen
  method actually answer that type of question (Section 4.1, Section 15)?
- Is the sample size justified by saturation or statistical power
  reasoning, rather than chosen for convenience (Section 4.5)?
- Are the instrument's questions checked for leading phrasing, and has the
  instrument been piloted before full fieldwork (Section 16)?
- Is there a concrete plan for synthesis (technique and owner), not just
  for running sessions (Section 9)?
- Will this finding be triangulated against at least one other source
  before being acted on (Section 4.6)?
- Where will this finding live after the immediate project ends, and is it
  discoverable by the next team that asks a related question (Section 7)?

## 27. Summary

Research replaces internal opinion and hierarchy with evidence gathered
directly from the people a product is meant to serve. The core taxonomy
this chapter owns — generative versus evaluative, qualitative versus
quantitative, attitudinal versus behavioral — determines which method can
actually answer a given question, and mismatching them is one of the most
common and expensive ways research goes wrong. Planning (a research
question, a justified method and sample size, a concrete recruiting
screener) and synthesis (structured coding and affinity techniques that
keep observation separate from interpretation, then triangulated across
sources) are what turn raw fieldwork into a defensible finding, and a
durable research repository plus a hub-and-spoke ResearchOps model are what
let that capability scale with the organization rather than bottlenecking
on a handful of specialists. The next two chapters in this subsection build
directly on this foundation: [Personas](CH03_Personas.md) takes synthesized
research and compresses it into a reusable design artifact, and the
forthcoming [User Interviews](CH04_User_Interviews.md) chapter goes deep on
the single most common generative method this chapter deliberately left at
survey depth.

**Further reading**: [Empathy](CH01_Empathy.md) ·
[Personas](CH03_Personas.md) ·
[User Interviews](CH04_User_Interviews.md) ·
[What is Software Architecture?](../01_Architecture_Mindset/CH01_What_is_Software_Architecture.md) ·
[Architecture Thinking](../01_Architecture_Mindset/CH03_Architecture_Thinking.md) ·
[Design Thinking and Product Management — Part Overview](PART_OVERVIEW.md)
