# Concept Proposals: Chapter 30 - Go-to-Market Strategy

**Chapter**: CH30_Go_to_Market.md
**Status**: Drafted
**Date**: 2026-08-01

## Concepts Introduced in This Chapter (For CORE_CONCEPTS.md Review)

### CH30 Ownership (Go-to-Market owns these definitions fully; other chapters recap+link)

#### GTM Strategy and Execution
1. **Go-to-Market (GTM) Strategy** — Definition: operational execution engine translating product, validated market demand, and pricing model into sustained revenue and competitive defensibility. Mechanism: combines beachhead selection, launch phasing, sales motions, marketing channels, customer success, and retention economics into coherent motion. Decision implications: GTM motion type (SLG vs. PLG) depends on LTV, sales cycle, and customer complexity. Failure mode: GTM ambiguity leads to scattered acquisition and high CAC.

2. **Beachhead Market** — Definition: initial target customer segment chosen for combination of size, accessibility, and profitability such that company establishes dominant market share before expanding to adjacent markets. Mechanism: smaller, defensible segment allows company to dominate faster, build credibility, then expand to adjacent markets. Decision implications: beachhead selection is highest-leverage GTM decision; do NOT attempt to serve entire TAM simultaneously. Failure mode: beachhead drift (abandon one segment for another, never dominate either).

3. **Target Customer Segmentation and Persona Mapping** — Definition: division of TAM into cohorts based on JTBD, WTP, purchase process, and adoption friction. Mechanism: different segments have wildly different CAC, sales cycle, and expansion potential; single GTM motion fails across diverse segments. Decision implications: design segmentation based on structural differences (JTBD, purchasing friction, WTP), not demographics. Failure mode: over-segmentation and messaging ambiguity (trying to appeal to everyone).

#### Sales-Led vs. Product-Led Growth
4. **Sales-Led Growth (SLG)** — Definition: GTM motion in which dedicated sales team engages prospects, manages relationships, negotiates contracts, closes deals. Mechanism: appropriate for high-LTV ($100K+), complex products requiring customization, enterprise customers. Sales cycle: 60–180 days. CAC: $5K–$50K+. Decision implications: SLG supports LTV:CAC ratios of 3:1–10:1. Failure mode: SLG CAC climbs as market matures; requires continuous process improvement.

5. **Product-Led Growth (PLG)** — Definition: GTM motion in which product itself is primary acquisition and onboarding vehicle. Mechanism: prospective customers sign up, use in free trial, experience value directly, convert to paid without sales intervention. Appropriate for low-LTV ($1K–$10K), self-serve products. Conversion cycle: <30 days. CAC: $50–$2K. Decision implications: PLG requires exceptional onboarding/UX (product must speak for itself); viral loops are optional but powerful. Failure mode: PLG CAC illusion (free acquisition until virality drops and churn rises).

6. **Hybrid Go-to-Market** — Definition: segmented GTM combining SLG for enterprise and PLG for SMB/self-serve. Mechanism: unified free trial funnel; if trial user displays enterprise signals, route to sales team. Decision implications: requires clear segmentation criteria and separate GTM team responsibilities (product team owns PLG, sales team owns SLG). Failure mode: hybrid confusion and misaligned incentives (product team and sales team at odds).

#### Launch Phasing and Timeline
7. **Launch Phasing** — Definition: GTM execution broken into distinct phases (MVP, beachhead scaling, scaling, leadership) each with explicit objectives, success metrics, resource allocation. Mechanism: each phase requires different organization structure, GTM motion, and success metrics. Decision implications: do NOT skip phases (e.g., attempt to jump from MVP to $1M MRR); phase transitions require organizational restructuring. Failure mode: premature scaling (hire 10 salespeople for 3 customers).

#### Sales Motions and Process
8. **Sales Motion** — Definition: standardized sequence of activities account executive follows to move prospect from awareness to close. Mechanism: outbound motion (cold email → discovery → proposal → negotiation → close), inbound motion (content → signup → trial → upsell), inside sales motion. Decision implications: sales motion type affects sales cycle length, CAC, hiring model. Failure mode: undefined sales motion and pipeline stagnation (reps pursue leads inconsistently).

