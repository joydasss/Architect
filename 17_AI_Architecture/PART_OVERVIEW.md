# Part 17 — AI Architecture

Supplemental system-architecture module for designing production solutions that use Artificial Intelligence (AI), Machine Learning (ML), and Generative AI (GenAI). Part 16 — AI and GenAI owns model families, algorithms, prompts, retrieval, fine-tuning, agents, evaluation techniques, and infrastructure implementations. Part 17 owns how those capabilities fit together as a solution: workload qualification, data/model/inference boundaries, human oversight, platform integration, reliability, cost, and governance.

## Scope boundary

These chapters select and compose AI capabilities; they do not re-teach the model or algorithm internals owned by [Part 16](../16_AI_and_GenAI/PART_OVERVIEW.md). Cloud provider architecture remains with Part 09 and the supplemental [Cloud Architecture](../10_Cloud_Architecture/PART_OVERVIEW.md) module. Kubernetes, Security, and Observability remain with Parts 12, 13, and 12, respectively, and are recapped where needed.

## Chapters

| Chapter | Focus | Status |
|---|---|---|
| AI Workload Qualification and Architecture Foundations | Decide whether a problem warrants AI; compare deterministic software, predictive ML, GenAI, retrieval, and agentic solutions using value, risk, data, latency, and control requirements. | Not Started |
| AI Capability and Model Selection | Map task, quality, explainability, latency, privacy, cost, and deployment constraints to hosted, self-managed, specialized, or non-AI components; recap Part 16 model details. | Not Started |
| Reference Architectures for Predictive, Generative, and Agentic Systems | Compare batch prediction, online inference, retrieval-augmented generation (RAG), and agent workflows; identify shared and style-specific control/data planes. | Not Started |
| AI Data Architecture and Preparation Boundaries | Architect ingestion, quality, lineage, feature/embedding creation, access control, and refresh paths; recap Part 16 data/modeling mechanics and database owners. | Not Started |
| Retrieval-Augmented Generation System Architecture | Compose source ingestion, chunking/embedding, retrieval, reranking, generation, citations, and feedback into an operable system; vector-index mechanics remain with Part 16/Part 06. | Not Started |
| Agentic System Architecture and Tool Boundaries | Design planning/execution loops, tool adapters, permissions, memory scope, checkpoints, human approval, and bounded autonomy; recap Part 16 agent mechanics. | Not Started |
| Inference Serving and Model Placement | Choose synchronous, asynchronous, streaming, batch, edge, or regional inference based on latency, data locality, throughput, and failure requirements. | Not Started |
| Model Gateway, Routing, and Fallback Architecture | Route by task, quality tier, availability, privacy, or cost; define fallback and provider abstraction without duplicating API Gateway's general architecture. | Not Started |
| Human Oversight and AI-Assisted Workflow Integration | Place review, escalation, confirmation, rollback, and audit steps around consequential AI decisions and generated actions. | Not Started |
| AI Platform and Model Lifecycle Architecture | Compose training, registry, deployment, evaluation, monitoring, rollback, and retirement into an MLOps/LLMOps lifecycle; recap Part 16 infrastructure tools. | Not Started |
| Evaluation and Observability Architecture for AI Systems | Connect offline evaluation, online quality signals, traces, feedback, model/version attribution, and incident diagnosis; recap Part 16 evaluation and Part 14 telemetry. | Not Started |
| AI Safety, Security, Privacy, and Governance Architecture | Place policy enforcement, sensitive-data controls, model/tool isolation, provenance, human accountability, and audit evidence across the system; recap Part 15 Security. | Not Started |
| Reliability and Resilience Patterns for AI Workloads | Architect timeouts, bulkheads, degraded modes, deterministic fallbacks, queueing, recovery, and service-level objectives for variable or unavailable inference. | Not Started |
| AI Cost, Performance, and Sustainability Decisions | Compare token/compute/storage/network costs, batching, caching, quantization, placement, model tiers, and quality budgets at the system level. | Not Started |
| End-to-End AI Architecture Reviews and Case Studies | Review complete AI-enabled solutions against workload, data, model, inference, control, operations, security, and cost concerns. | Not Started |
