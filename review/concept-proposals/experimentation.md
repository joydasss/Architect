# Concept Proposals — Chapter 26 Experimentation

Proposed new concepts for merger into `CORE_CONCEPTS.md` after batch review.

| Concept | Status | Notes |
|---------|--------|-------|
| Hypothesis formulation (falsifiability, specificity, success thresholds) | New | Proposed by Experimentation; core to all experimentation work |
| Treatment randomization (unit of randomization, deterministic hashing) | New | Proposed by Experimentation; foundational for causal inference |
| Control groups and counterfactual construction (pure control vs. active control) | New | Proposed by Experimentation; distinguishes experiment types |
| Sample-size calculation and statistical power (Type I/II error, power analysis) | New | Proposed by Experimentation; fundamental to powering experiments |
| Confounding variables and internal validity (definition, SUTVA, balance checks) | New | Proposed by Experimentation; critical for experiment validity |
| Sequential testing and adaptive designs (interim analyses, stopping rules, group-sequential) | New | Proposed by Experimentation; architectural pattern for experiment acceleration |
| Experimentation governance and multiple-comparison correction (pre-registration, FDR, experiment registry) | New | Proposed by Experimentation; organizational pattern for scale |

---

## Ownership Arbitration Notes

**None at this stage.** Experimentation introduces new concepts not owned by other chapters in Part 02.

**Forward references:**
- A/B Testing (CH27) will own statistical implementation details (sequential analysis mathematics, stopping rules, effect-size estimation, confidence-interval construction).
- Experimentation owns hypothesis design, experimental methodology, and governance frameworks that feed into A/B Testing's statistical machinery.

---

## Related Concepts in CORE_CONCEPTS.md (Existing)

The following existing concepts are referenced/recapped in Section 4.x but *not* re-taught:

- **Rapid Prototyping Loop (assumption -> artifact -> exposure -> evidence -> decision)** — Owned by [Rapid Prototyping](../02_Design_Thinking_and_Product_Management/CH08_Rapid_Prototyping.md); Section 4.1 recaps only.
- **MVP (Minimum Viable Product)** — Owned by [MVP](../02_Design_Thinking_and_Product_Management/CH23_MVP.md); Section 1 recaps MVP validation loop relationship.
- **Riskiest Assumption Testing (RAT)** — Owned by [MVP](../02_Design_Thinking_and_Product_Management/CH23_MVP.md); mentioned in context of experiment design.
- **Metrics (output vs. outcome, HEART framework, AARRR)** — Owned by [Metrics](../02_Design_Thinking_and_Product_Management/CH24_Metrics.md); Section 4.x defers metric definitions.
- **Telemetry / Event Schema** — Owned by [Metrics](../02_Design_Thinking_and_Product_Management/CH24_Metrics.md); Section 5 builds on telemetry architecture.
