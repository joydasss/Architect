# Part 02 — Design Thinking and Product Management Topic Map

This map is the coverage contract for Part 02's 31 chapters across two subsections. Design Thinking chapters build human-centered evidence and solution exploration; Product Management chapters use that evidence to make market, strategy, investment, delivery, and outcome decisions. The map preserves the distinct ownership of the repeated Personas and Journey Mapping titles.

## Part-wide ownership boundaries

- Part 02 Design Thinking owns user-centered inquiry, problem framing, ideation, prototyping, usability, accessibility, service design, and Lean UX practices.
- Part 02 Product Management owns market and product strategy, discovery decisions, commercial lifecycle, roadmaps, backlogs, metrics, experiments, prioritization, pricing, go-to-market, and feedback systems.
- Part 01 owns the general architecture decision loop and Architecture Decision Record (ADR) practice. Product and design decisions may use those methods but should not re-teach them.
- Part 03 owns software engineering and delivery implementation. Part 18 owns enterprise architecture. Part 24 owns case-study synthesis. These parts may provide applications or evidence, not alternate owners of the methods mapped here.
- Keep duplicate titles disambiguated: CH03 Personas defines the Design Thinking research artifact; CH18 Personas (Product Management) applies market/customer segmentation and product decisions. CH05 Journey Mapping teaches the human-centered journey artifact; CH19 Journey Mapping (Product Management) maps the commercial/customer lifecycle and recaps the construction method.
- Distinguish evidence from inference. Personas, journey maps, market estimates, roadmaps, metrics, and experiments are decision aids whose validity depends on sampling, assumptions, ownership, and update cadence.

## Cross-part stakeholders and quality scenarios

- Users and customers need products that solve real problems and remain usable across abilities, contexts, and access modes.
- Designers and researchers need credible methods for discovering needs without confusing a loud anecdote with representative evidence.
- Product managers and business owners need explicit choices about market, value, investment, sequencing, pricing, and outcomes.
- Engineering, operations, sales, support, and legal stakeholders need a shared view of scope, dependencies, feasibility, and launch readiness.
- Important scenarios include invalidating a strategic assumption before a large investment; detecting a severe accessibility blocker before launch; changing a roadmap after new evidence; learning from an experiment without overclaiming causality; and ensuring customer feedback reaches a decision owner.

## Design Thinking

### CH01 Empathy

**Reader outcome:** Gather and interpret human evidence with care, distinguishing a person's context and needs from the team's assumptions.

**Coverage:** Empathy as disciplined inquiry; observation and listening; context, motivation, constraints, and emotion; empathy maps as synthesis artifacts; ethical research and privacy; translating evidence into questions rather than solutions.

**Decision/evidence:** Check whose perspective is represented, what is directly observed, and what remains inferred. Preserve contradictory evidence and consent boundaries.

**Diagram opportunities:** (1) observation-to-interpretation boundary; (2) empathy-map evidence flow; (3) contextual inquiry interaction; (4) assumption versus observed behavior; (5) synthesis from multiple participant signals.

### CH02 Research

**Reader outcome:** Select and combine research methods that reduce uncertainty about users, problems, and contexts.

**Coverage:** Research questions; qualitative and quantitative methods; sampling and recruitment; interviews, observation, surveys, and secondary sources; bias and validity; synthesis and confidence; ethical data handling.

**Decision/evidence:** Match method to uncertainty and decision cost. Record sample limitations and avoid treating convenience samples as population truth.

**Diagram opportunities:** (1) question-to-method selection; (2) research plan and sampling path; (3) triangulation across qualitative and quantitative evidence; (4) bias entering collection and interpretation; (5) evidence-confidence ladder.

### CH03 Personas

**Reader outcome:** Build evidence-grounded user archetypes that communicate recurring goals and constraints without presenting fictional characters as facts.

**Coverage:** Persona purpose and limits; behavioral patterns; evidence provenance; segmentation signals; goals, needs, context, and barriers; validation and retirement; use in design decisions.

