# Pricing — Concept Ownership Proposals

This file proposes new concept ownership entries that should be merged into [CORE_CONCEPTS.md](../../CORE_CONCEPTS.md) after batch review completes. See the [Concept Ownership Rule](../../STYLE_GUIDE.md#concept-ownership-rule-anti-repetition) in STYLE_GUIDE.md.

## New Concepts Introduced in CH29 (Pricing)

| Concept | Owning Chapter | Scope | Notes |
|---|---|---|---|
| **Value-based pricing** | [CH29: Pricing](../02_Design_Thinking_and_Product_Management/CH29_Pricing.md#41-value-based-pricing) | WTP (Willingness-to-Pay) elicitation, pricing ceiling vs. cost floor, consumer surplus vs. producer surplus | Core mechanism: aligning price to value delivered; includes methodology for segment-specific WTP research (conjoint analysis, van Westendorp). Other chapters recap + link when discussing revenue models or unit economics. |
| **Willingness-to-Pay (WTP)** | [CH29: Pricing](../02_Design_Thinking_and_Product_Management/CH29_Pricing.md#41-value-based-pricing) | Customer's maximum price; survey/interview techniques; segment variance | Foundation for value-based pricing; used throughout pricing decisions. Economics primer owned by this chapter; application in other models (freemium, tiered) recap + link. |
| **Cost-plus and cost-minus pricing** | [CH29: Pricing](../02_Design_Thinking_and_Product_Management/CH29_Pricing.md#42-cost-plus-and-cost-minus-pricing) | Markup mechanics, margin targets, negotiation anchors | Accounting/operational mechanics; used as comparison baseline to value-based pricing. Other chapters recap + link when discussing cost structure. |
| **Freemium models** | [CH29: Pricing](../02_Design_Thinking_and_Product_Management/CH29_Pricing.md#43-freemium-models) | Free tier scope, conversion funnel design, friction-wall mechanics, CAC (Customer Acquisition Cost) subsidy calculation | Full teaching: why freemium works, when it applies (high-volume B2C), conversion funnel expectations (3–10% B2C, 2–15% B2B). Operationally tightly linked to [CH24: Metrics](#) churn/retention and [future CH30: Go-to-Market](#). Other chapters recap + link. |
| **Tiered pricing (good/better/best)** | [CH29: Pricing](../02_Design_Thinking_and_Product_Management/CH29_Pricing.md#44-tiered-pricing-goodbetterbest) | Discrete price points, feature bundling, price anchoring psychology (anchor effect, compromise effect), tier-boundary design | Psychology + mechanics: how customers self-select into tiers via anchoring and feature perception. Links to pricing psychology (anchoring) and behavioral economics. Other chapters recap + link when discussing market segmentation or revenue levers. |
| **Usage-based/metered pricing** | [CH29: Pricing](../02_Design_Thinking_and_Product_Management/CH29_Pricing.md#45-per-unitusage-based-pricing) | Unit definition (API calls, MB, transactions), metering architecture, billing calculation, bill-shock mitigation, hybrid models (base + overage) | Full teaching: mechanism, incentive alignment, operational challenges (usage unpredictability), hybrid strategies to reduce bill shock. Architecturally important: metering requires event logging, aggregation pipeline, billing system integration. Other chapters recap + link. |
| **Subscription vs. perpetual licensing** | [CH29: Pricing](../02_Design_Thinking_and_Product_Management/CH29_Pricing.md#46-subscription-vs-perpetual-licensing) | Recurring revenue model, cash-flow timing, switching costs, feature upgrade incentives, SaaS business model | Distinct models with different unit economics and operator incentives. This chapter owns the conceptual distinction; [CH24: Metrics](#) owns MRR and recurring revenue tracking; operations owns billing system implementation. Other chapters recap + link. |
| **Geographic and segment pricing** | [CH29: Pricing](../02_Design_Thinking_and_Product_Management/CH29_Pricing.md#48-geographic-and-segment-pricing) | Region-specific pricing, PPP (Purchasing Power Parity), gray-market arbitrage, segment-specific WTP | Exploits WTP variance across geographies and customer types (startup/mid-market/enterprise). Regulatory and operational risks (arbitrage, fairness perception). Architecturally requires conditional pricing logic in billing system. |
| **Launch pricing strategies (skimming vs. penetration)** | [CH29: Pricing](../02_Design_Thinking_and_Product_Management/CH29_Pricing.md#49-launch-pricing-skimming-vs-penetration) | High-price launch targeting early adopters vs. low-price launch for market share; network effects and switching costs as moderating factors | Strategic choice driven by product characteristics (differentiation, network effects, competitive intensity). Integrated with go-to-market strategy ([future CH30](#)). Other chapters recap + link. |
| **Price elasticity of demand (PED)** | [CH29: Pricing](../02_Design_Thinking_and_Product_Management/CH29_Pricing.md#410-price-elasticity-and-demand-curves) | Elasticity definition (% qty change / % price change), elastic vs. inelastic demand, demand curves, revenue optimization | Microeconomics foundation for understanding market sensitivity to price changes. Informs whether price increases are viable (inelastic) or will trigger large churn (elastic). Other chapters recap + link when discussing pricing decisions. |
| **Pricing communication and anchoring** | [CH29: Pricing](../02_Design_Thinking_and_Product_Management/CH29_Pricing.md#411-pricing-communication-and-anchoring) | Anchoring effect (reference dependence), pricing narrative, value justification, fairness framing | Behavioral economics mechanism: how first prices shape perception of subsequent prices. Links to marketing/positioning but distinct from value-based pricing (both anchoring and value-delivery matter). Other chapters recap + link when discussing customer perception. |
| **Freemium vs. free trial vs. hybrid** | [CH29: Pricing](../02_Design_Thinking_and_Product_Management/CH29_Pricing.md#47-freemium-vs-free-trial-vs-freemium) | Time-limited free access, credit-card-required trial, hybrid free trial → freemium path | Tactical customer-acquisition mechanism; distinct from the freemium **model** above. Owned by this chapter; [future CH30: Go-to-Market](#) owns launch/positioning of trial offers. Other chapters recap + link. |

## Integration Points with Other Chapters

### Inbound (Chapters that propose concepts this chapter *recaps + links*)

- **[CH24: Metrics](../02_Design_Thinking_and_Product_Management/CH24_Metrics.md)**: LTV, CAC, churn, retention, ARPU, MRR
  - *Recap*: This chapter uses CAC/LTV to evaluate whether a pricing model's unit economics are viable (e.g., freemium conversion must yield LTV > CAC / 0.30).
  - *Link*: See [CH24](#) for full LTV/CAC definitions and instrumentation.

- **[CH16: Business Model](#)**: Revenue stream definition, unit economics, margin targets
  - *Recap*: Pricing is the operational lever for unit economics; business model sets the constraint (what revenue streams are possible?), pricing implements it.
  - *Link*: See [CH16](#) for business model alignment.

- **[CH15: Product Strategy](../02_Design_Thinking_and_Product_Management/CH15_Product_Strategy.md)**: OKRs, revenue KPIs, strategic pricing as a lever
  - *Recap*: Pricing decisions can accelerate or hinder strategic revenue outcomes (e.g., penetration pricing to achieve market-share OKR).
  - *Link*: See [CH15](#) for OKR/KPI framework.

### Outbound (Chapters that will recap + link these new concepts)

- **[future CH28: Prioritization](#)**: Uses payoff (price × market size) as a tie-breaker when competing initiatives have equal impact
  - *Will link*: See [CH29: Pricing](#) for WTP/elasticity to estimate price lever on payoff.

- **[future CH30: Go-to-Market](#)**: Pricing messaging, competitive positioning, launch cadence
  - *Will link*: See [CH29: Pricing](#) for pricing model design; [CH30](#) implements go-to-market positioning of the model.

- **[future CH31: Customer Feedback](#)**: Pricing feedback loops, customer satisfaction surveys (NPS, pricing perception)
  - *Will link*: See [CH29: Pricing](#) for pricing concepts; [CH31](#) owns gathering feedback on whether pricing feels fair/transparent.

---

## Rationale for Ownership Assignments

1. **Pricing mechanisms are this chapter's core responsibility**: All pricing models (value-based, tiered, freemium, usage-based, subscription, geographic, launch strategies) are taught in depth in CH29, Section 4. No other chapter owns pricing.

2. **Distinction from go-to-market (CH30)**: This chapter owns *how the pricing model works* (mechanism, psychology, implementation). [CH30](#) owns *how the pricing model is positioned and launched to the market* (messaging, competitive framing, launch timing).

3. **Distinction from metrics (CH24)**: This chapter owns *how pricing models generate value* (WTP, elasticity, margin targets). [CH24](#) owns *how to measure the outcome* (LTV, CAC, ARPU, churn tracking).

4. **Freemium is pivotal**: Freemium is both a pricing model (this chapter's ownership) and a customer-acquisition strategy (future CH30's domain). To avoid duplication: this chapter owns the model's mechanics and economics; CH30 owns the go-to-market execution and messaging.

---

## Merge Checklist

When consolidating these proposals into [CORE_CONCEPTS.md](../../CORE_CONCEPTS.md) after batch review:

- [ ] Verify no conflicting ownership claims (is any concept already owned by another chapter?)
- [ ] Update the integration-point links to point to actual chapter files once [CH28, CH30, CH31](#) are drafted
- [ ] Mark this file as merged (update status in CH29_Pricing.md from "Drafted" to "Merged")
