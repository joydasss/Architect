# Batch Review — Part 02 Batch 11 (North Star Metrics, Experimentation, A/B Testing)

Covers:
- `02_Design_Thinking_and_Product_Management/CH25_North_Star_Metrics.md`
- `02_Design_Thinking_and_Product_Management/CH26_Experimentation.md`
- `02_Design_Thinking_and_Product_Management/CH27_A_B_Testing.md`

## 1. Overlap / Duplicate Ownership Checks

### A. North Star Metrics (CH25)
- **Product Strategy (CH15) boundary**: CH15 owns Strategy Stack, OKRs, and strategic-fit sequencing test. CH25 explicitly defers to CH15 for OKRs definition and adds a new concept: OKRs vs. North Star Metrics Arbitration and Synchronized Governance (the operational discipline for reconciling the two).
- **Metrics (CH24) boundary**: CH24 owns Input/Output Metric Trees, HEART, AARRR, Counter-Metrics, Telemetry Architecture. CH25 recaps these and owns North Star-specific telemetry foundation requirements (metric definition versioning, aggregation consistency, data quality assertions).
- **Roadmaps (CH21) boundary**: CH21 owns outcome-based roadmapping. CH25 teaches how North Star Metrics inform roadmap prioritization without re-teaching roadmap construction.

### B. Experimentation (CH26)
- **MVP (CH23) boundary**: CH23 owns Riskiest Assumption Testing (RAT) and MVP validation loops. CH26 recaps MVP context and owns broader hypothesis formulation, experimental design, randomization, control groups, sample-size calculation, confounding variables, sequential testing, and governance.
- **Metrics (CH24) boundary**: CH24 owns telemetry architecture and metric calculation. CH26 builds on telemetry but focuses on experimental design methodology.
- **A/B Testing (CH27) boundary**: CH26 owns hypothesis formulation, experimental design decisions, and governance frameworks. CH27 owns the statistical machinery (power analysis formulas, frequentist/Bayesian testing, MCP correction, SPRT mathematics, factorial designs, bandits). Clean separation: CH26 is "what experiments to run and how to run them"; CH27 is "how to compute statistical results."

### C. A/B Testing (CH27)
- **Experimentation (CH26) boundary**: CH27 owns statistical implementation details (randomization algorithms, power analysis, hypothesis testing frameworks, MCP correction, SPRT, factorial design mathematics, Thompson Sampling). CH26 recaps hypothesis formulation and experimental design concepts when using them to set A/B test parameters.
- **Metrics (CH24) boundary**: CH24 owns metric definition and telemetry pipelines. CH27 assumes those exist and focuses on assignment logic, analysis engines, and statistical decision boundaries.
- **North Star Metrics (CH25) boundary**: CH25 owns North Star selection and governance. CH27 recaps North Star concepts when setting success thresholds for A/B tests but does not re-teach North Star mechanics.

## 2. Completeness & Structural Quality

All three chapters verified via `grep_search`:
- `CH25_North_Star_Metrics.md`: Exactly 27 sections, 12 inline Mermaid diagrams ✓
- `CH26_Experimentation.md`: Exactly 27 sections (Section 6 heading fixed from h3 to h2), 14 inline Mermaid diagrams ✓
- `CH27_A_B_Testing.md`: Exactly 27 sections, 11 inline Mermaid diagrams ✓

All three chapters include `\begin{landscape}` wrappers around wide architecture/decision diagrams for PDF generation.
All three expand acronyms on first use (e.g., SUTVA, SPRT, FWER, FDR, MDE, UCB, ANOVA, HARKing, MCP).

## 3. Accuracy & Cross-Reference Fixes

- Resolved pending forward references from Product Strategy (CH15) regarding North Star Metrics alignment with strategy and OKRs.
- Resolved pending forward references from Metrics (CH24) regarding telemetry requirements for experimentation and A/B testing.
- No stale "not yet drafted" references found in previously drafted chapters that should now resolve to CH25, CH26, or CH27.

## 4. Concept Ownership Log

Proposed additions merged into `CORE_CONCEPTS.md`:
- **CH25 (North Star Metrics)**: 8 new concepts (North Star Metric, North Star Selection Frameworks, North Star vs. OKRs Arbitration, North Star Cascade, North Star Lifecycle, Multi-Product North Star Structures, North Star Telemetry Foundation).
- **CH26 (Experimentation)**: 7 new concepts (Hypothesis Formulation, Treatment Randomization, Control Groups & Counterfactual Construction, Sample-Size Calculation & Statistical Power, Confounding Variables & Internal Validity, Sequential Testing & Adaptive Designs, Experimentation Governance & MCP Correction).
- **CH27 (A/B Testing)**: 10 new concepts (Randomization & Hash-Based Assignment, Power Analysis & Sample Size Calculation, Frequentist Hypothesis Testing & p-Values, Bayesian Posterior Inference, MCP & FDR, SPRT, Factorial & Multivariate Design, Contextual Bandits & Thompson Sampling, Stratification & Latin Square Designs, Experiment Collision & Interference).

**Note**: Some concepts appear in both CH26 and CH27 with precise scoping:
- "Sample-Size Calculation and Statistical Power" is owned by CH26 (methodology), while "Power Analysis and Sample Size Calculation" is owned by CH27 (statistical formulas and calculations). The two are complementary, not duplicative.
- "Treatment Randomization" (CH26) vs. "Randomization and Hash-Based Assignment" (CH27): CH26 owns the conceptual requirement for randomization, while CH27 owns the technical implementation of deterministic hashing and stratified randomization protocols.

## 5. Key Architectural Insights

- **Hypothesis-Driven Culture**: Experimentation (CH26) establishes that every feature change should be preceded by an explicit, falsifiable hypothesis—not intuition-driven development.
- **Randomization as Critical Infrastructure**: A/B Testing (CH27) emphasizes that deterministic hashing for treatment assignment is not a "nice to have" but architectural-level infrastructure required for causal inference.
- **North Star as Organizational Alignment**: North Star Metrics (CH25) frames single-metric alignment as a foundational problem in multi-product organizations, preventing one product from cannibalizing another's roadmap.
- **Sequential Testing for Velocity**: Sequential testing and adaptive designs (CH26, CH27) enable faster decision-making while maintaining statistical rigor—addressing the traditional trade-off between speed and accuracy.