**Decision/evidence:** Show which research supports each claim, confidence, and unresolved variation. Avoid demographic stereotypes and false precision.

**Diagram opportunities:** (1) interview data clustered into behavioral patterns; (2) evidence-to-persona claim trace; (3) persona confidence and sample coverage; (4) persona-to-design decision use; (5) persona review and update lifecycle.

**Boundary:** CH03 owns the human-centered persona artifact; CH18 owns Product Management's segmentation and market/persona application and recaps this definition.

### CH04 User Interviews

**Reader outcome:** Plan and conduct interviews that reveal behavior and context without leading participants toward the team's preferred answer.

**Coverage:** Research objective; recruitment and consent; interview guide; open questions and follow-up probes; observation versus interpretation; note-taking and synthesis; common interviewer bias.

**Decision/evidence:** Use recent concrete behavior, not only stated preference. Check that the guide can disconfirm the hypothesis and that participant selection is fit for purpose.

**Diagram opportunities:** (1) interview preparation and consent flow; (2) question ladder from context to behavior; (3) neutral versus leading question contrast; (4) quote/observation/inference coding; (5) interview themes mapped to confidence and next research.

### CH05 Journey Mapping

**Reader outcome:** Model an evidenced user journey across stages and touchpoints to expose friction, emotion, and opportunities for improvement.

**Coverage:** Journey-map purpose and anatomy; actor, scenario, stages, actions, thoughts, emotion, pain points, and opportunities; current versus future state; evidence sources; cross-channel handoffs; map validation and maintenance.

**Decision/evidence:** Keep stages grounded in research and distinguish user experience from internal process. Identify the most consequential breakdown and its owner.

**Diagram opportunities:** (1) staged journey with actions and touchpoints; (2) emotional curve connected to evidence; (3) cross-channel handoff and failure; (4) current-to-future state comparison; (5) pain-point-to-opportunity trace.

**Boundary:** CH05 owns journey-map construction; CH19 (Product Management) owns commercial-lifecycle application and recaps this artifact.

### CH06 Problem Framing

**Reader outcome:** Turn observations into a bounded problem statement that identifies affected people, unmet need, and evidence without prescribing a premature solution.

**Coverage:** Symptoms versus root needs; point of view and open-ended opportunity prompts; scope and constraints; causal analysis; assumptions; reframing and validation; linkage to outcomes.

**Decision/evidence:** Check that the problem is specific enough to guide exploration and broad enough to allow alternatives. Trace every claim to research or label it as an assumption.

**Diagram opportunities:** (1) symptom-to-need reframing; (2) causal chain from context to observed friction; (3) problem-statement components; (4) constraint versus solution boundary; (5) evidence-backed framing review.

### CH07 Ideation

**Reader outcome:** Generate and compare solution directions while preserving divergent exploration before converging on a testable concept.

**Coverage:** Divergent/convergent modes; individual and collaborative ideation; constraints and prompts; concept combination; selection criteria; feasibility, desirability, and viability; bias and group dynamics.

**Decision/evidence:** Avoid premature voting and loudest-voice selection. Document the alternatives and criteria used to converge.

**Diagram opportunities:** (1) divergent-to-convergent funnel; (2) prompt and constraint shaping idea space; (3) concept-clustering map; (4) idea evaluation across user/business/technical criteria; (5) selection rationale and test question.

### CH08 Rapid Prototyping

**Reader outcome:** Build the cheapest artifact that can answer a specific design uncertainty and learn from observed behavior.

**Coverage:** Prototype fidelity; paper, clickable, coded, and service prototypes; hypotheses; testing setup; iteration; prototype limitations; safety and ethical simulation.

**Decision/evidence:** Match fidelity and cost to the risk of the question. Do not treat prototype approval as production validation.

**Diagram opportunities:** (1) uncertainty-to-prototype-fidelity choice; (2) build-test-learn iteration; (3) prototype boundary versus production system; (4) hypothesis and observable behavior; (5) prototype result updating a design decision.

