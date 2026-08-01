# Concept Proposals — Chapter 28: Prioritization

Staged concepts introduced in CH28, ownership statements for merge into CORE_CONCEPTS.md.

## New Concepts (Owned by CH28)

- **RICE Scoring (Reach, Impact, Confidence, Effort)**: A quantitative prioritization formula where score = (Reach × Impact × Confidence) / Effort; operationalizes customer impact, confidence level in estimates, and engineering effort into a single comparable metric; foundational framework in modern product management for ranking feature value-per-engineering-hour.

- **MoSCoW Prioritization (Must/Should/Could/Won't)**: A stakeholder alignment framework that categorizes backlog items into four buckets (MUST = business-critical, SHOULD = high-value, COULD = nice-to-have, WON'T = deferred) to manage scope negotiation and capacity allocation; solves release planning and enterprise roadmap consensus problems.

- **Kano Model (Basic/Performance/Delighter)**: A feature categorization framework that maps customer satisfaction curves to feature types (Basic: absence causes dissatisfaction but presence creates neutrality; Performance: linear satisfaction increase; Delighter: presence creates disproportionate joy, absence creates disappointment); predicts feature evolution (delighters become performance features, then basic over time).

- **Eisenhower Matrix (Urgency vs. Importance)**: A two-axis prioritization framework that classifies work into four quadrants (Q1: Urgent + Important = crisis; Q2: Not Urgent + Important = strategic work; Q3: Urgent + Not Important = interruptions; Q4: Not Important + Not Urgent = waste); surfacing that organizations spend 80% capacity on Q1+Q3 but competitive advantage is built in Q2.

- **Composite Prioritization**: An orchestration pattern that applies multiple prioritization frameworks to different item types (RICE for user stories, MoSCoW for scope, Kano for satisfaction positioning, Cost-of-Delay for financial impact, Eisenhower for urgency), then aggregates signals into a unified ranking and detects veto scenarios (framework conflicts that require stakeholder escalation).

- **Cost-of-Delay (CoD)**: A financial framework that quantifies monthly business impact (revenue, metric, or risk) of deferring an item; prioritization by CoD/Effort ratio surfaces which items create the most value per engineering week; grounds opportunity cost reasoning in measurable terms.

- **Prioritization ROI**: The ratio of RICE score (or equivalent impact measure) to effort (person-weeks), used to compare value-per-engineering-hour across items; enables capacity-constrained portfolio optimization where high-ROI items are scheduled first and lower-ROI items are deferred.

- **Veto Mechanism**: An explicit, documented override of quantitative prioritization by a stakeholder with authority (e.g., VP Product, CTO, CEO) when organizational context (legal, competitive, strategic) diverges from the framework; tracked as precedent to detect if frameworks need recalibration.

- **Prioritization Trigger**: A mid-quarter signal (scope change, technical bottleneck, metric surprise, competitive threat, capacity change) that justifies re-running prioritization to reshuffle backlog rankings; prevents static prioritization from drifting when conditions change.

- **Backlog Re-Prioritization**: The process of revisiting and reranking backlog items when prioritization triggers emerge; mechanically distinct from quarterly prioritization (which is comprehensive) vs. tactical (which addresses specific escalations mid-cycle).

- **Reach Estimate (RICE)**: The count or percentage of users/customers affected by a feature per time period (e.g., monthly); calibrated against historical precedent; subject to inflation bias; requires validation via user research or A/B test control groups.

- **Impact Score (RICE)**: The ordinal magnitude of value delivered to each affected user (1 = Minimal, 2 = Medium, 3 = Major); defined in terms of user outcome change (time saved, revenue enabled, frustration reduced); distinct from Kano impact (satisfaction curves) and business impact (revenue, retention).

- **Confidence Level (RICE)**: A percentage (typically 10%, 25%, 50%, 75%, 90%, 100%) representing estimation uncertainty; penalizes speculative items by scaling the score; calibrated to the degree of customer research, market validation, or historical data supporting Reach and Impact estimates.

- **Effort Estimation (RICE)**: The engineering cost to implement an item, typically in person-weeks or story points; includes implementation, testing, documentation, and deployment; subject to underestimation bias; discipline requires 20–30% buffer and senior engineering input.

- **Kano Validation Survey**: A two-question user research instrument ("How would you feel if this feature were present?" and "If absent?") used to categorize features into Basic/Performance/Delighter based on satisfaction curve analysis; mitigates team bias in Kano classification.

- **Stakeholder Negotiation in Prioritization**: The interpersonal and decision-making process of reconciling competing stakeholder value systems (Product maximizes satisfaction, Engineering minimizes debt, Finance maximizes revenue, Sales maximizes commitments) when frameworks conflict; requires structured, documented conflict resolution (e.g., escalation veto, cost-of-delay reasoning).

- **Capacity Allocation (MoSCoW / Composite)**: The division of quarterly engineering capacity into MUST/SHOULD/COULD/WON'T buckets (typically 50–70% MUST, 20–30% SHOULD, 5–10% COULD); enforces ruthless triage and prevents capacity overcommitment; requires 20% contingency buffer for interruptions.

- **Framework Selection Decision Tree**: A meta-framework that guides practitioners on which prioritization method to use for which item type (RICE for features, MoSCoW for enterprise scope, Kano for satisfaction positioning, Eisenhower for urgency triage, Cost-of-Delay for financial items); prevents framework warfare and ensures consistency.

- **Prioritization Anomaly Detection**: Automated flagging of unusual score patterns (e.g., high-effort items with perfect confidence, low-confidence items with high reach estimates, minimal-impact features proposed as strategic) that signal estimation bias and warrant re-discussion.

- **ROI Tier**: A categorization bucket for composite prioritization scores (Tier 1: Score > 500 or ROI > $100K/week; Tier 2: 200–500 or ROI $10K–$100K/week; Tier 3: 50–200 or ROI $1K–$10K/week; Tier 4: < 50 or ROI < $1K/week) enabling teams to quickly identify priority brackets without full detailed scoring.