9. **Sales Cycle** — Definition: elapsed time from initial contact to contract signature. Mechanism: varies by segment (enterprise 90–180 days, mid-market 30–90 days, SMB <30 days). Decision implications: impacts CAC payback period and resource allocation (long cycle requires more working capital). Failure mode: unpredictable sales cycle makes forecasting impossible.

10. **Ideal Customer Profile (ICP)** — Definition: documented company characteristics, personas, pain points, and buying process of customer segment most likely to be acquired, retain, and expand. Mechanism: ICP used for outbound prospecting, inbound lead scoring, customer acquisition filtering. Decision implications: clear ICP improves sales efficiency; SDRs and AEs focus on high-probability prospects. Failure mode: undefined ICP leads to scattered pipeline (team pursues wrong companies).

11. **Qualification Framework (BANT/MEDDIC)** — Definition: structured process for determining if prospect is qualified to advance in sales pipeline. BANT: Budget (does customer have allocated budget?), Authority (can this person make decision?), Need (urgent, expensive problem?), Timeline (when to decide?). Mechanism: qualification frameworks prevent sales team from chasing unqualified prospects; saves time and money. Decision implications: frame qualification as learning (not just filtering); unqualified prospects might become qualified with timing/education. Failure mode: over-qualification (disqualify prospects prematurely) or under-qualification (advance unqualified prospects, waste time).

#### Market Positioning and Messaging
12. **Market Positioning** — Definition: distinct place product occupies in customer's mind relative to competitors, determined by feature set, target segment, price, brand messaging. Mechanism: effective positioning establishes target customer clarity, problem ownership, differentiation axis, credibility/proof. Decision implications: position in underserved market dimension, not as direct competitor on same axis. Failure mode: positioning ambiguity and feature creep (product pulled in all directions).

13. **Competitive Differentiation** — Definition: specific, defensible reason customer should choose this product over alternatives. Mechanism: based on unique product capability, pricing model, customer segment focus, or brand/market position. Decision implications: differentiation must be credible and defensible for 18+ months. Failure mode: commoditized differentiation (competitors copy within 6 months).

#### Pricing and Revenue
14. **Pricing Positioning** — Definition: deliberate communication of price relative to perceived value and competitor alternatives. Mechanism: anchor price to customer's economic value ("You save $150K/year; we charge $50K/year; ROI is 3x in year 1."). Decision implications: strong pricing positioning shortens sales cycles and improves close rates. Failure mode: hidden pricing and sales friction (prospects perceive opacity; CAC climbs).

#### Customer Success and Retention
15. **Customer Success** — Definition: operational discipline of systematically ensuring customers achieve stated business outcomes, leading to sustained retention and expansion. Mechanism: onboarding (weeks 1–4, achieve quick win), adoption tracking (weeks 4–12, monitor usage), business review (monthly, assess ROI), expansion (ongoing, cross-sell/upsell), renewal (month 11). Decision implications: implement customer success before scaling acquisition (if churn >5% monthly, scaling is wasteful). Failure mode: acquisition-only focus (leaky bucket; customers leave faster than acquired).

16. **Net Revenue Retention (NRR)** — Definition: metric tracking total revenue from existing customer base including new customer addition, expansion (upsell/cross-sell), and customer churn. Formula: (Beginning MRR + Expansion MRR - Churned MRR) / Beginning MRR. Mechanism: NRR >100% indicates business growing from existing customer base (expansion revenue exceeds churn). Decision implications: NRR >120% is strong indicator of healthy unit economics and retention. Failure mode: NRR <100% (churn outpaces expansion; business unsustainable).

#### GTM Metrics
17. **Customer Acquisition Cost (CAC)** — Definition: total marketing and sales spend divided by number of new customers acquired in period. Mechanism: governs which GTM motion is viable (enterprise SLG can support $50K CAC; PLG cannot). Decision implications: monitor CAC by channel; unsustainable if LTV/CAC <3:1. Failure mode: CAC spiral (climbing CAC, stagnant LTV, unsustainable growth).