### CH09 Wireframing

**Reader outcome:** Communicate information hierarchy, flow, and interaction structure before visual polish obscures unresolved usability questions.

**Coverage:** Information architecture; layout and hierarchy; navigation; states and transitions; low/high-fidelity wireframes; annotation and collaboration; responsive and accessibility considerations.

**Decision/evidence:** Evaluate whether users can find and complete priority tasks, not whether a wireframe looks finished.

**Diagram opportunities:** (1) content hierarchy to screen layout; (2) navigation and task flow; (3) empty/loading/error/success screen states; (4) responsive layout transformation; (5) annotation linking design choice to user need.

### CH10 Usability Testing

**Reader outcome:** Design and run task-based tests that reveal whether representative users can complete meaningful goals and where the design fails.

**Coverage:** Test objectives; participant selection; scenarios and tasks; moderated/unmoderated methods; observation; severity and frequency; synthesis; accessibility and ethical considerations; iteration.

**Decision/evidence:** Use task success, errors, time, and observed breakdown in context. Separate usability evidence from market demand and preference polling.

**Diagram opportunities:** (1) test plan from decision question; (2) participant-task-observation flow; (3) task success and severity matrix; (4) usability issue to design iteration; (5) confidence boundary between a small formative test and a population claim.

### CH11 Accessibility

**Reader outcome:** Design and evaluate experiences usable by people with diverse abilities, assistive technologies, and situational constraints.

**Coverage:** Accessibility principles and standards; semantic structure; keyboard and focus; screen readers; contrast and visual presentation; captions and alternatives; forms and errors; testing methods; inclusive design and legal context.

**Decision/evidence:** Combine automated checks with manual assistive-technology testing and disabled-user input. Treat severe blockers as release risks, not cosmetic defects.

**Diagram opportunities:** (1) user/task/assistive-technology interaction; (2) keyboard focus order through a task; (3) semantic structure to accessible name/role/state; (4) automated/manual evaluation coverage; (5) accessibility defect severity and remediation flow.

### CH12 Service Design

**Reader outcome:** Model an end-to-end service across user-facing interactions and backstage people, processes, systems, and handoffs.

**Coverage:** Service ecosystems; frontstage/backstage; service blueprint; touchpoints and channels; operational dependencies; handoffs; failure recovery; co-design and service evolution.

**Decision/evidence:** Identify the owner and evidence for every critical handoff. A polished interface does not compensate for an unowned operational step.

**Diagram opportunities:** (1) service blueprint swimlane; (2) frontstage/backstage handoff; (3) dependency and ownership map; (4) failure/recovery journey; (5) service change from user signal to operating-process update.

### CH13 Lean UX

**Reader outcome:** Reduce product and design uncertainty through small hypotheses, collaborative experiments, and outcome-focused learning.

**Coverage:** Lean UX principles; assumptions and hypotheses; MVP as a learning instrument; cross-functional collaboration; validated learning; experiment cadence; outcomes versus output; when lean methods are unsafe or insufficient.

**Decision/evidence:** State what evidence changes the decision and how an experiment avoids harming users. A small release is not automatically an MVP or a valid test.

**Diagram opportunities:** (1) assumption-to-hypothesis-to-test loop; (2) MVP scope versus learning objective; (3) output metric versus user outcome; (4) evidence changing a product decision; (5) experiment guardrails and rollback.

## Product Management

### CH14 Product Discovery

**Reader outcome:** Identify valuable opportunities and test whether a product direction addresses a real customer problem before committing to a delivery plan.

**Coverage:** Continuous discovery; opportunity framing; customer evidence; solution exploration; assumption testing; product trio collaboration; discovery/delivery balance; transition to strategy and execution.

**Decision/evidence:** Make uncertainty explicit, prioritize learning by decision impact, and avoid treating feature requests as validated opportunities.

