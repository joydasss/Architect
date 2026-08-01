# A/B Testing Concepts Staging File (CH27)

Proposed new concepts introduced in CH27 "A/B Testing". Per STYLE_GUIDE.md Concept Ownership Rule, these are staged here before merging into CORE_CONCEPTS.md. Concept ownership arbitration will occur in a separate merge step after parallel chapter authoring completes.

## New Concepts Introduced

### Concept: Randomization and Hash-Based Assignment
- **Definition:** Deterministic, reproducible assignment of observations (users) to experimental variants using cryptographic hash functions, ensuring uniformity and independence.
- **Owning Chapter:** CH27_A_B_Testing
- **Rationale:** A/B Testing chapter owns the technical machinery of randomization protocols (simple randomization, stratified randomization, Latin Square designs). Related chapters (Experimentation) recap this mechanically but focus on hypothesis design.
- **Reference Location:** Section 4.1 (Core Concepts: Randomization and Stratification)

### Concept: Power Analysis and Sample Size Calculation
- **Definition:** Pre-experimental statistical calculation determining required observation count per variant to achieve target power (true-positive rate) and significance level (false-positive rate) for a specified effect size.
- **Owning Chapter:** CH27_A_B_Testing
- **Rationale:** A/B Testing owns the complete statistical machinery of power calculations, MDE (Minimum Detectable Effect), and sample-size formulas. Experimentation (CH26) recaps the concept when used for experiment design.
- **Reference Location:** Section 4.2

### Concept: Frequentist Hypothesis Testing and *p*-Values
- **Definition:** Statistical inference framework based on null hypothesis significance testing (NHST), computing *p*-values as the probability of observing data as extreme or more extreme than observed, assuming the null hypothesis is true.
- **Owning Chapter:** CH27_A_B_Testing
- **Rationale:** A/B Testing owns the full technical explanation of *p*-values, their misinterpretations, and correct interpretation (false-positive rate over repeated experiments, not probability the null is true).
- **Reference Location:** Section 4.3.1

### Concept: Bayesian Posterior Inference
- **Definition:** Statistical inference framework treating model parameters as random variables with probability distributions, updating from prior beliefs to posterior beliefs using Bayes' theorem after observing data.
- **Owning Chapter:** CH27_A_B_Testing
- **Rationale:** A/B Testing chapter owns the technical explanation of Bayesian posterior computation, credible intervals, and posterior probability statements as alternatives to frequentist *p*-values.
- **Reference Location:** Section 4.3.2

### Concept: Multiple Comparison Problem (MCP) and False Discovery Rate (FDR)
- **Definition:** Statistical phenomenon where false-positive rate inflates as the number of statistical tests increases. Family-Wise Error Rate (FWER) controls probability of any false positive; False Discovery Rate (FDR) controls expected proportion of false positives among all rejections.
- **Owning Chapter:** CH27_A_B_Testing
- **Rationale:** A/B Testing owns the complete technical machinery of multiple-comparison corrections (Bonferroni, Benjamini-Hochberg, etc.) and when to apply FWER vs. FDR control.
- **Reference Location:** Section 4.4

### Concept: Sequential Probability Ratio Test (SPRT)
- **Definition:** Sequential statistical procedure that permits continuous monitoring of accumulated data, with formal decision boundaries (likelihood ratio thresholds) for early stopping while maintaining error control.
- **Owning Chapter:** CH27_A_B_Testing
- **Rationale:** A/B Testing owns the technical implementation and statistical theory of SPRT, group sequential tests, and peeking-penalty mathematics. Experimentation (CH26) recaps SPRT as an experimental design choice.
- **Reference Location:** Section 4.5

### Concept: Factorial and Multivariate Experimental Design
- **Definition:** Experimental design testing multiple factors (independent variables) simultaneously using 2^k or higher-order designs, enabling estimation of main effects and interaction effects efficiently.
- **Owning Chapter:** CH27_A_B_Testing
- **Rationale:** A/B Testing owns the complete technical machinery of factorial designs, orthogonal designs, and interaction estimation. Experimentation (CH26) recaps factorial design as an experimental structure choice.
- **Reference Location:** Section 4.6

