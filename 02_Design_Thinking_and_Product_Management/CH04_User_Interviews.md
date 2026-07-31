# Chapter: User Interviews

Part: [02 — Design Thinking and Product Management](PART_OVERVIEW.md) · Status: Drafted

## 1. Introduction

A user interview is a conversation with a single participant, deliberately
structured and moderated to surface evidence about that person's real goals,
context, and behavior — as opposed to their opinions about a feature idea,
their guesses about their own future behavior, or whatever answer feels
polite to give a stranger holding a clipboard. It is the single most
frequently used generative research method in software product development,
and it is also one of the easiest methods to run badly while feeling
confident that it went well, because a bad interview and a good interview
can look identical from the outside: both involve a friendly conversation
that produces quotes. The difference is entirely in craft that is invisible
unless you know what to look for — question wording, what the moderator does
in the silence after a participant stops talking, and whether a follow-up
probe chases the participant's own thread or subtly redirects it toward what
the moderator already expected to hear.

This chapter is chapter four of Part 02 — Design Thinking and Product
Management, and it exists because of a boundary [Research](CH02_Research.md)
drew deliberately around itself. Research owns the *methodology* layer: the
taxonomy of research types (generative versus evaluative, qualitative versus
quantitative, attitudinal versus behavioral — recap:
[Research § Core Concepts](CH02_Research.md#4-core-concepts) for the full
treatment), how to choose a method for a given question, how to plan and
recruit for a study, and how to synthesize raw data into a defensible
finding via affinity diagramming or thematic analysis (recap:
[Research § Internal Working](CH02_Research.md#5-internal-working)). This
chapter owns the layer Research explicitly left at survey depth: the actual
craft of running one instance of the most common method on that landscape —
what happens between "the recruiting screener passed this person through"
and "the recording stops and synthesis begins." That craft is narrow enough
in scope and deep enough in nuance that it earns its own chapter rather than
a section: how to design a discussion guide, how to word a question so it
elicits evidence instead of politeness, how to build enough rapport that a
stranger tells you something true in forty-five minutes, and — the hardest
skill in the whole method — how to notice and correct a leading question or
a biased probe *while the conversation is still happening*, not three weeks
later while reading a transcript.

This chapter deliberately does **not** re-teach what [Research](CH02_Research.md)
already owns. When this chapter needs the generative/evaluative distinction,
the qualitative/quantitative axis, sample-size and saturation reasoning, the
research-bias taxonomy in general, or the research plan artifact, it recaps
each in two or three sentences and links back rather than re-deriving them —
see the boxed recaps throughout Sections 3-4. Two adjacent chapters in this
part are being drafted in the same batch as this one — "Journey Mapping" and
"Problem Framing" — and this chapter makes no assumptions about their
eventual content; it simply notes, where relevant, that interview data is
raw material those chapters are likely to consume, without teaching their
techniques itself.

For the Solution Architect audience of this handbook specifically: almost
every Architecturally Significant Requirement (recap:
[What is Software Architecture? § Core
Concepts](../01_Architecture_Mindset/CH01_What_is_Software_Architecture.md#4-core-concepts))
that claims to be user-driven traces back, at some point, to a small number
of interviews. An architect who can read a discussion guide and immediately
spot three leading questions, or who can ask "was that a direct quote about
a specific past event, or a paraphrase of what the moderator assumed the
participant meant" has a concrete, falsifiable way to pressure-test a
requirement's evidentiary basis — the same instinct this handbook already
trains for architecture trade-offs (recap:
[Architecture Thinking § Core
Concepts](../01_Architecture_Mindset/CH03_Architecture_Thinking.md#4-core-concepts)),
applied one layer further upstream, to the requirement itself rather than
the design response to it.

## 2. Historical Evolution

The one-on-one qualitative interview predates software product design by
decades and was assembled from several source disciplines, each contributing
technique this chapter still uses directly.

- **1920s-1940s — the clinical and depth interview.** Psychotherapeutic
  interviewing (notably Carl Rogers' person-centered approach, formalized in
  the 1940s-50s) established active listening, unconditional positive
  regard, and reflective paraphrasing as deliberate conversational
  techniques rather than incidental politeness — the direct ancestor of the
  rapport-building and probing technique in Sections 4.4-4.5.
- **1950s-1960s — the focused and non-directive interview in social
  science.** Robert Merton's "focused interview" (with Patricia Kendall,
  1946) and the broader non-directive interviewing tradition in sociology
  established the idea of a topic guide that steers a conversation toward
  areas of interest without scripting the participant's answers — the
  conceptual root of the semi-structured format this chapter treats as the
  default (Section 4.1).
- **1979 — Spradley's ethnographic interview.** James Spradley's *The
  Ethnographic Interview* formalized descriptive, structural, and contrast
  questions as a systematic technique for eliciting a participant's own
  cultural/behavioral categories rather than imposing the interviewer's —
  directly informing the laddering and grand-tour question technique in
  Section 4.3.
- **1980s — contextual inquiry emerges at Digital Equipment Corporation and
  Xerox PARC (Palo Alto Research Center).** Fieldwork blending observation
  with in-context questioning (recap:
  [Research § Historical Evolution](CH02_Research.md#2-historical-evolution)
  covers the broader ethnographic-research lineage this belongs to) began
  treating "ask while watching, in the participant's own environment" as a
  distinct interviewing mode from the sit-down conversation.
- **1998 — Beyer and Holtzblatt's *Contextual Design*.** Hugh Beyer and
  Karen Holtzblatt formalized contextual inquiry's **master-apprentice
  model** — the interviewer positions themselves as an apprentice learning
  a skill from the participant-as-master, asking questions only to
  understand what is being observed rather than to direct it — which this
  chapter treats in depth as its own interview mode (Section 4.6), distinct
  from the sit-down interview.
- **2000s — usability-testing-specific interviewing (the think-aloud
  protocol).** Concurrent think-aloud technique, formalized for usability
  work by practitioners including Jakob Nielsen, adapted interview-adjacent
  probing ("what are you thinking right now?") to run alongside a
  participant performing a task rather than only recalling one — evaluative
  interviewing's counterpart to generative interviewing's technique.
- **2013 — Rob Fitzpatrick's *The Mom Test*.** A short, widely read,
  practitioner-focused book that reframed the core interviewing problem in
  a memorable way: design every question so that even your own mother —
  who wants to make you happy and will say anything polite to do so —
  could not lie to you without it being obvious. This chapter's treatment
  of behavioral-versus-hypothetical question wording (Section 4.3) draws
  directly on this framing, now close to industry-standard vocabulary for
  the failure mode it names.
- **2015-2020 — Teresa Torres and continuous, lightweight interviewing.**
  As covered at the process level in
  [Research § Architecture Patterns](CH02_Research.md#7-architecture-patterns),
  the continuous-discovery movement pushed interviewing toward a standing
  weekly habit run by product trios (product manager, designer, engineer)
  rather than a rare, heavyweight event — which raised the bar for
  interviewing craft being a broadly held skill rather than a specialist
  one, since far more people were now expected to run interviews
  competently, more often, with less individual practice time between
  sessions.
- **2020s — remote video interviewing as the default mode.** The
  pandemic-era shift to remote, video-conferencing-based sessions (recap:
  [Research § Historical Evolution](CH02_Research.md#2-historical-evolution))
  changed several interview-specific mechanics this chapter covers directly
  in Section 4.8 — rapport-building without shared physical space, the
  loss of most environmental/contextual-inquiry cues, and the normalization
  of AI (artificial intelligence)-assisted live transcription reducing (but
  not eliminating) the note-taker's cognitive load during a session.

## 3. Why It Exists

Interviewing exists as its own disciplined craft, distinct from ordinary
conversation, because of two related failure modes that ordinary
conversational instinct does not protect against.

- **The say-do gap, applied in real time.** Research already establishes
  (recap:
  [Research § Why It Exists](CH02_Research.md#3-why-it-exists)) that what
  people say and what people do systematically diverge. An interview is the
  one method where a skilled moderator can actively fight that gap
  *during* the conversation — by redirecting a hypothetical answer back to
  a specific past event as it happens — rather than only discovering the
  gap later during synthesis, once the conversation that could have caught
  it is already over. An unskilled moderator, by contrast, can *widen* the
  gap in real time, by asking exactly the kind of future-hypothetical
  question ("would you use a feature that...") that invites a polite,
  unfalsifiable answer.
- **Rapport is a precondition for honesty, not a social nicety.** A
  participant who does not feel heard, or who senses judgment, will
  default to socially desirable answers (recap:
  [Research § Core Concepts](CH02_Research.md#46-bias-validity-and-triangulation)
  for the bias taxonomy in general) — not out of dishonesty, but because
  humans are conflict-averse with strangers by default. Building enough
  trust in forty-five minutes that a participant volunteers an
  embarrassing workaround, an unflattering opinion of the product, or an
  admission that they never actually use a feature they claimed to value
  is a skill, not a personality trait, and it degrades measurably under
  remote-video conditions (Section 4.8) unless deliberately compensated
  for.
- **The moderator is simultaneously the instrument and a source of bias.**
  In a survey, the instrument is fixed in advance and cannot react to an
  individual respondent; in an interview, the moderator *is* the
  instrument, deciding in real time which thread to follow, how to phrase
  a follow-up, and when to let silence sit — every one of those in-the-
  moment decisions is a fresh opportunity to introduce confirmation bias
  (chasing only the answers that confirm what the moderator expected) or
  a leading question (Section 4.3) that a fixed instrument could never
  introduce after design time. No other common research method concentrates
  this much bias-introducing opportunity into a single, live, unrepeatable
  event — which is exactly why the craft in this chapter exists as a named
  discipline rather than being left to instinct.
- **The gap between novice and expert interviewers is unusually large and
  unusually invisible.** A novice moderator's transcript often *reads* fine
  — full of quotes, no obvious errors — while still having steered every
  answer subtly toward confirmation, because the damage is in phrasing and
  timing choices that don't announce themselves on the page. This is why
  Section 16 (Testing) treats pilot interviews and moderator calibration as
  load-bearing practices rather than optional polish, and why this chapter
  exists at all rather than trusting good-faith conversational instinct to
  produce good data by default.

## 4. Core Concepts

### 4.1 Interview formats: structured, semi-structured, and unstructured

Interviews sit on a spectrum of how tightly the questions and their order
are fixed in advance — see the diagram at
[diagrams/matrix/interview-format-spectrum.md](../diagrams/matrix/interview-format-spectrum.md).

- **Structured interviews** use a fixed set of questions, asked in a fixed
  order, with little or no improvised follow-up — closer in spirit to a
  survey administered verbally. They maximize comparability across
  participants (every participant answered the exact same question in the
  exact same words) at the cost of missing anything the fixed question set
  didn't anticipate. They are appropriate when a study needs to aggregate
  or compare answers across many participants in a structured way — a
  posture closer to the quantitative side of Research's landscape grid
  (recap:
  [Research § Core Concepts](CH02_Research.md#43-the-research-methods-landscape-attitudinalbehavioral--qualitativequantitative)).
- **Unstructured interviews** have a topic in mind but no fixed question
  set at all — closer to an open conversation guided entirely by what the
  participant says next. They maximize the chance of discovering something
  the researcher didn't anticipate, at the cost of comparability across
  participants and a much higher dependency on moderator skill, since there
  is no guide to fall back on if the conversation stalls.
- **Semi-structured interviews** are the default and by far the most common
  format for generative product research: a discussion guide (Section 4.2)
  defines a topic sequence and a bank of prepared questions, but the
  moderator is expected to reorder, skip, rephrase, and — most
  importantly — follow up on unanticipated threads the participant raises,
  rather than executing the guide mechanically. This chapter's technique
  (Sections 4.2-4.6) is written primarily for the semi-structured format,
  because it is where craft matters most: a structured interview's rigidity
  protects a novice moderator from some mistakes at the cost of missing
  discoveries, while an unstructured interview offers no such protection at
  all.
- Choosing a point on this spectrum is itself a decision with a trade-off
  (Section 20), not a stylistic preference — a study whose research
  question (recap:
  [Research § Core Concepts](CH02_Research.md#44-research-questions-vs-interviewsurvey-questions))
  needs cross-participant comparability should lean structured; a study
  whose research question is "what haven't we thought to ask about yet"
  should lean unstructured; most generative product research sits in the
  semi-structured middle by design.

### 4.2 The discussion guide

A discussion guide (sometimes called an interview guide or topic guide) is
the concrete artifact a moderator prepares before a semi-structured
interview — the interview-specific instrument Research's research plan
(recap:
[Research § Implementation](CH02_Research.md#9-implementation)) refers to
only as an "instrument outline" deferred to this chapter. A well-built guide
has a **funnel structure**, moving from broad to specific:

1. **Warm-up (2-5 minutes)**: low-stakes, easy-to-answer questions
   ("tell me a bit about your role and a typical day") that establish
   rapport (Section 4.4) and let the participant get comfortable talking
   before anything sensitive or effortful is asked.
2. **Grand-tour questions**: broad, open invitations to describe a general
   area ("walk me through the last time you had to reconcile this report")
   that let the participant set the initial frame in their own words and
   vocabulary, rather than the moderator's.
3. **Core questions**: the guide's main body, organized by topic and tied
   directly back to the study's research questions (recap:
   [Research § Core Concepts](CH02_Research.md#44-research-questions-vs-interviewsurvey-questions)) —
   each core question should trace to a specific thing the team needs to
   learn, not just feel generally relevant.
4. **Probes**: not separate questions but prepared, generic follow-ups
   ("what happened next," "why was that frustrating," "who else was
   involved") attached under each core question, ready to deploy when the
   participant's initial answer is thin — detailed further in Section 4.5.
5. **Wrap-up**: a closing, wide-open question ("is there anything about
   this we haven't touched on that you think matters") that frequently
   surfaces the single most valuable finding of the session, precisely
   because it is the one question not constrained by the moderator's own
   prior framing.

A guide should be treated as a **checklist the moderator has memorized well
enough to abandon**, not a script read verbatim — the funnel structure and
prepared probes exist so the moderator's cognitive effort during the live
session goes toward listening and following threads (Section 4.5), not
toward remembering what to ask next. A guide that must be read from
verbatim, question by question, has already collapsed into the structured
format (Section 4.1) whether or not that was the intent.

### 4.3 Question design and wording

This is the single highest-leverage skill this chapter teaches, because a
badly worded question contaminates every answer that follows it regardless
of how skilled the rest of the session is.

- **Behavioral versus hypothetical wording.** A hypothetical question asks
  a participant to predict or imagine ("would you use a feature that lets
  you export to a spreadsheet automatically?") and reliably produces an
  optimistic, unreliable answer, because predicting your own future
  behavior is a task humans are demonstrably bad at (recap: the say-do gap,
  [Research § Why It Exists](CH02_Research.md#3-why-it-exists)). A
  behavioral question asks about a specific, real, past event ("tell me
  about the last time you needed data out of this system in spreadsheet
  form — what did you actually do?") and produces a verifiable, concrete
  account instead. The single most reliable rewrite pattern in this
  chapter is converting any hypothetical question into its behavioral
  equivalent before it goes in a discussion guide.
- **The Mom Test.** Rob Fitzpatrick's framing (Section 2) gives a portable
  test for question quality: would this question extract real information
  even from someone who loves you and wants you to feel good about your
  idea? "Do you think this is a good idea?" fails the test (your mother
  will say yes to be kind); "how are you currently handling this problem,
  and what have you already tried?" passes it, because it asks for facts
  a well-meaning participant cannot fabricate as easily as an opinion.
- **Open versus closed questions.** Open questions ("how do you currently
  decide which invoices to prioritize?") invite the participant to
  structure their own answer and frequently surface vocabulary and
  categories the moderator didn't anticipate; closed questions ("do you
  prioritize invoices by due date?") invite a yes/no or short factual
  answer and are appropriate for confirming a specific detail, not for
  generative exploration. A guide dominated by closed questions produces
  thin, moderator-led data regardless of how well-intentioned the
  moderator is.
- **Avoiding leading questions.** A leading question embeds the expected
  or socially preferred answer inside its own phrasing (recap: leading
  questions are named in Research's general bias taxonomy,
  [Research § Core Concepts](CH02_Research.md#46-bias-validity-and-triangulation);
  this section owns the specific wording patterns and moment-to-moment
  discipline needed to avoid them). Common leading patterns to eliminate
  from a guide, and in live rephrasing:
  - **Tag questions**: "this is frustrating, isn't it?" — the tag itself
    supplies the answer.
  - **Assumed-premise questions**: "why do you find the export feature
    confusing?" assumes the participant finds it confusing before they've
    said so; "what's your experience been with the export feature?" does
    not.
  - **Loaded adjectives**: "how much do you enjoy this streamlined
    workflow?" presupposes the workflow is in fact streamlined and
    enjoyable; "walk me through this workflow" does not.
  - **Compound/double-barreled questions**: "was that fast and easy?"
    conflates two separate dimensions into one answer and biases toward
    whichever one is more socially comfortable to affirm.
- **Laddering (the "why" chain / means-end technique).** Adapted from
  means-end chain theory in marketing research and from Spradley's
  contrast questions (Section 2), laddering repeatedly asks *why* a stated
  preference or action matters, climbing from a concrete feature-level
  statement ("I want a faster export") up through underlying reasoning
  ("because I need the numbers before the 9am meeting") to the actual goal
  or value at stake ("because being unprepared in front of my boss's boss
  is the thing I'm actually afraid of"). The technique is powerful and easy
  to overuse; three to five "why" iterations is typically enough to reach
  a genuine underlying goal, and pushing further risks feeling like an
  interrogation (Section 19) rather than a conversation.
- **Critical Incident Technique.** Rather than asking a participant to
  generalize about "typical" usage — which invites recency and primacy
  bias (recap:
  [Research § Core Concepts](CH02_Research.md#46-bias-validity-and-triangulation)) —
  critical incident technique anchors the entire question on one specific,
  memorable, real incident ("tell me about the worst time this process
  went wrong") and mines that single incident for detail. A concrete
  incident is far more reliably recalled and far less prone to
  post-hoc rationalization than a generalization about "usually."

### 4.4 Rapport-building

Rapport is the working trust that makes a participant willing to say
something true, unflattering, or uncertain to a person they have known for
five minutes.

- **The warm-up's real job** (Section 4.2) is not information-gathering; it
  is establishing that the moderator is a genuinely curious, non-judgmental
  listener before anything consequential is asked.
- **Explaining the "why" and the ground rules up front** — that there are
  no wrong answers, that the moderator did not build the thing being
  discussed and won't be offended by criticism (true even when this is not
  literally accurate, since the participant's honesty depends on believing
  it), and that the goal is to learn from the participant's real experience
  — measurably reduces social-desirability bias (recap:
  [Research § Core Concepts](CH02_Research.md#46-bias-validity-and-triangulation))
  for the remainder of the session.
- **Matching register and pace**, not correcting a participant's
  terminology or tone, signals that the conversation is on the
  participant's terms — a participant corrected for using a "wrong" term
  for a feature is now performing for the moderator's approval rather than
  reporting freely.
- **Tolerating silence.** A pause after a question feels uncomfortably long
  to a novice moderator and is routinely "rescued" by adding detail,
  offering an example, or rephrasing — every one of which risks turning an
  open question into a leading one (Section 4.3) or simply answering the
  question for the participant before they had the chance to. Waiting
  through several seconds of silence is one of the most effective and most
  underused rapport and data-quality techniques in this chapter, because it
  is precisely the moment before a participant produces their own
  unprompted, unbiased answer.

### 4.5 Moderation and probing

Moderation is the real-time skill of steering a semi-structured
conversation without steering its content.

- **Active listening signals** — brief, content-free acknowledgments
  ("mm-hmm," a nod, "go on") — keep a participant talking without
  supplying any information that could bias the next sentence, unlike
  evaluative reactions ("oh interesting," visible surprise, or a wince),
  which participants read as feedback about which of their answers the
  moderator liked and will often start optimizing for.
- **Generic probes**, prepared in the guide (Section 4.2) and deployed
  whenever an answer is thinner than the topic warrants: "what happened
  next," "can you say more about that," "why was that a problem," "who
  else was involved," "how did that make you feel." Their genericness is
  the point — a probe that references specific content the moderator
  already suspects ("was that because the export was slow?") is a leading
  question in probe form (Section 4.3).
- **Following the participant's own thread versus protecting the guide's
  structure.** The single most common moderation judgment call is deciding
  whether an unanticipated tangent is a discovery worth following (the
  entire justification for the semi-structured format, Section 4.1) or a
  genuine digression that needs a polite redirect back to the guide, given
  finite session time. There is no universal rule; the practical heuristic
  is whether the tangent still traces to one of the study's research
  questions (recap:
  [Research § Core Concepts](CH02_Research.md#44-research-questions-vs-interviewsurvey-questions)) —
  if it plausibly does, follow it; if it clearly doesn't, redirect briefly
  and note the tangent for later rather than cutting it off abruptly.
- **Handling difficult participant behaviors**: a participant who rambles
  off-topic needs a warm, specific redirect ("that's helpful context — can
  we come back to what happened right before that error appeared?"); a
  monosyllabic participant needs more, not fewer, silences and open probes
  rather than an escalating stream of closed questions that trains them to
  keep answering in single words; a participant clearly performing for the
  moderator's approval needs the ground rules (Section 4.4) restated, not
  a harder push for a "real" answer.
- **The moderator's own neutrality is a continuously monitored discipline,
  not a one-time setup step** — confirmation bias (recap:
  [Research § Core Concepts](CH02_Research.md#46-bias-validity-and-triangulation))
  shows up moment-to-moment as an urge to probe harder on answers that
  confirm a hypothesis and move on quickly from answers that don't; a
  disciplined moderator applies the same probing energy regardless of
  which direction an answer points.

### 4.6 Contextual inquiry and the master-apprentice model

Contextual inquiry (recap:
[Research § Historical Evolution](CH02_Research.md#2-historical-evolution)
introduces it as a generative method category; this section owns the
in-session technique) is a distinct interview mode conducted in the
participant's actual working environment while they perform real work,
rather than in a conference room recalling that work afterward. Beyer and
Holtzblatt's **master-apprentice model** (Section 2) reframes the
moderator's role entirely: the participant is the master of a skill or
process, the moderator is an apprentice trying to learn it, and questions
are asked only to understand what is being observed in the moment ("why did
you switch to that other screen just now?"), not to direct or evaluate it.
This mode trades the controllability and comparability of a sit-down
interview (every session happens in a different, uncontrolled real
environment) for a categorical advantage no recall-based interview can
match: it captures workarounds, interruptions, and environmental
constraints the participant has stopped consciously noticing and would
never think to mention unprompted, because "of course I keep a paper backup
next to my keyboard" only becomes visible to the participant themselves
once someone unfamiliar with the workflow asks about it.

### 4.7 Roles: moderator and note-taker/observer

Running an interview with two people in dedicated roles measurably improves
data quality over a single person attempting both jobs simultaneously:

- The **moderator** owns the conversation exclusively — following the
  guide (Section 4.2), building rapport (Section 4.4), and probing
  (Section 4.5) — and should not be splitting attention with detailed
  note-taking, since divided attention during a live conversation directly
  degrades the quality of in-the-moment listening and follow-up decisions.
- The **note-taker/observer** captures observations in real time
  (recap: the observation-versus-interpretation discipline owned by
  [Research § Internal Working](CH02_Research.md#51-synthesis-technique-in-detail)),
  tracks which prepared questions have and haven't been covered, and — in
  a well-run session — passes the moderator a short list of follow-up
  questions to ask near the end if time allows, catching threads the
  moderator's own attention may have missed while focused on the live
  conversation.
- When only one person is available, recording (with consent, Section 13)
  becomes load-bearing rather than optional, since detailed notes cannot be
  reliably produced by the same person who is simultaneously moderating.

### 4.8 Remote versus in-person interviews

- **In-person interviews**, especially contextual inquiry (Section 4.6),
  give the moderator the full environment as a source of unprompted
  observation — sticky notes, workaround spreadsheets, the physical
  arrangement of a workspace — none of which is visible over
  video-conferencing software unless the participant deliberately shares
  it, and most participants do not think to.
- **Remote interviews** trade that environmental visibility for reach
  (recruiting outside a single geography, recap:
  [Research § Historical Evolution](CH02_Research.md#2-historical-evolution))
  and lower logistical cost, and are now the default mode for most
  generative product research. Rapport-building (Section 4.4) requires
  more deliberate compensation over video — explicitly naming the ground
  rules, tolerating silence despite the mild awkwardness video calls add to
  pauses, and watching for the specific remote failure mode of a
  participant multitasking or reading from a device off-camera, which
  degrades both rapport and answer quality without the moderator
  necessarily noticing.
- **Screen-sharing** partially recovers some of in-person's contextual
  advantage for interviews about digital tools specifically (a participant
  can show, not just describe, their actual spreadsheet or workaround),
  though it recovers none of it for interviews about a physical workspace
  or process.

## 5. Internal Working

A single interview session, end to end, follows a repeatable internal
sequence regardless of format — see the diagram at
[diagrams/flow/interview-session-flow.md](../diagrams/flow/interview-session-flow.md):

**Prepare guide → Confirm logistics/consent → Warm-up → Grand-tour →
Core questions + probes → Wrap-up → Close and thank → Immediate debrief**

1. **Prepare the guide** (Section 4.2), tied to the study's research
   questions (recap:
   [Research § Implementation](CH02_Research.md#9-implementation)) and, for
   a guide's first live use, already piloted (Section 16).
2. **Confirm logistics and consent** at the top of the session itself, not
   only in a prior recruiting email — restating what is being recorded,
   how it will be used, and confirming the participant still consents,
   immediately before starting (Section 13).
3. **Warm-up and grand-tour** (Section 4.2) establish rapport (Section 4.4)
   and let the participant frame the topic area in their own words before
   the moderator narrows in.
4. **Core questions and probes** (Sections 4.3, 4.5) are where most of the
   session's time and the moderator's judgment calls are spent, following
   threads that trace back to the research questions and redirecting
   those that don't.
5. **Wrap-up** deliberately opens the floor one more time (Section 4.2),
   catching whatever the guide's own structure didn't anticipate.
6. **Close and thank**, restating what happens with the recording/notes
   and, where applicable, incentive logistics (recap:
   [Research § Implementation](CH02_Research.md#9-implementation)).
7. **Immediate debrief**: the moderator and note-taker (Section 4.7) spend
   five to ten minutes immediately after the participant leaves, while
   memory is freshest, capturing top-of-mind impressions and flagging
   anything that felt like a strong signal — this raw debrief is itself an
   observation to be checked against the fuller synthesis later (recap:
   [Research § Internal Working](CH02_Research.md#5-internal-working)
   owns the full synthesis pipeline this session's transcript and notes
   feed into), not a substitute for it.

### 5.1 The probe decision loop

Within step 4 above, a moderator is continuously running a small decision
loop worth making explicit, since it is the core moment-to-moment skill this
chapter teaches: **listen to the answer → judge whether it is a concrete,
behavioral, sufficiently detailed account or a thin/hypothetical/vague one
(Section 4.3) → if thin, deploy a generic probe (Section 4.5) rather than a
leading one → if concrete, judge whether it opens a thread worth laddering
into (Section 4.3) or the guide should move on → repeat**. Every iteration
of this loop is a fresh opportunity to introduce or avoid bias, which is why
Section 15 treats the accumulation of many small in-the-moment mistakes,
rather than one dramatic error, as the most common way an interview session
actually goes wrong.

## 6. Design Principles

- **Ask about a specific past event, never a hypothetical future one**
  (Section 4.3) — this is the single highest-leverage rule in the whole
  chapter and the direct cause of most of the other principles below.
- **A question that only your own mother could safely answer honestly has
  already failed** (Section 4.3, the Mom Test) — design every question to
  survive being asked of someone who wants to make you happy.
- **Treat the guide as a checklist to abandon, not a script to read**
  (Section 4.2) — rigid execution of a memorized structure degrades
  moderation quality (Section 4.5) far more than skipping or reordering
  questions in response to what the participant actually says.
- **Prefer silence to rescue** (Section 4.4) — resist filling a pause with
  a suggestion, an example, or a rephrase; the participant's own next
  sentence, produced without prompting, is more valuable data than
  anything the moderator could offer to fill the gap.
- **Probe generically, not specifically** (Section 4.5) — a follow-up that
  names content the moderator already suspects is a leading question
  wearing a different grammatical form.
- **Separate the moderator and note-taker roles whenever session logistics
  allow it** (Section 4.7) — divided attention degrades both jobs
  simultaneously.
- **Debrief immediately, synthesize later** (Section 5) — capture raw
  top-of-mind impressions right after a session while treating full
  synthesis (recap:
  [Research § Internal Working](CH02_Research.md#51-synthesis-technique-in-detail))
  as a separate, more disciplined later step, not something the immediate
  debrief substitutes for.

## 7. Architecture Patterns

This section covers recurring structural patterns for how interviews are
organized and combined with other methods — the interview-specific
counterpart to Research's organizational patterns
(recap: [Research § Architecture
Patterns](CH02_Research.md#7-architecture-patterns) for team-topology and
process-level patterns; this section is about patterns within and around a
single method).

- **Interview-then-debrief-then-synthesize pipeline**: the standard
  pattern this chapter's Section 5 describes, feeding directly into
  Research's synthesis stage (recap:
  [Research § Internal Working](CH02_Research.md#5-internal-working)) —
  the point at which this chapter's ownership ends and Research's resumes.
- **Diary-then-interview (debrief) pattern**: for behavior that unfolds
  over days or weeks, a longitudinal diary study (recap:
  [Research § Architecture Patterns](CH02_Research.md#7-architecture-patterns)
  owns the diary-study method itself) is typically closed out with a
  one-on-one debrief interview using this chapter's technique, mining the
  diary entries for critical incidents (Section 4.3) worth laddering into
  rather than starting the interview cold.
- **Interview paired with think-aloud/usability observation**: an
  evaluative session commonly opens with a short interview-style warm-up
  (Section 4.2) before transitioning into task-based think-aloud
  observation, using this chapter's rapport and probing technique for the
  interview portion and evaluative-method-specific technique (owned
  elsewhere in this part, once a Usability Testing chapter exists) for the
  task portion.
- **Dual-moderator pairing for calibration**: newer moderators are paired
  with an experienced one in the note-taker role (Section 4.7) specifically
  to observe technique, then swap roles across sessions — the interview
  method's version of the pilot-and-calibration discipline Section 16
  treats as load-bearing.
- **Continuous, standing interview cadence**: recap:
  [Research § Architecture Patterns](CH02_Research.md#7-architecture-patterns)
  covers Teresa Torres' continuous-discovery habit of a small, steady
  weekly volume of interviews at the process level; this chapter's
  technique is what makes that cadence produce reliable data run after
  run, rather than degrading as moderators rush guide preparation under a
  standing weekly deadline.

## 8. Production Architecture

The concrete tooling and information flow around a single interview study
looks like this:

```text
Research plan (recap: Research § Implementation) hands off
        |
        v
Discussion guide authored + piloted (Section 4.2, Section 16)
        |
        v
Recruiting/scheduling tool confirms participant + logistics
        |
        v
Session: video-conferencing/in-person + consent capture (Section 13)
        |
        +--> Live: moderator (Section 4.7) + note-taker/observer (Section 4.7)
        |
        v
Recording + (often AI-assisted) transcript
        |
        v
Immediate debrief notes (Section 5) captured separately from the transcript
        |
        v
Handoff into Research's synthesis pipeline
   (recap: Research § Internal Working, § 5.1 Synthesis technique)
```

The interview-specific additions to Research's own production-architecture
diagram (recap:
[Research § Production Architecture](CH02_Research.md#8-production-architecture))
are the discussion-guide authoring/piloting step and the live
moderator/note-taker session itself — everything downstream of the
transcript is Research's synthesis pipeline, unchanged by which specific
method produced the raw data.

## 9. Implementation

Preparing to run a defensible interview study, beyond the research plan
Research already requires (recap:
[Research § Implementation](CH02_Research.md#9-implementation)), means
producing this chapter's specific artifacts:

- **A discussion guide** (Section 4.2) with an explicit funnel structure,
  core questions traced to research questions, and prepared generic probes
  under each core question (Section 4.5).
- **A question-wording pass** applying the Mom Test and the leading-
  question checks (Section 4.3) to every question in the guide before
  first use — in practice, reading each question aloud and asking "could
  a participant who wants to please me answer this without giving me real
  information?"
- **A consent script**, read or restated verbatim at the start of every
  session (Section 13), covering what is recorded, how it is used, and
  confirming continued consent — kept consistent across every session in a
  study rather than improvised each time.
- **A role assignment** for moderator and note-taker/observer (Section 4.7)
  decided before the session, not negotiated in the room.
- **A debrief template** — a short, standard set of prompts ("what
  surprised you," "what's the strongest quote from this session," "what
  would you probe harder on next time") used immediately after every
  session (Section 5) to keep debriefs consistent and comparable across a
  multi-session study, rather than an unstructured chat that captures
  whatever happens to come up.

## 10. Complete Code Examples

Interviewing is a conversational craft, but two small, reusable scripts
support the mechanical parts of preparing and reviewing sessions:

- Python — a discussion-guide linter that scans a guide's question text
  for common leading-question patterns (tag questions, assumed-premise
  phrasing, loaded adjectives — Section 4.3) and flags lines for review
  before a guide's first use:
  [code/python/user-interviews-chapter/leading_question_linter.py](../code/python/user-interviews-chapter/leading_question_linter.py)
- Python — a talk-time ratio calculator that parses a speaker-labeled
  transcript and reports the moderator-to-participant speaking-time ratio,
  flagging sessions where the moderator talked disproportionately more than
  the participant (Section 14, Section 15) as a coachable moderation
  signal:
  [code/python/user-interviews-chapter/talk_time_ratio.py](../code/python/user-interviews-chapter/talk_time_ratio.py)

## 11. Performance

The relevant "performance" measure for a single interview is how much
usable, concrete signal it produces per minute of participant time, not
merely how many topics the guide covered. A session dominated by closed
questions (Section 4.3) can cover more nominal ground in forty-five minutes
while producing less usable evidence than a session that lingers on two or
three critical incidents (Section 4.3) in depth — breadth and depth trade
directly against each other within a fixed session length (Section 20), and
a guide author has to choose deliberately rather than trying to maximize
both. Session length itself has a practical ceiling: most participants'
attention and candor measurably decline past roughly sixty to seventy-five
minutes, so a guide with more core-question material than a session can
cover at a comfortable, unhurried pace should be trimmed before the study
starts, not compressed into a faster-talking moderator during the session.

## 12. Scalability

As a study or a continuous-discovery cadence (Section 7) scales to more
sessions and more moderators, the risk shifts from any single interview's
quality to **consistency across moderators**. The dual-moderator
calibration pattern (Section 7) and a shared, reviewed discussion guide
(Section 9) are the primary scaling mechanisms — a guide that has already
been piloted and question-linted (Section 16) travels well across
moderators of varying experience, whereas an unstructured or purely
improvised interviewing style does not scale past whichever individual
happens to be skilled at it. At larger scale, recap:
[Research § Scalability](CH02_Research.md#12-scalability) covers the
organizational side of this problem — a hub-and-spoke ResearchOps model
that trains and calibrates a wider pool of interviewers (product managers,
designers, engineers running their own continuous-discovery sessions)
against a shared quality bar, rather than every interview depending on a
small number of specialist researchers.

## 13. Security

Interviews carry the same participant-data obligations Research already
establishes (recap:
[Research § Security](CH02_Research.md#13-security) for informed consent,
regulatory compliance, anonymization, and retention limits in general),
plus interview-specific considerations:

- **Re-confirming consent at the start of the live session** (Section 9),
  not only via a prior recruiting email, since a participant's willingness
  to be recorded can change between scheduling and the session itself.
- **Recording device and storage security**: video-conferencing recordings
  and any local backup recordings should land directly in access-controlled
  storage rather than a moderator's personal device or unmanaged folder,
  consistent with Research's storage/retention guidance.
- **In-session escalation handling**: a participant may disclose something
  requiring immediate escalation regardless of research topic — a safety
  concern, a compliance issue, or business-sensitive information under an
  existing non-disclosure agreement (recap:
  [Research § Security](CH02_Research.md#13-security) covers the
  B2B/NDA-covered participant case) — and a study should define in advance
  who the moderator alerts if this happens, rather than leaving it to
  in-the-moment improvisation.
- **Psychological safety and the right to pass.** A participant should be
  told explicitly, as part of the consent script (Section 9), that they can
  decline any question or stop the session at any time without
  consequence — particularly important for sensitive topics (financial
  hardship, health, workplace conflict) where a critical-incident question
  (Section 4.3) could otherwise resurface real distress.

## 14. Observability

An interviewing practice's craft quality is measurable, not just a matter
of moderator reputation:

- **Talk-time ratio**: the participant should speak substantially more than
  the moderator across a session (a common rough target is 70-80%
  participant talk time) — a session where the moderator talks more than
  the participant is a strong signal of over-explaining, leading, or
  rescuing silence (Section 4.4), measurable directly from a
  speaker-labeled transcript (Section 10).
- **Leading-question rate**: the proportion of a discussion guide's
  questions flagged by a leading-question review (Section 4.3, Section 10)
  before first use, tracked across guides over time as a proxy for how
  well question-wording discipline is spreading across a growing pool of
  moderators.
- **Probe-to-thin-answer ratio**: whether thin or vague answers are
  actually followed by a generic probe (Section 4.5) rather than the guide
  simply moving on — visible from a note-taker's session log and a useful
  coaching signal distinct from talk-time ratio.
- **Inter-moderator consistency**: whether two moderators running the same
  guide against comparable participants produce similarly structured,
  similarly deep sessions (recap: an interview-specific instance of
  Research's inter-rater reliability check,
  [Research § Testing](CH02_Research.md#16-testing)).
- **No-show and reschedule rate**: an operational health signal shared with
  Research's own recruiting-quality tracking (recap:
  [Research § Observability](CH02_Research.md#14-observability)), since
  a high no-show rate silently erodes a study's effective sample size below
  its planned saturation target (recap:
  [Research § Core Concepts](CH02_Research.md#45-sample-size-and-saturation)).

## 15. Failure Scenarios

- **Leading the witness in the moment**: a moderator rescues an
  uncomfortable silence (Section 4.4) by suggesting a possible answer,
  which the participant then politely confirms — producing a transcript
  that reads as a finding but is actually the moderator's own hypothesis
  reflected back at them.
- **Compounding small biases across many probes**: no single question in
  a session is dramatically leading, but a steady pattern of slightly
  loaded follow-ups (Section 5.1) accumulates into a session-wide steer
  toward the moderator's prior expectation, invisible from any one exchange
  in isolation.
- **Moderator monopolizing talk time**: over-explaining context, filling
  pauses with the moderator's own opinions, or narrating what the
  moderator already believes before the participant answers (Section 14) —
  each of which reduces the participant's airtime and, with it, the
  amount of unprompted data the session produces.
- **Social-desirability capture despite good rapport intent**: a
  participant who senses (correctly or not) that the moderator built or
  is emotionally invested in the thing being discussed shifts toward
  polite, protective answers regardless of how warmly the session opened
  (Section 4.4) — a risk the consent-script framing (Section 9) exists
  specifically to reduce, not eliminate.
- **Note-taker/moderator role collapse**: a single person attempting both
  jobs (Section 4.7) either takes worse notes, moderates worse, or both,
  most visibly when a genuinely interesting unanticipated thread appears
  and there is no one dedicated to deciding whether to follow it while the
  moderator is mid-conversation.
- **Technical failure**: a recording that silently failed to start, or a
  note-taker's connectivity dropping mid-session, discovered only during
  synthesis — a preventable failure mode a pre-session checklist (Section
  16) should catch before it happens rather than after.

## 16. Testing

- **Pilot interviews** (recap:
  [Research § Testing](CH02_Research.md#16-testing) covers instrument
  pretesting in general): running the discussion guide once, ideally with
  an internal colleague unfamiliar with the study or a low-stakes
  participant, specifically to catch confusing wording, questions that
  don't produce usable answers, and a session length estimate before full
  fieldwork begins — pilot session data is typically excluded from the
  study's final findings.
- **Leading-question linting** (Section 10): running every question in a
  guide through the Mom Test and the specific leading-pattern checks
  (Section 4.3) before the pilot, not only after a problem is noticed in
  a live transcript.
- **Moderator shadowing and calibration**: a newer moderator observes an
  experienced one in the note-taker role (Section 7) before running
  sessions solo, and periodically afterward, specifically checking for
  the failure patterns in Section 15 rather than only general
  conversational competence.
- **A pre-session technical checklist**: confirming recording is active,
  consent has been (re-)obtained, and the note-taker has access to the
  guide, run as a standing habit before every session rather than only
  after a technical failure (Section 15) has already occurred once.

## 17. Common Mistakes

- Asking a hypothetical, future-facing question ("would you use...")
  instead of its behavioral, past-facing equivalent (Section 4.3).
- Rescuing silence with a suggestion or example instead of waiting for the
  participant's own next sentence (Section 4.4).
- Deploying a specific, content-laden probe ("was that because it was too
  slow?") instead of a generic one ("what happened next?") (Section 4.5).
- Reading the discussion guide verbatim in fixed order instead of using it
  as a checklist to abandon in favor of following the participant's own
  thread (Section 4.2, Section 4.5).
- Asking double-barreled, compound questions that conflate two separate
  dimensions into one answer (Section 4.3).
- Letting a single person handle both moderating and detailed note-taking
  (Section 4.7), degrading both.
- Treating a session's immediate debrief impressions as a finished finding
  instead of raw input to full synthesis (Section 5, recap:
  [Research § Internal Working](CH02_Research.md#5-internal-working)).

## 18. Best Practices

- Convert every hypothetical question in a guide to its behavioral
  equivalent before first use (Section 4.3).
- Run the Mom Test and a leading-question check on the full guide before
  piloting it (Section 4.3, Section 16).
- Build in deliberate warm-up and wrap-up questions rather than starting
  cold on the core topic or ending abruptly when the guide runs out
  (Section 4.2).
- Assign moderator and note-taker roles explicitly before every session
  (Section 4.7).
- Debrief immediately after each session using a consistent template
  (Section 5, Section 9), before moving on to the next session or task.
- Calibrate newer moderators through shadowing before they run sessions
  solo (Section 16).
- Track talk-time ratio and leading-question rate across a study as
  concrete, checkable quality signals rather than relying on subjective
  impressions of "how it went" (Section 14).

## 19. Anti-Patterns

- **The sales pitch interview**: the moderator spends much of the session
  explaining or defending the product instead of listening, producing a
  session that resembles a customer call more than research.
- **The survey read aloud**: a guide made entirely of closed, fixed
  questions, executed rigidly in order (Section 4.1, Section 4.2),
  producing thin, comparable-but-shallow data better suited to an actual
  survey instrument.
- **The friendly chat with no structure and no findings**: an unstructured
  conversation (Section 4.1) that builds genuine rapport but never
  connects back to a research question, producing an enjoyable session
  with no usable output.
- **The interrogation**: rapid-fire questions with no warm-up, no silence
  tolerance, and no rapport-building (Section 4.4), producing guarded,
  minimal answers from a participant who never relaxes enough to offer
  unprompted detail.
- **The leading-witness session**: a pattern of suggestive probes and
  rescued silences (Section 4.3, Section 15) that produces a transcript
  confirming exactly what the moderator expected to hear, regardless of
  what was actually true for the participant.

## 20. Trade-off Analysis

| Decision | Benefit | Cost |
|---|---|---|
| Structured vs. semi-structured vs. unstructured format (Section 4.1) | Structured: cross-participant comparability; unstructured: maximizes unanticipated discovery | Structured: misses the unanticipated; unstructured: low comparability, highly moderator-dependent |
| In-person vs. remote (Section 4.8) | In-person: full environmental/contextual cues; remote: reach and lower logistical cost | In-person: limited geography, higher cost; remote: weaker rapport, lost environmental signal |
| Two-person (moderator + note-taker) vs. solo moderation (Section 4.7) | Two-person: undivided attention for both jobs | Two-person: doubles staffing cost per session |
| Breadth (more topics) vs. depth (fewer topics, more laddering) within a fixed session length (Section 11) | Depth: richer critical incidents and underlying goals via laddering | Breadth: covers more of the guide but each topic more shallowly |
| Recording every session vs. notes-only (Section 13) | Recording: exact transcript, frees note-taker's attention | Recording: added consent/storage/compliance burden |

## 21. Comparison Table

| Interview mode | Structure (4.1) | Setting | Best for | Key risk |
|---|---|---|---|---|
| Structured interview | Fixed questions, fixed order | In-person or remote | Cross-participant comparison of specific answers | Misses unanticipated findings |
| Semi-structured interview | Guide + prepared probes, adaptive order | In-person or remote | General-purpose generative product research | Depends heavily on moderator skill |
| Unstructured interview | Topic only, no fixed questions | Usually in-person | Early, exploratory discovery of an unfamiliar domain | Low comparability; hard to train new moderators on |
| Contextual inquiry (master-apprentice) | Loosely guided, observation-led | In-person, participant's real environment | Capturing workarounds and unconsciously-omitted context | Not scalable across geography; harder logistics |
| Diary-study debrief interview | Semi-structured, anchored to logged entries | In-person or remote | Mining longitudinal/infrequent behavior for critical incidents | Depends on diary entry quality/completeness |

## 22. Real-World Case Study

Return to the fintech budgeting case introduced in
[Research § Real-World Case Study](CH02_Research.md#22-real-world-case-study):
a team ran eight generative interviews after support tickets requested
"better budgeting tools." The discussion guide's first draft, in its pilot
run (Section 16), included the question "don't you wish this app made
budgeting easier?" — a tag-question, loaded-adjective leading question
(Section 4.3) that the pilot participant answered with an enthusiastic but
essentially uninformative "yes, definitely." The guide-review pass caught
it before fieldwork began and rewrote it to "tell me about the last time
you had to figure out whether you could afford something" — a behavioral,
critical-incident-anchored question (Section 4.3) that, across the eight
real sessions, reliably surfaced the same unprompted theme: participants
described specific past moments of anxiety about an unexpected charge
appearing *after* they had already decided they could afford something,
not confusion about budgeting math itself. One session in particular
demonstrated the value of silence tolerance (Section 4.4): a participant
paused for nearly ten seconds after the critical-incident question before
volunteering, unprompted, that they had been embarrassed by a declined card
at a restaurant the previous month — a specific, emotionally loaded
incident the moderator would very likely have pre-empted with a rescuing
follow-up example, and one that turned out to anchor the eventual reframing
away from a budgeting calculator and toward proactive spending alerts
(recap:
[Research § Real-World Case Study](CH02_Research.md#22-real-world-case-study)
for how that reframing then fed problem framing and a subsequent
evaluative usability round). The case illustrates this chapter's core claim
concretely: the difference between a leading question that would have
confirmed the team's existing "users want better budgeting math" assumption
and a well-worded behavioral question that overturned it was a single
sentence's wording, caught only because the guide was piloted and reviewed
before fieldwork rather than trusted on first draft.

## 23. Interview Questions

1. Rewrite the question "would you use a feature that automatically flags
   suspicious transactions?" as a behavioral question, and explain what
   specifically makes the original version unreliable.
2. What is the difference between a generic probe and a leading probe, and
   why can the same follow-up phrase be either depending on its wording?
3. Explain the master-apprentice model in contextual inquiry and why it
   changes what an interview can capture compared to a sit-down,
   recall-based interview.
4. A note-taker reports that the moderator talked for roughly half of a
   forty-five-minute session. What does that observability signal suggest,
   and what would you check next before concluding the session's data is
   unusable?
5. Why does this chapter recommend treating a discussion guide as a
   checklist to abandon rather than a script to read, and what specific
   failure mode does rigid, verbatim execution of a guide risk?

## 24. Hands-on Exercises

1. Draft a discussion guide (Section 4.2) with a warm-up, three core
   questions each with two prepared generic probes, and a wrap-up
   question, for a research question of your choosing; run it through the
   Mom Test and the leading-question checks (Section 4.3) before
   finalizing it.
2. Recruit a colleague or friend and run a fifteen-minute semi-structured
   interview using the guide from Exercise 1, with a second person acting
   as note-taker (Section 4.7); afterward, run the talk-time ratio script
   from Section 10 against a transcript of the session and discuss what
   it shows.
3. Take a discussion guide you did not write (a colleague's, or a
   published example) and run the leading-question linter script from
   Section 10 against it; manually review any flagged questions and
   propose a behavioral rewrite for each.

## 25. Design Exercises

Design the interview component of a research plan (recap:
[Research § Implementation](CH02_Research.md#9-implementation)) for a
0-to-1 product team that has only support tickets and internal assumptions
to work from — no prior research repository entries exist yet. Specify:
the interview format chosen on the structured-to-unstructured spectrum
(Section 4.1) and why; the guide's funnel structure and at least three core
questions with the reasoning that ties each to a research question; the
moderator/note-taker staffing plan (Section 4.7); and a concrete piloting
and calibration plan (Section 16) given that none of the assigned
moderators has run a formal interview study before. Evaluation criteria:
every core question survives the Mom Test (Section 4.3); the format choice
is justified against the trade-offs in Section 20 rather than asserted;
the plan explicitly addresses moderator inexperience rather than assuming
competence.

## 26. Architecture Review Questions

- Does every question in the discussion guide survive the Mom Test and the
  specific leading-question checks in Section 4.3?
- Is the interview format (structured/semi-structured/unstructured,
  Section 4.1) an explicit, justified choice rather than a default?
- Are moderator and note-taker roles assigned before the session, and is
  there a calibration plan for newer moderators (Section 4.7, Section 16)?
- Has the guide been piloted, and were pilot findings used to revise
  question wording before fieldwork began (Section 16)?
- Is there a standard debrief template used immediately after every
  session, distinct from full synthesis (Section 5, Section 9)?
- Are talk-time ratio and leading-question rate being tracked as concrete
  quality signals across the study (Section 14), rather than relying on
  subjective impressions of session quality?

## 27. Summary

A user interview looks, from the outside, like an ordinary conversation —
which is exactly why its craft is easy to underrate and easy to get subtly
wrong while feeling confident it went well. This chapter's core contribution
is making that craft explicit and checkable: converting hypothetical
questions into behavioral ones, applying the Mom Test and specific
leading-question patterns to every question before it is asked, building a
funnel-structured discussion guide treated as a checklist rather than a
script, tolerating silence instead of rescuing it, probing generically
rather than specifically, and separating the moderator and note-taker roles
so neither job is degraded by divided attention. None of this replaces
[Research](CH02_Research.md)'s methodology layer — choosing the right method
for a question, planning a study, and synthesizing raw data into a
defensible finding remain owned there, and this chapter's output (a
transcript and a set of debrief notes) is simply Research's synthesis
pipeline's raw input. What this chapter adds is the difference between a
session that produces genuine, unbiased evidence and one that produces a
confident-sounding transcript that mostly reflects the moderator's own prior
beliefs back at them. The forthcoming Journey Mapping and Problem Framing
chapters later in this part are likely to consume exactly this kind of
interview data as raw material, without needing to re-derive how it was
collected.

**Further reading**: [Empathy](CH01_Empathy.md) ·
[Research](CH02_Research.md) ·
[Personas](CH03_Personas.md) ·
[What is Software Architecture?](../01_Architecture_Mindset/CH01_What_is_Software_Architecture.md) ·
[Architecture Thinking](../01_Architecture_Mindset/CH03_Architecture_Thinking.md) ·
[Design Thinking and Product Management — Part Overview](PART_OVERVIEW.md)
