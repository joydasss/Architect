# Part 17 — AI Architecture

Supplemental system-architecture module for designing production solutions that use Artificial Intelligence (AI), Machine Learning (ML), and Generative AI (GenAI). Part 16 — AI and GenAI owns model families, algorithms, prompts, retrieval, fine-tuning, agents, evaluation techniques, and infrastructure implementations. Part 17 owns how those capabilities fit together as a solution: workload qualification, data/model/inference boundaries, human oversight, platform integration, reliability, cost, and governance.

## Scope boundary

These chapters select and compose AI capabilities; they do not re-teach the model or algorithm internals owned by [Part 16](../16_AI_and_GenAI/PART_OVERVIEW.md). Cloud provider architecture remains with Part 09 and the supplemental [Cloud Architecture](../10_Cloud_Architecture/PART_OVERVIEW.md) module. Kubernetes, Security, and Observability remain with Parts 12, 15, and 14, respectively, and are recapped where needed.

Topic map: [TOPIC_MAP.md](TOPIC_MAP.md)

## Chapters

Each revised chapter is at least 23,000 words (excluding diagrams), has at least nine diagrams, and links runnable examples under `code/python/`.

| Chapter | Focus | Status |
|---|---|---|
| [AI Workload Qualification and Architecture Foundations](CH01_AI_Workload_Qualification_and_Architecture_Foundations.md) | Decide whether a problem warrants AI; compare deterministic software, predictive ML, GenAI, retrieval, and agentic solutions using value, risk, data, latency, and control requirements. | Revised (in-depth rewrite) |
| [AI Capability and Model Selection](CH02_AI_Capability_and_Model_Selection.md) | Map task, quality, explainability, latency, privacy, cost, and deployment constraints to hosted, self-managed, specialized, or non-AI components; recap Part 16 model details. | Revised (in-depth rewrite) |
| [Reference Architectures for Predictive, Generative, and Agentic Systems](CH03_Reference_Architectures_for_Predictive_Generative_and_Agentic_Systems.md) | Compare batch prediction, online inference, retrieval-augmented generation (RAG), and agent workflows; identify shared and style-specific control/data planes. | Revised (in-depth rewrite) |
| [AI Data Architecture and Preparation Boundaries](CH04_AI_Data_Architecture_and_Preparation_Boundaries.md) | Architect ingestion, quality, lineage, feature/embedding creation, access control, and refresh paths; recap Part 16 data/modeling mechanics and database owners. | Revised (in-depth rewrite) |
| [Retrieval-Augmented Generation System Architecture](CH05_Retrieval_Augmented_Generation_System_Architecture.md) | Compose source ingestion, chunking/embedding, retrieval, reranking, generation, citations, and feedback into an operable system; vector-index mechanics remain with Part 16/Part 06. | Revised (in-depth rewrite) |
| [Agentic System Architecture and Tool Boundaries](CH06_Agentic_System_Architecture_and_Tool_Boundaries.md) | Design planning/execution loops, tool adapters, permissions, memory scope, checkpoints, human approval, and bounded autonomy; recap Part 16 agent mechanics. | Revised (in-depth rewrite) |
| [Inference Serving and Model Placement](CH07_Inference_Serving_and_Model_Placement.md) | Choose synchronous, asynchronous, streaming, batch, edge, or regional inference based on latency, data locality, throughput, and failure requirements. | Revised (in-depth rewrite) |
| [Model Gateway, Routing, and Fallback Architecture](CH08_Model_Gateway_Routing_and_Fallback_Architecture.md) | Route by task, quality tier, availability, privacy, or cost; define fallback and provider abstraction without duplicating API Gateway's general architecture. | Revised (in-depth rewrite) |
| [Human Oversight and AI-Assisted Workflow Integration](CH09_Human_Oversight_and_AI_Assisted_Workflow_Integration.md) | Place review, escalation, confirmation, rollback, and audit steps around consequential AI decisions and generated actions. | Revised (in-depth rewrite) |
| [AI Platform and Model Lifecycle Architecture](CH10_AI_Platform_and_Model_Lifecycle_Architecture.md) | Compose training, registry, deployment, evaluation, monitoring, rollback, and retirement into an MLOps/LLMOps lifecycle; recap Part 16 infrastructure tools. | Revised (in-depth rewrite) |
| [Evaluation and Observability Architecture for AI Systems](CH11_Evaluation_and_Observability_Architecture_for_AI_Systems.md) | Connect offline evaluation, online quality signals, traces, feedback, model/version attribution, and incident diagnosis; recap Part 16 evaluation and Part 14 telemetry. | Revised (in-depth rewrite) |
| [AI Safety, Security, Privacy, and Governance Architecture](CH12_AI_Safety_Security_Privacy_and_Governance_Architecture.md) | Place policy enforcement, sensitive-data controls, model/tool isolation, provenance, human accountability, and audit evidence across the system; recap Part 15 Security. | Revised (in-depth rewrite) |
| [Reliability and Resilience Patterns for AI Workloads](CH13_Reliability_and_Resilience_Patterns_for_AI_Workloads.md) | Architect timeouts, bulkheads, degraded modes, deterministic fallbacks, queueing, recovery, and service-level objectives for variable or unavailable inference. | Revised (in-depth rewrite) |
| [AI Cost, Performance, and Sustainability Decisions](CH14_AI_Cost_Performance_and_Sustainability_Decisions.md) | Compare token/compute/storage/network costs, batching, caching, quantization, placement, model tiers, and quality budgets at the system level. | Revised (in-depth rewrite) |
| [End-to-End AI Architecture Reviews and Case Studies](CH15_End_to_End_AI_Architecture_Reviews_and_Case_Studies.md) | Review complete AI-enabled solutions against workload, data, model, inference, control, operations, security, and cost concerns. | Revised (in-depth rewrite) |

## Planned additional chapters

These chapters fill gaps found during the in-depth rewrite. No chapter files, topic-map entries, or concept-registry entries exist yet; each will be added when the chapter is drafted.

| Chapter | Planned focus | Status |
|---|---|---|
| Multi-Tenant AI Architecture and Data Isolation | Tenant isolation across prompts, caches, retrieval indexes, memory, fine-tuned adapters, and traces; noisy-neighbor control, per-tenant quotas and keys, bring-your-own-key, residency per tenant, and cross-tenant leak testing. | Planned (not yet drafted) |
| Conversational and Real-Time Voice AI Architecture | Session and dialogue state, turn-taking and barge-in, streaming speech pipelines versus speech-to-speech models, latency budgets, telephony and WebRTC integration, handoff to humans, and consent and recording rules. | Planned (not yet drafted) |
| AI Regulatory Compliance Mapping Architecture | Mapping obligations from the EU AI Act, NIST AI RMF, ISO/IEC 42001, sector rules, and privacy law to engineering controls; evidence automation, technical documentation, record-keeping, and change-triggered re-assessment. | Planned (not yet drafted) |
