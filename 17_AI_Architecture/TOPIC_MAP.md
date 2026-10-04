# Part 17 — AI Architecture Topic Map

This map defines coverage for Part 17's fifteen system-architecture chapters. Part 17 selects and composes AI capabilities into operable production systems; it does not re-teach model families, algorithms, prompt mechanics, vector indexes, or provider products owned elsewhere.

## Part-wide ownership boundaries

- Part 17 owns workload qualification and end-to-end architecture across data, models, inference, tools, human control, operations, security, and cost.
- Part 16 owns model families, learning algorithms, GenAI techniques, evaluation methods, and AI infrastructure implementations. Part 06 CH21 owns vector-database index mechanics.
- Part 09 owns provider cloud services; Part 12 owns Kubernetes; Part 13 owns deployment pipelines; Part 14 owns observability platforms; Part 15 owns security foundations; Part 07 owns distributed reliability semantics.
- Every architecture should name a deterministic or human fallback, ownership boundary, data/model provenance, and quality evidence. Treat model choice as one component decision inside a larger system.

## Cross-part stakeholders and scenarios

- Product/business owners need evidence that AI improves an outcome versus rules or ordinary software.
- Data, ML, platform, security, legal, and operations teams need explicit ownership for training, retrieval, inference, and response.
- Important scenarios include an unavailable model provider; a stale or unauthorized retrieval source; an unsafe tool action; a model update that degrades a task; and a latency or cost budget exceeded by context growth.

## Chapters

### CH01 AI Workload Qualification and Architecture Foundations

**Reader outcome:** Decide whether a problem warrants AI and define an architecture problem statement with value, risk, data, latency, and control requirements.
**Coverage:** Deterministic software versus predictive ML, GenAI, retrieval, and agents; task decomposition; business outcome; data availability; uncertainty; human control; and baseline alternatives.
**Diagram opportunities:** (1) problem-to-capability selection; (2) decision boundary between deterministic and learned behavior; (3) value/risk/data qualification matrix; (4) human-versus-model authority spectrum; (5) workload objective and evidence chain.

### CH02 AI Capability and Model Selection

**Reader outcome:** Match task and constraints to hosted, self-managed, specialized, or non-AI components without overfitting to a model benchmark.
**Coverage:** Quality, explainability, latency, privacy, cost, deployment, model lifecycle, provider dependence, and Part 16 model-detail recap.
**Diagram opportunities:** (1) task capability decomposition; (2) model-selection decision tree; (3) hosted versus self-managed trust boundary; (4) quality/latency/cost frontier; (5) fallback capability map.

### CH03 Reference Architectures for Predictive, Generative, and Agentic Systems

**Reader outcome:** Compare batch prediction, online inference, retrieval-augmented generation (RAG), and agent workflows by their data, control, and runtime planes.
**Coverage:** Shared platform services, workload-specific paths, feature/retrieval/model components, orchestration, feedback, and failure behavior.
**Diagram opportunities:** (1) batch prediction topology; (2) online inference path; (3) RAG system boundary; (4) bounded agent workflow; (5) shared versus style-specific control/data planes.

### CH04 AI Data Architecture and Preparation Boundaries

**Reader outcome:** Architect data ingestion, quality, lineage, access, transformation, and refresh paths for model and retrieval use.
**Coverage:** Source contracts, quality checks, labeling, feature/embedding creation, lineage, permissions, retention, freshness, and Part 16 data/model recap.
**Diagram opportunities:** (1) source-to-feature/embedding pipeline; (2) data lineage and provenance; (3) quality gate and quarantine; (4) access/consent boundary; (5) refresh and invalidation path.

### CH05 Retrieval-Augmented Generation System Architecture

**Reader outcome:** Compose ingestion, retrieval, reranking, generation, citations, and feedback into an operable, secure RAG system.
**Coverage:** Index lifecycle, query decomposition, retrieval/reranking, context budget, grounding, freshness, authorization, failure fallback, and vector-index owner recap.
**Diagram opportunities:** (1) offline ingestion/index path; (2) online retrieval-to-generation path; (3) identity-aware retrieval filter; (4) citation/grounding trace; (5) stale-index update and rollback.

### CH06 Agentic System Architecture and Tool Boundaries

**Reader outcome:** Design bounded agent loops with explicit tools, permission scopes, memory, checkpoints, and human approval.
**Coverage:** Planner/executor boundary, tool adapters, authentication, action limits, memory scope, retries, state persistence, approval, and Part 16 agent mechanics recap.
**Diagram opportunities:** (1) plan/act/observe loop; (2) tool permission boundary; (3) checkpoint and resume path; (4) human approval for consequential action; (5) loop budget and termination state.

### CH07 Inference Serving and Model Placement