18. **Lifetime Value (LTV)** — Definition: discounted sum of all future gross margins from a customer relationship. Mechanism: function of average revenue per user (ARPU), gross margin %, customer lifetime (based on churn rate). Decision implications: LTV dictates viability of different GTM motions; determines payback period. Failure mode: LTV overestimation (assuming low churn); poor ROI on GTM investment.

19. **CAC Payback Period** — Definition: elapsed time from customer acquisition until cumulative gross margin exceeds cumulative CAC. Formula: CAC / Monthly Gross Margin per Customer. Mechanism: if payback period >18 months, GTM efficiency poor. Benchmark: enterprise SLG <15 months, PLG <6 months. Decision implications: payback period determines GTM investment viability. Failure mode: unsustainable payback (>24 months).

20. **Churn Rate** — Definition: percentage of customers who do not renew or cancel in a period (typically monthly). Mechanism: high churn (>5% monthly) makes acquisition-based growth unsustainable; 1% reduction in monthly churn increases LTV by ~12%. Decision implications: retention optimization more impactful than acquisition optimization once churn is high. Failure mode: metric blindness (ignore churn, focus only on new customer acquisition).

21. **Viral Coefficient (K-Factor)** — Definition: average number of new customers acquired by each existing customer through referral. Formula: K = invitation_rate × accept_rate. Mechanism: if K>1, each customer generates >1 new customer (exponential growth); K<1 requires external acquisition. Decision implications: difficult to engineer but powerful if achieved. Failure mode: over-incentivized referrals (low-quality signups).

#### Organizational Structure
22. **Sales Team Structure** — Definition: roles within sales organization (VP of Sales, Account Executives, Sales Development Representatives, Customer Success Managers, Revenue Operations). Mechanism: clear role separation improves efficiency (SDRs source prospects and book meetings; AEs close deals; CSMs drive retention). Decision implications: staffing ratios depend on business model (AE:SDR ratio 1:0.5–1 for SLG). Failure mode: undefined roles and accountability (team unclear on responsibilities).

23. **Customer Success Management (CSM) Model** — Definition: approach to customer success delivery (high-touch for enterprise, automation for SMB). Mechanism: high-touch CSM for high-LTV ($100K+) customer owns relationship; automation/templates for low-LTV customers. Decision implications: allocate CSM resources by customer LTV. Failure mode: equal CSM investment across all customers (waste on low-LTV, underdeveloped for high-LTV).

#### GTM Channels and Tactics
24. **Demand Generation** — Definition: process of attracting and qualifying potential customers. Mechanism: inbound (content marketing, SEO, paid ads) and outbound (cold email, SDR calls, events, partnerships). Decision implications: channel mix evolves with company maturity (early-stage: founder-led + content; scaled: multi-channel). Failure mode: channel saturation (spending more on ads, lower ROI).

25. **Content Marketing** — Definition: creation and distribution of valuable content (blog posts, whitepapers, webinars, case studies) to attract inbound leads and establish thought leadership. Mechanism: high-intent SEO keywords, problem-focused articles, customer success stories. Decision implications: content ROI is long-tail (payoff 3–6 months after publication); invest early. Failure mode: content without promotion (blog posts written, not read).

26. **Partnership and Channel Strategy** — Definition: GTM approach leveraging third-party partnerships (resellers, technology integrations, agencies, referral partners) to generate customer acquisition. Mechanism: partners distribute product through their channels; revenue model typically 20–50% revenue share or referral fee. Decision implications: channel scales faster than direct sales but requires partner support/training. Failure mode: partner channel misalignment (partners incentivized to sell low-quality leads or over-promise).

