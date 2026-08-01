# Concept Proposals: Chapter 31 — Customer Feedback

This document stages core concepts owned by CH31_Customer_Feedback.md for integration into CORE_CONCEPTS.md.

## Owned Concepts (Full Teaching in CH31)

- **Net Promoter Score (NPS):** Quantitative customer loyalty metric (0-10 question, segmented into Promoters/Passives/Detractors, -100 to +100 score); measures likelihood to recommend; leading indicator of churn and expansion. (§4.1)

- **Customer Satisfaction Score (CSAT):** Quantitative satisfaction metric for specific experiences (1-5 or 1-10 Likert scale); deployed post-interaction; context-rich but narrower than NPS. (§4.2)

- **Voice of Customer (VoC) Program:** Systematic ongoing process for collecting, analyzing, and acting on customer feedback across multiple channels (surveys, support, interviews, social); unified repository and synthesis pipeline. (§4.3)

- **Feedback-to-Action Loop:** Operational process that routes customer feedback to product/engineering/support, prioritizes for roadmap inclusion, and communicates status back to customers; close-loop systems build trust and advocacy. (§4.4)

- **Sentiment Analysis (Automated):** Computational classification of customer feedback as positive/negative/neutral using rule-based (lexicon) or transformer-based (BERT, GPT) approaches; enables scaling feedback synthesis to thousands of pieces. (§4.5)

- **Theme Extraction / Topic Modeling:** Automated or semi-automated clustering of feedback into recurring topics (Performance, Onboarding, Pricing, etc.); enables identification of high-impact themes across customer base. (§4.5)

- **Behavioral Feedback Signals:** Quantitative or qualitative data derived from product usage (feature adoption, session recordings, error logs, funnel drop-offs) distinct from explicit surveys; reveals unmet needs and UX friction invisible to support tickets. (§4.6)

- **Customer Effort Score (CES):** Quantitative metric measuring ease of completing a task or resolving an issue (1-5 scale); predictor of customer satisfaction and loyalty; deployed post-support or post-task. (§4.2, §5.0)

- **Win/Loss Analysis:** Qualitative feedback method that interviews customers who chose your product (wins) and competitors (losses); reveals feature gaps, pricing positioning, and competitive threats. (§9)

- **Close-Loop Feedback System:** Infrastructure where customers receive visibility into actions taken (or not taken) in response to their feedback; increases retention, advocacy, and NPS among requesting customers. (§4.4)

- **NPS Cohort Analysis:** Segmentation of NPS by customer segment (enterprise vs. SMB), geography, tenure, or feature-adoption level; reveals cohort-specific satisfaction issues and churn risks. (§7)

- **Feedback Routing / Triage Engine:** Automated or rule-based system that routes feedback to appropriate teams (Engineering for bugs, Product for features, Sales for competitive intelligence) based on content, priority, and customer value. (§8)

- **Churn Risk Scoring:** Behavioral model that estimates customer churn probability based on NPS trend, feature usage depth, session frequency, and support tickets; enables proactive retention outreach. (§4.6, §7)

- **Feedback Bias and Representativeness:** Selection bias (self-selected survey respondents), response bias (power users over-represented), confirmation bias (teams interpreting feedback through existing worldview); mitigated through triangulation with behavioral data and diverse recruitment. (§14)

- **Feedback Quality Validation:** Framework for assessing whether feedback corpus is actionable (representative, sufficient sample size, recent enough, high confidence); marks provisional conclusions for low-quality feedback. (§13.12)

- **Privacy-by-Design in Feedback Infrastructure:** Architectural principle that feedback collection, storage, and analysis include consent management, PII masking, access controls, and retention policies from the start, not retrofitted. (§11.3, §13.11)

## Concepts Owned by Other Chapters (Recap + Link)

- **Metrics and Instrumentation** (CH24): Feedback synthesis supports metric validation; behavioral signals feed telemetry. Link for context.

- **North Star Metrics Alignment** (CH25): Feedback validates whether North Star Metric reflects customer value. Link for context.

- **Experimentation Hypothesis Formulation** (CH26): Customer feedback informs experiment hypotheses. Link for context.

- **A/B Testing Statistical Rigor** (CH27): Feedback provides qualitative context for quantitative test results. Link for context.

- **Roadmap Prioritization Frameworks** (CH28): Feedback is a key input signal (frequency, customer value, strategic fit) to prioritization decision trees. Link for context.

## Boundary Clarifications

- **Product Discovery (CH14) vs. Customer Feedback (CH31):** CH14 owns early-stage user research (discovery interviews, problem validation, concept testing during product discovery phase). CH31 owns ongoing, systematic feedback collection post-launch as a continuous loop. Overlap minimal; both can coexist. CH31 may reference CH14 for interview methodology, but CH31 focuses on scale and synthesis.

- **Journey Mapping (CH19) vs. Voice of Customer (CH31):** CH19 owns journey mapping as a design artifact (understanding customer workflow and touchpoints across experience). CH31 owns VoC as a systematic feedback program (collecting voice across those touchpoints). Complementary, not duplicate.

- **User Research and Testing (CH10, CH11) vs. Behavioral Feedback (CH31):** CH10/CH11 own formal research methodology (study design, usability testing protocols). CH31 owns continuous behavioral telemetry (session recording, usage analytics, error tracking) as implicit feedback signals. Different timescales and methodologies; both valuable.