### Concept: Contextual Bandits and Thompson Sampling
- **Definition:** Online learning algorithms that adaptively allocate traffic or actions based on observed context and rewards, balancing exploitation (pulling high-reward actions) and exploration (occasionally sampling low-reward actions).
- **Owning Chapter:** CH27_A_B_Testing
- **Rationale:** A/B Testing owns the technical implementation of Thompson Sampling, Upper Confidence Bound (UCB), and other bandit algorithms. Differentiates bandits from fixed-allocation A/B tests (which are not valid for power analysis).
- **Reference Location:** Section 4.7

### Concept: Minimum Detectable Effect (MDE) and Practically Significant Effect (PSE)
- **Definition:** MDE is the smallest true effect size detectable by a designed experiment with specified power and significance level. PSE is the smallest effect size a decision-maker cares about. Comparing MDE vs. PSE determines experiment feasibility.
- **Owning Chapter:** CH27_A_B_Testing
- **Rationale:** A/B Testing chapter owns the statistical machinery and trade-offs between MDE and PSE. Experimentation (CH26) uses MDE as an input to experiment design decisions.
- **Reference Location:** Section 4.2.2

### Concept: Experiment Collision and Interference
- **Definition:** Statistical or causal interference between concurrent experiments when the same user or observation unit is assigned to variants of multiple experiments, causing results of Experiment A to bias outcomes of Experiment B.
- **Owning Chapter:** CH27_A_B_Testing
- **Rationale:** A/B Testing owns the technical architecture and detection mechanisms for experiment collisions, isolation layers, and orthogonal designs.
- **Reference Location:** Section 4.4.2

### Concept: Stratification and Latin Square Designs
- **Definition:** Experimental technique partitioning observations into homogeneous subgroups (strata) based on known confounding variables, then applying randomization independently within each stratum to reduce variance and ensure balanced representation.
- **Owning Chapter:** CH27_A_B_Testing
- **Rationale:** A/B Testing owns the complete technical machinery of stratification, variance reduction via stratification, Latin Square balanced designs, and their interaction with sample-size calculations.
- **Reference Location:** Section 4.1.2

### Concept: Type I Error (False Positive) and Type II Error (False Negative)
- **Definition:** Type I Error: rejecting a true null hypothesis (declaring an effect exists when it doesn't). Type II Error: failing to reject a false null hypothesis (missing a real effect). α and β are error rates; power = 1 - β.
- **Owning Chapter:** CH27_A_B_Testing
- **Rationale:** A/B Testing owns the technical definition, interpretation, and control of Type I and Type II errors in the context of A/B testing infrastructure. Experimentation (CH26) references these conceptually when designing experiments.
- **Reference Location:** Implicit throughout Section 4 (especially Section 4.2)

---

## Related Concepts Owned by Other Chapters (Recap + Link Only in CH27)

When CH27 references these concepts, it will recap in 2-3 sentences and link to the owning chapter, not re-teach:

- **Hypothesis Formulation and Experimental Design:** Owned by [Experimentation](CH26_Experimentation.md). A/B Testing recaps: "Experimentation chapter covers hypothesis specification, outcome selection, and experimental structure choices. A/B Testing focuses on the statistical machinery of executing that design."
- **Post-Experiment Inference and Decision Logic:** Owned by [Experimentation](CH26_Experimentation.md). A/B Testing recaps: "After statistical analysis completes, Experimentation chapter covers interpreting results and executing business decisions (pivot vs. persevere). A/B Testing hands off at the decision boundary."
- **Riskiest Assumption Testing (RAT):** Owned by [Product Discovery](CH14_Product_Discovery.md). Recap when referenced in context of MVP prioritization of experiments.

---

## Ownership Arbitration Notes

None required at this time. No overlaps with existing CORE_CONCEPTS.md entries or other staged chapters detected (CH26 Experimentation will be authored separately and collision risk is expected — collision resolution deferred to merge step).