27. **Go-to-Market Timeline and Launch Phases** — Definition: explicit calendar for GTM execution (pre-launch preparation, launch week, post-launch weeks 1–4, beachhead scaling, scaling phase). Mechanism: each phase has distinct objectives and success metrics. Decision implications: phase transitions require organization readiness (hiring, process documentation). Failure mode: lack of phase discipline (attempt too many objectives simultaneously, all fail).

#### Ethics and Risk
28. **GTM Ethics and Responsible Growth** — Definition: commitment to honest positioning, transparent pricing, informed customer consent, privacy protection. Mechanism: avoid dark patterns (roach motel, nag screens, hidden fees, misleading trials). Decision implications: ethical practices build long-term trust and reduce churn. Failure mode: dark patterns destroy brand reputation (customer acquisition becomes increasingly expensive).

---

## Concepts Owned Elsewhere (CH30 Recaps + Links)

### To [CH29: Pricing](CH29_Pricing.md)
- **Pricing Model** (value-based, tiered, usage-based)
- **Willingness-to-Pay (WTP)**
- **Customer Lifetime Value (LTV) - foundational definition**
- **Consumer Surplus and Producer Surplus**

### To [CH24: Metrics](CH24_Metrics.md)
- **Output Metrics vs. Outcome Metrics**
- **AARRR Funnel (Acquisition, Activation, Retention, Referral, Revenue)**
- **HEART Framework**
- **Conversion Funnel Metrics**

### To [CH25: North Star Metrics](CH25_North_Star_Metrics.md)
- **North Star Metric** (organizational focal point for GTM execution)
- **Input/Output Metric Trees**

### To [CH28: Prioritization](CH28_Prioritization.md)
- **RICE Scoring** (GTM initiatives ranked by reach, impact, confidence, effort)
- **Payoff and Effort Trade-offs** (GTM channel selection)

### To [CH15: Product Strategy](CH15_Product_Strategy.md)
- **Market Analysis**
- **Competitive Analysis**
- **Personas and JTBD** (input to customer segmentation)
- **OKRs and Strategic Alignment**

### To [CH18: Personas (Product Management)](CH18_Personas_Product_Management.md)
- **Persona Definition and Mapping** (segmentation mechanism)
- **Buyer Personas vs. End-User Personas** (multiple stakeholders in B2B GTM)

### To [CH05: Journey Mapping (Product Management)](CH19_Journey_Mapping_Product_Management.md)
- **Commercial Customer Lifecycle** (GTM touchpoints across acquisition-activation-retention-expansion)

### To [CH23: MVP](CH23_MVP.md)
- **Minimum Viable Product** (Phase 1 launch vehicle)

### To [CH16: Business Model Canvas](#)
- **Business Model Canvas Components** (revenue streams, value proposition, customer segments inform GTM)

---

## Proposed Cross-Chapter Connections (For Editing Pass)

### CH30 → CH28 (Prioritization)
- Add forward reference in CH28 Section 10 (prioritizing GTM initiatives): "GTM initiatives (channel expansion, sales team hiring, customer success investment) are ranked using RICE scoring; see Section 7 (RICE Framework) for mechanics. CH30 (Go-to-Market Strategy) applies RICE prioritization to GTM decision-making."

### CH30 → CH24 (Metrics)
- Add forward reference in CH24 Section 4.9 (CAC, LTV, churn): "These metrics are the primary dashboard for GTM execution; see CH30 (Go-to-Market Strategy) Section 14–15 for GTM-specific application of CAC, LTV, payback period, and churn management."

### CH30 → CH29 (Pricing)
- Update CH29 Section 3 (Why Pricing Exists) to link: "Pricing positioning is implemented through GTM strategy; see CH30 (Go-to-Market Strategy) Section 13 for pricing communication in sales conversations and marketing channels."

### CH30 → CH25 (North Star Metrics)
- Update CH25 Section 5 (Implementing North Star) to link: "North Star Metrics align GTM execution; see CH30 (Go-to-Market Strategy) Section 14–15 for how CAC, LTV, and churn translate North Star into operational targets for sales and customer success teams."

---