**Diagram opportunities:** (1) continuous discovery loop; (2) opportunity-solution tree; (3) assumption risk and evidence matrix; (4) discovery-to-delivery handoff; (5) customer signal to validated opportunity.

### CH15 Product Strategy

**Reader outcome:** Define a coherent product direction that connects target customers, differentiated value, choices, capabilities, and measurable outcomes.

**Coverage:** Strategy versus goals and roadmap; market/customer choices; value proposition; strategic trade-offs; capability alignment; product principles; strategic bets; validation and adaptation.

**Decision/evidence:** Make explicit what the product excludes and why. Link each bet to customer and market evidence, resources, risks, and a measurable result.

**Diagram opportunities:** (1) strategy stack from market context to choices; (2) target customer/value proposition fit; (3) strategic bet portfolio; (4) capability gap and investment path; (5) strategy hypothesis and evidence review.

### CH16 Market Analysis

**Reader outcome:** Assess market structure, customer segments, demand, and opportunity size without treating estimates as certainty.

**Coverage:** Market definition; segmentation; customer needs; total addressable/serviceable/obtainable market estimates; demand signals; adoption and constraints; evidence quality and sensitivity analysis.

**Decision/evidence:** Make assumptions, sources, ranges, and uncertainty visible. Market size alone does not prove a reachable or profitable opportunity.

**Diagram opportunities:** (1) market boundary and adjacent categories; (2) segment needs and adoption barriers; (3) market-sizing funnel with assumptions; (4) evidence-source confidence map; (5) sensitivity range under changed assumptions.

### CH17 Competitive Analysis

**Reader outcome:** Compare alternatives and competitive positioning to identify customer choice drivers and defensible product opportunities.

**Coverage:** Direct/indirect alternatives; customer decision criteria; positioning; competitor evidence; differentiation; market dynamics; ethical limits and update cadence.

**Decision/evidence:** Compare on customer-relevant dimensions rather than feature counts. Separate observed competitor facts from inference and avoid copying a competitor's roadmap.

**Diagram opportunities:** (1) alternatives by customer job; (2) value curve across choice criteria; (3) positioning map with evidence; (4) competitor capability versus customer outcome; (5) competitive response scenario.

### CH18 Personas (Product Management)

**Reader outcome:** Use market and customer segments to focus product strategy and investment while reusing the human-centered persona foundation from CH03.

**Coverage:** Market segments and buying roles; customer value and willingness to adopt; persona-to-product implications; segmentation evidence; commercial lifecycle and decision authority; validation.

**Decision/evidence:** Do not conflate user archetypes with market segments, buyers, or account types. CH03 owns persona construction; this chapter owns product-management application.

**Diagram opportunities:** (1) human-centered persona mapped to buyer/user roles; (2) segment-to-value proposition matrix; (3) account buying committee and adoption path; (4) segment evidence and confidence; (5) segment choice changing product investment.

### CH19 Journey Mapping (Product Management)

**Reader outcome:** Apply journey mapping to the commercial and product lifecycle, connecting customer stages to value, conversion, retention, and operational ownership.

**Coverage:** Customer lifecycle stages; acquisition, onboarding, adoption, renewal, and expansion; commercial touchpoints and handoffs; stage metrics; revenue or retention implications; recap CH05's map-construction method.

**Decision/evidence:** Keep projected business impact labeled as an estimate and validate it across segments. CH05 owns the human-centered journey artifact; this chapter owns the Product Management application.

**Diagram opportunities:** (1) lifecycle stages with ownership; (2) conversion and retention drop-off; (3) stage touchpoint-to-metric trace; (4) customer handoff across product and commercial teams; (5) segment-specific journey comparison.

### CH20 Story Mapping

**Reader outcome:** Organize user activities and tasks into a shared product narrative, then derive a coherent first release and incremental slices.

**Coverage:** User backbone; activities and tasks; walking skeleton; release slices; prioritization within a story map; collaboration; relationship to backlog and roadmap.

