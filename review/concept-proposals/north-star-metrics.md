# Concept Proposals: North Star Metrics (CH25)

**Chapter**: CH25_North_Star_Metrics.md (02_Design_Thinking_and_Product_Management)

**Status**: Staged for merge into CORE_CONCEPTS.md

---

## Concepts Owned by CH25_North_Star_Metrics

This file stages the cross-cutting concepts that CH25 introduces and owns according to STYLE_GUIDE.md concept ownership rules. These concepts will be merged into CORE_CONCEPTS.md and other chapters must recap+link, never re-teach.

---

### 1. North Star Metric

**Definition**: A single, quantitative measure of core customer value — typically growth in a key behavior or outcome — that an organization selects as the primary focal point for all product, engineering, and operational decisions for a defined time horizon (usually one to three years).

**Scope**: 
- This concept is fully owned and taught by CH25.
- Other chapters referencing North Star Metrics (e.g., [Product Strategy](../CH15_Product_Strategy.md)) should recap in 2-3 sentences and link to [CH25, Section 4.1](../CH25_North_Star_Metrics.md#41-north-star-metric-definition-mechanism-and-organizational-role).
- Do NOT re-teach North Star Metric selection, cascade mechanics, or governance in other chapters.

**Architectural/Product Decision Implications** (taught in CH25 Section 4.1):
- Organizations with multiple product teams face a structural alignment problem if each team optimizes locally without a shared focal point.
- A North Star Metric solves this by providing a single measure all teams evaluate their work against.
- Organizations without a North Star typically regress to HiPPO (highest-paid person's opinion) prioritization.

---

### 2. North Star Selection Frameworks

**Definition**: Systematic approaches for choosing which single metric to elevate to North Star status, using one or more of three complementary frameworks: Contextual (grounded in customer value and business model), Strategic (aligned with company strategy), and Opportunity-Based (grounded in competitive positioning).

**Scope**: 
- This concept is fully owned and taught by CH25, Section 4.3.
- Each framework (Contextual, Strategic, Opportunity-Based) is distinct and mutually-reinforcing.
- The Contextual Framework operationalizes [Product Strategy](../CH15_Product_Strategy.md)'s Jobs-to-be-Done (JTBD) concepts; CH25 uses JTBD as a selection lens without re-teaching it.
- Other chapters must not re-invent North Star selection frameworks; refer to CH25.

**Key Concepts**:
- **Contextual Framework**: Use the product's core Job-to-be-Done to identify outcome metrics customers perceive as valuable.
- **Strategic Framework**: Align the North Star to the company's stated competitive advantage.
- **Opportunity-Based Framework**: Ground the North Star in market positioning and defensibility against competitive threats.

---

### 3. North Star Metrics vs. OKRs Arbitration and Synchronized Governance

**Definition**: The operational discipline of managing the relationship between organization-wide North Star Metric optimization and team-level Objectives and Key Results (OKRs), which operate on different time horizons and scopes. Arbitration rules resolve conflicts when North Star optimization and OKR-driven work point in different directions.

**Scope**:
- This concept is fully owned and taught by CH25, Section 4.4.
- [Product Strategy](../CH15_Product_Strategy.md) owns the definition and structure of OKRs per se; CH25 does not re-teach OKRs.
- Arbitration is CH25's unique contribution: the explicit governance process for reconciling the two.

**Key Decision Rules** (taught in Section 4.4):
- **Strong Alignment**: OKR predicted to increase North Star materially → approve with top priority.
- **Weak Alignment**: OKR moves North Star but inefficiently → approve at lower priority; explore alternatives.
- **Orthogonal**: OKR does not impact North Star (either positively or negatively) but is strategically important → approve selectively.
- **Conflicting**: OKR predicted to decrease North Star → block or fundamentally renegotiate.

---

### 4. The North Star Cascade

**Definition**: The multi-tier system of metrics flowing from a single company-level North Star Metric down through product lines, platforms, and individual teams, with each tier translating the company North Star into locally-actionable, measurable proxy metrics that teams can optimize directly without losing alignment to the global signal.

**Scope**:
- This concept is fully owned and taught by CH25, Section 4.5.
- Cascade design is a structural decision that prevents multi-product organizations from having one product cannibalize another's roadmap.
- [Metrics](../CH24_Metrics.md) chapter owns the definition and calculation of underlying Input/Output metric trees; CH25 layers the cascade strategy on top.

**Key Principles**:
- Monotonic Alignment: If team-level proxy metrics improve, product-line North Stars must improve.
- Aggregation Consistency: When all team metrics improve, the product-line North Star must improve.
- Isolation Principle: A team's proxy metric should be under the team's control.
- Feedback Loop Speed: Team-level proxy metrics should provide feedback on timescales of days to weeks.

---

### 5. North Star Metric Lifecycle: Selection, Evolution, Retirement, and Pivoting

**Definition**: The operational progression a North Star Metric follows from initial selection, through active optimization, to evolution or retirement as market, business model, or customer needs change. Includes phases: Selection, Launch, Active Optimization, Plateau/Risk Evaluation, Evolution, Transition, or Retirement/Sunsetting.

**Scope**:
- This concept is fully owned and taught by CH25, Section 4.6.
- Lifecycle discipline prevents "zombie North Star" anti-patterns where organizations continue optimizing a metric long after it has lost relevance.

**Key Phases**:
- **Selection** (2–4 weeks): Candidate identification, vetting, telemetry verification.
- **Launch** (1–2 weeks): Company-wide announcement and team training.
- **Active Optimization** (12–36 months typical): Teams align OKRs, roadmap initiatives evaluated on predicted North Star impact.
- **Plateau/Risk Signal**: Metric flattens, market shifts, or causal connection weakens.
- **Evaluation** (2–4 weeks): Diagnostic — is plateau due to saturation or inadequacy?
- **Evolution or Retirement**: Transition phase (1–2 quarters of dual-tracking) or formal sunsetting.

---

### 6. Multi-Product and Cross-Product North Star Structures

**Definition**: Organizational frameworks for defining and governing North Star Metrics across companies that operate multiple independent or interdependent products, where a single company-level metric is insufficient to prevent one product from cannibalizing another's roadmap or market.

**Scope**:
- This concept is fully owned and taught by CH25, Section 4.7.
- Solves the problem that a single umbrella metric (e.g., "Total Revenue") does not guide individual product teams in multi-product companies.
- Proposes a tiered structure: Company-level + Product-line-level + Platform Health (optional).

**Key Principles**:
- One North Star Per Autonomous Product Line: Autonomous products get their own North Stars.
- Platform Health North Star: If products are intended to be purchased together, measure cross-product adoption.
- Explicit Arbitration Rules: Define how to prioritize when product-line North Stars conflict.

---

### 7. North Star Telemetry Foundation

**Definition**: The end-to-end instrumentation pipeline — event schemas, collection infrastructure, data warehousing, schema validation, and metric calculation procedures — that makes measuring a North Star Metric reliable, repeatable, and attributable to specific product changes.

**Scope**:
- This concept is owned jointly with [Metrics](../CH24_Metrics.md#4-core-concepts), which owns broader telemetry architecture and metric instrumentation.
- CH25 Section 4.2 teaches the North Star-specific telemetry requirements: event schema contracts, metric definition versioning, aggregation boundaries, data quality assertions.
- [Metrics](../CH24_Metrics.md) teaches the underlying event collection, streaming, and time-series storage; CH25 assumes those exist and focuses on North Star-specific quality gates.

**North Star-Specific Requirements**:
- Explicit, versioned metric definition (SQL formula) stored in version control.
- Data quality checks to detect sudden deviations from expected range.
- Historical data retention for ≥12–24 months.
- Aggregation consistency across time granularities (daily, weekly, monthly).

---

## Boundary Clarifications (Anti-Repetition)

The following concepts are explicitly NOT owned by CH25:

### Already Owned by [Metrics](../CH24_Metrics.md):
- **Input/Output Metric Trees**: Taxonomy of metrics at different stages of the user journey/product pipeline.
- **HEART Framework** (Happiness, Engagement, Adoption, Retention, Task Success): Structured categorization of user experience metrics.
- **AARRR Acquisition Funnel** (Acquisition, Activation, Retention, Referral, Revenue): Funnel taxonomy for SaaS companies.
- **Counter-Metrics and Guardrail Metrics**: Metrics that must not degrade as the North Star improves.
- **Telemetry Architecture** (event collection, streaming, data warehousing): Infrastructure for capturing and storing behavioral data.
- **Vanity Metrics vs. Actionable Metrics**: Distinction between metrics that feel good but don't predict business outcomes vs. metrics that drive decisions.

### Already Owned by [Product Strategy](../CH15_Product_Strategy.md):
- **Objectives and Key Results (OKRs) as a strategy-execution cascade**: Quarterly goal-setting framework.
- **Jobs-to-be-Done (JTBD)**: Customer value framework used by CH25 as a North Star selection lens.

### Deferred to Future Chapters:
- **Experimentation and Hypothesis Design**: [Experimentation](chapters not yet drafted) owns how to design experiments to improve North Star Metrics.
- **A/B Testing and Statistical Significance**: [A/B Testing](chapters not yet drafted) owns sample allocation, sequential testing, and significance calculation.
- **Roadmap Construction**: [Roadmaps](../CH21_Roadmaps.md) owns the artifact and governance of sequencing work; CH25 teaches how North Star Metrics inform roadmap prioritization.
- **Backlog and Story Management**: [Backlog](chapters not yet drafted) owns ticket-level work sequencing.

---

## Revision History

- **2026-08-01**: Initial staging. All 7 concepts proposed for merge into CORE_CONCEPTS.md.

---