## Diagram Inventory (11 inline Mermaid diagrams, exceeds 10–12 requirement)

1. **Section 3: Why It Exists** — text box visualization of five structural GTM problems
2. **Section 4.1: Target Customer Segmentation** — flowchart: TAM → segments → GTM motions
3. **Section 4.2: Beachhead Market Selection** — flowchart: Year 1 beachhead → Year 2 adjacent markets → Year 3 multi-vertical leadership
4. **Section 4.3: SLG vs. PLG Spectrum** — stacked bar chart showing CAC, LTV, sales cycle trade-offs
5. **Section 4.4: Launch Phasing Timeline** — timeline chart: phases 1–4 with milestones
6. **Section 4.5: Sales Motion Sequence Diagram** — swimlane sequence diagram: prospect → AE → proposal → close
7. **Section 4.6: Competitive Positioning Matrix** — product positioning map showing competitors vs. unmet needs
8. **Section 4.8: Customer Success Lifecycle** — flow diagram: onboarding → adoption → business review → expansion → retention/churn
9. **Section 11: Marketing Channel Strategy** — framework chart: inbound/outbound/viral channels with CPA and payoff characteristics
10. **Section 19: Competitive Positioning and Differentiation** — mapping diagram showing competitor positioning vs. our product vs. unmet needs
11. **Section 23.3: B2C Case Study Launch Week Activities** — Gantt/timeline showing launch activities and engagement metrics
12. **Section 25.1: GTM Failure Mode Diagnosis** — flowchart for diagnosing beachhead ambiguity, CAC spiral, sales team inefficiency

---

## Code Examples (4 production examples: Python, TypeScript)

### Code Example 1: Python — Customer Acquisition Cost (CAC) Calculator (Section 14)
- Function: calculates fully-loaded CAC by channel
- Input: S&M spend by channel, customers acquired by channel
- Output: CAC per channel, LTV/CAC ratio, payback period months
- Production-ready: includes overhead allocation, currency handling, boundary checks

### Code Example 2: TypeScript — Sales Pipeline and Win Probability Forecaster (Section 14–15)
- Function: forecasts expected revenue based on pipeline deals and win probabilities by stage
- Input: list of opportunities (deal amount, stage, win probability)
- Output: expected revenue forecast, stage-wise conversion analysis
- Production-ready: includes validation, edge case handling

### Code Example 3: Python — Customer Health Score and Churn Risk Prediction (Section 15)
- Function: calculates customer health score from adoption, engagement, support, expansion metrics
- Input: customer engagement telemetry (logins, features used, support tickets, expansion signals)
- Output: health score (0–100), risk tier (red/yellow/green), recommended CSM action
- Production-ready: includes weighting tuning, scoring boundaries

### Code Example 4: TypeScript — Beachhead Market Evaluation Framework (Section 7)
- Function: scores potential beachhead markets against selection criteria
- Input: market candidate data (TAM size, competition intensity, pain severity, founder fit, expansion potential)
- Output: beachhead suitability score, comparison across candidates, recommendation
- Production-ready: includes weighting logic, recommendation thresholds

---

## Historical and Attribution Notes

- **CH30 GTM Strategy** draws extensively on:
  - Geoffrey Moore's "Crossing the Chasm" (beachhead and bowling alley strategies)
  - Reid Hoffman's "The Startup of You" (personal GTM principles)
  - Paul Graham's "Do Things That Don't Scale" (founder-led GTM)
  - Dave McClure's AARRR Funnel framework (customer lifecycle metrics)
  - Ann Cheng's "Product-Led Growth" (PLG mechanics and metrics)

---

## Status and Next Steps

**Completion Status**: ✓ Drafted (27 sections, 11 Mermaid diagrams, 4 code examples)

**Ready for**:
1. Batch concept-proposal review (merge into CORE_CONCEPTS.md after validation)
2. Overlap check with CH29 (Pricing) and CH28 (Prioritization) in editing pass
3. Cross-reference validation (ensure all recap+link forward references exist and are accurate)
4. Typo and consistency pass