**Decision/evidence:** Preserve end-to-end user value in each slice instead of delivering disconnected layers. Roadmaps own broader strategic sequencing; this chapter owns story-level slicing.

**Diagram opportunities:** (1) activity/task story-map backbone; (2) vertical release slices across user flow; (3) walking skeleton versus feature-complete release; (4) dependency and risk across slices; (5) story map to backlog transfer.

### CH21 Roadmaps

**Reader outcome:** Communicate strategic intent, outcomes, sequencing, and uncertainty through a roadmap suited to its audience and commitment level.

**Coverage:** Outcome/feature/timeline formats; Now/Next/Later; themes and bets; roadmap governance; stakeholder communication; dependency and confidence; update cadence; anti-patterns.

**Decision/evidence:** Distinguish forecast from promise and outcome from output. Roadmaps sequence themes; CH20 and CH22 own within-scope story/backlog and prioritization methods.

**Diagram opportunities:** (1) outcome-based roadmap themes; (2) Now/Next/Later horizon compression; (3) roadmap confidence and dependency map; (4) strategy bet to roadmap entry trace; (5) roadmap change after new evidence.

### CH22 Backlog

**Reader outcome:** Maintain a transparent, actionable work queue that connects product intent to deliverable items without confusing backlog ordering with roadmap strategy.

**Coverage:** Backlog purpose and ownership; item refinement; acceptance criteria; dependencies; sizing and readiness; queue health; technical work; relationship to story maps and roadmap themes.

**Decision/evidence:** Treat the backlog as a live decision aid, not a delivery commitment. Avoid allowing it to become a dumping ground. Make priority rationale and stale-item policies visible.

**Diagram opportunities:** (1) strategy/theme/story/backlog decomposition; (2) refinement workflow; (3) dependency and readiness states; (4) queue aging and stale-item detection; (5) backlog reorder after discovery evidence.

### CH23 MVP (Minimum Viable Product)

**Reader outcome:** Define the smallest safe product or experiment that can test a material assumption and produce interpretable learning.

**Coverage:** MVP definitions and misconceptions; minimum scope; hypothesis and target segment; experiment design; quality and safety floor; learning criteria; release and measurement.

**Decision/evidence:** A reduced feature set is not an MVP unless it tests a question. Do not remove safeguards needed for privacy, accessibility, security, or trustworthy measurement.

**Diagram opportunities:** (1) assumption-to-MVP scope; (2) learning value versus implementation cost; (3) MVP experiment and success criteria; (4) minimum viable versus minimum safe boundary; (5) evidence-to-continue/pivot/stop decision.

### CH24 Metrics

**Reader outcome:** Choose product metrics that support decisions by connecting observable measures to user and business outcomes.

**Coverage:** Metric definition; leading/lagging measures; input/output/outcome distinction; funnel and cohort analysis; metric ownership; instrumentation; segmentation; gaming and unintended incentives.

**Decision/evidence:** Specify numerator, denominator, population, time window, and source. Avoid metrics that reward local optimization or hide user harm.

**Diagram opportunities:** (1) business outcome to product behavior to metric; (2) funnel with cohort drop-off; (3) leading/lagging metric tree; (4) metric definition and data lineage; (5) Goodhart-style gaming feedback loop.

### CH25 North Star Metrics

**Reader outcome:** Select a durable measure of delivered customer value and connect it to supporting inputs without treating one number as a complete strategy.

**Coverage:** North Star purpose; value metric; input metrics; time horizon; segment fit; balance metrics; governance; failure modes and revision.

**Decision/evidence:** Validate that the metric reflects repeatable customer value and cannot be improved by harmful behavior. Use guardrails for quality, trust, and long-term retention.

**Diagram opportunities:** (1) North Star and input metric tree; (2) customer value-to-business result chain; (3) balancing guardrail metrics; (4) segment comparison; (5) metric gaming and correction loop.

### CH26 Experimentation