**Reader outcome:** Place inference across synchronous, asynchronous, streaming, batch, edge, and regional targets from latency, locality, throughput, and failure requirements.
**Coverage:** Request path, placement, model loading, network/data gravity, isolation, capacity, streaming, and provider-neutral runtime choices.
**Diagram opportunities:** (1) inference placement topology; (2) sync/async/streaming request paths; (3) regional data-locality flow; (4) model warm/cold start; (5) serving dependency and failure domain.

### CH08 Model Gateway, Routing, and Fallback Architecture

**Reader outcome:** Route requests across models/providers by task, quality, privacy, availability, and cost while preserving a stable application contract.
**Coverage:** Gateway responsibilities, routing policy, model adapters, fallback, retries, circuit breaking, versioning, credentials, and API Gateway boundary.
**Diagram opportunities:** (1) client-to-model gateway topology; (2) policy-based model routing; (3) fallback and circuit-breaker state; (4) provider credential boundary; (5) stable API versus provider-specific adapter.

### CH09 Human Oversight and AI-Assisted Workflow Integration

**Reader outcome:** Place review, confirmation, escalation, rollback, and audit around consequential AI recommendations and actions.
**Coverage:** Human-in-the-loop/out-of-loop distinctions, confidence and escalation, review queues, authority limits, UX, accountability, and override.
**Diagram opportunities:** (1) confidence-to-human-review routing; (2) assisted decision and approval workflow; (3) override and rollback path; (4) audit trail and accountable owner; (5) automation level versus impact matrix.

### CH10 AI Platform and Model Lifecycle Architecture

**Reader outcome:** Compose training, model registry, evaluation, deployment, monitoring, rollback, and retirement into a governed lifecycle.
**Coverage:** Model/data lineage, artifact promotion, environment separation, evaluation gates, serving, drift/quality feedback, rollback, and Part 16 MLOps/LLMOps recap.
**Diagram opportunities:** (1) training-to-registry-to-serving lifecycle; (2) artifact lineage; (3) evaluation gate before promotion; (4) canary model release and rollback; (5) retirement and consumer migration.

### CH11 Evaluation and Observability Architecture for AI Systems

**Reader outcome:** Correlate offline evaluations, online quality, request traces, feedback, model versions, and incidents.
**Coverage:** Quality metrics, trace/metadata design, model and prompt version attribution, feedback capture, drift signals, sampling, redaction, and Part 14 telemetry recap.
**Diagram opportunities:** (1) offline/online evaluation loop; (2) request trace across retrieval and inference; (3) model/prompt/version metadata path; (4) feedback-to-test-set cycle; (5) quality regression alert and investigation.

### CH12 AI Safety, Security, Privacy, and Governance Architecture

**Reader outcome:** Place controls for sensitive data, model/tool isolation, provenance, human accountability, and audit across the AI system.
**Coverage:** Threat boundaries, prompt injection, tool authorization, data handling, content safeguards, provenance, policy enforcement, human oversight, and Part 15 recap.
**Diagram opportunities:** (1) AI system threat boundary; (2) untrusted input to tool-call defense; (3) sensitive data flow and redaction; (4) model/artifact provenance path; (5) governance decision and exception lifecycle.

### CH13 Reliability and Resilience Patterns for AI Workloads

**Reader outcome:** Design timeouts, bulkheads, degraded modes, queues, deterministic fallbacks, and recovery for variable or unavailable inference.
**Coverage:** Dependency failures, rate limits, retries, circuit breakers, graceful degradation, response deadlines, idempotency, and service-level objectives.
**Diagram opportunities:** (1) inference dependency failure modes; (2) timeout budget across request path; (3) circuit-breaker state; (4) degraded deterministic fallback; (5) queued workload recovery.

### CH14 AI Cost, Performance, and Sustainability Decisions

**Reader outcome:** Connect model, token, compute, storage, network, and quality choices to system-level unit economics and environmental impact.
**Coverage:** Token/compute costs, batching, caching, quantization, placement, model tiers, quality budgets, utilization, and lifecycle sustainability.
**Diagram opportunities:** (1) request cost breakdown; (2) batching/latency/cost trade-off; (3) model-tier routing by quality budget; (4) data movement and energy boundary; (5) cost/quality frontier.

### CH15 End-to-End AI Architecture Reviews and Case Studies

**Reader outcome:** Review a complete AI-enabled solution across business value, data, model, inference, control, operations, security, and cost.
**Coverage:** Architecture review method, evidence, assumptions, options, risks, decisions, validation plan, and end-to-end cases.
**Diagram opportunities:** (1) end-to-end AI system context; (2) evidence-to-architecture review map; (3) risk and ownership matrix; (4) decision alternatives and trade-offs; (5) production incident feedback into redesign.