**Reader outcome:** Design ethical, decision-oriented experiments that reduce uncertainty and produce interpretable evidence.

**Coverage:** Hypothesis; treatment/control; qualitative and quantitative experiments; randomization; exposure and instrumentation; guardrails; duration; interference; analysis and decision.

**Decision/evidence:** Ensure the experiment can distinguish outcomes, includes safety stop conditions, and answers a decision rather than merely producing a chart.

**Diagram opportunities:** (1) hypothesis-to-experiment workflow; (2) treatment/control assignment; (3) exposure and outcome data path; (4) guardrail-triggered stop; (5) experiment result to product decision.

### CH27 A/B Testing

**Reader outcome:** Implement and interpret controlled A/B tests while accounting for assignment, statistical power, interference, and operational risk.

**Coverage:** Randomization unit; exposure; primary and guardrail metrics; sample size and duration; significance versus practical effect; repeated peeking; novelty and selection effects; rollout and rollback.

**Decision/evidence:** Pre-register the hypothesis and decision rule. Do not claim causal impact when assignment, logging, or exposure is biased.

**Diagram opportunities:** (1) randomized assignment and exposure; (2) sample-size/power trade-off; (3) metric variance and effect estimate; (4) contamination/interference path; (5) test result and rollout decision.

### CH28 Prioritization (RICE, MoSCoW, Kano)

**Reader outcome:** Compare candidate work transparently using a method suited to the decision while exposing uncertainty and avoiding false precision.

**Coverage:** Reach, Impact, Confidence, Effort (RICE); Must/Should/Could/Won't (MoSCoW); Kano categories; scoring assumptions; stakeholder alignment; sensitivity; governance.

**Decision/evidence:** Scores structure a conversation. They cannot replace strategy or accountable judgment. Validate estimates and show how rankings change under uncertainty.

**Diagram opportunities:** (1) RICE score inputs and uncertainty; (2) MoSCoW scope boundary; (3) Kano satisfaction/dissatisfaction curve; (4) ranking sensitivity to estimates; (5) prioritization decision and owner.

### CH29 Pricing

**Reader outcome:** Design and test a pricing model that connects customer value, packaging, willingness to pay, and sustainable economics.

**Coverage:** Value metric; packaging and tiers; willingness-to-pay research; cost and margin; price fences; freemium/trial; discount governance; experiments and fairness.

**Decision/evidence:** Distinguish price from cost and list price from realized price. Test customer impact, unit economics, and behavior under tier thresholds.

**Diagram opportunities:** (1) value metric to package boundary; (2) tier-feature matrix; (3) willingness-to-pay distribution; (4) discount approval path; (5) price experiment and outcome measures.

### CH30 Go-to-Market

**Reader outcome:** Coordinate product, positioning, channel, sales, support, and launch readiness to reach a defined market and learn from adoption.

**Coverage:** Target segment and positioning; launch goals; channels; sales enablement; packaging; readiness; rollout; adoption and retention measurement; launch feedback.

**Decision/evidence:** Tie launch scale to operational readiness and support capacity. Separate announcement reach from activation, value realization, and retention.

**Diagram opportunities:** (1) segment-to-channel path; (2) launch readiness dependencies; (3) rollout cohorts and adoption funnel; (4) sales/support feedback loop; (5) launch metric tree.

### CH31 Customer Feedback

**Reader outcome:** Establish a reliable loop for collecting, interpreting, prioritizing, and responding to customer feedback across channels.

**Coverage:** Feedback channels; qualitative and quantitative signals; taxonomy and routing; sentiment limitations; representative sampling; privacy; response ownership; closing the loop; product decision linkage.

**Decision/evidence:** Distinguish frequency from importance and vocal-customer bias from broad need. Track disposition and response so collection does not become an unowned inbox.

**Diagram opportunities:** (1) feedback source-to-owner workflow; (2) taxonomy and routing; (3) volume-versus-severity prioritization; (4) feedback-to-product decision trace; (5) customer response and learning loop.
