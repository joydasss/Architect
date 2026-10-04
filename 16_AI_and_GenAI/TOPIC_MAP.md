# Part 16 — Artificial Intelligence, Machine Learning, and Generative AI Topic Map

This map defines coverage for Part 16's 31 chapters across machine learning/deep learning and large language models/generative AI. The part owns model families, learning algorithms, inference behavior, embeddings, retrieval techniques, fine-tuning, agents, evaluations, and implementation tools. The supplemental Part 17 AI Architecture owns how those capabilities are composed into production systems.

## Part-wide ownership boundaries

- Part 16 owns artificial intelligence (AI), machine learning (ML), and generative AI (GenAI) technical foundations: models, training, inference, retrieval, agents, evaluation, and infrastructure implementations.
- Part 17 owns system architecture that composes AI capabilities: workload qualification, data/model/inference boundaries, human oversight, service integration, reliability, cost, and governance.
- Part 06 CH21 owns vector database and approximate-nearest-neighbor index mechanics; Part 16 covers their role in AI retrieval and links to the storage owner.
- Part 07 owns distributed systems, consistency, and event-processing semantics; Part 08 owns API design; Part 13 owns general DevOps; Part 14 owns observability; Part 15 owns security foundations.
- Treat model capabilities, evaluation claims, and vendor/platform behavior as versioned evidence. Distinguish research benchmark results from production outcomes and model behavior from system behavior.

## Cross-part stakeholders and quality scenarios

- ML practitioners need correct data splits, reproducible training, model selection, and evaluation under distribution shift.
- Application architects need to understand latency, token/context cost, retrieval quality, tool permissions, safety, and fallbacks.
- Data owners need lineage, consent, privacy, retention, licensing, and provenance for training and retrieval sources.
- Important scenarios include data leakage inflating offline results; a model update reducing task quality; retrieval returning stale or unauthorized content; an agent invoking an unsafe tool; and inference capacity failing under burst load.

## Machine Learning and Deep Learning

### CH01 Machine Learning Foundations

**Reader outcome:** Frame an ML problem, choose a learning setup, and connect data, objective, model, and evaluation.
**Coverage:** Supervised/unsupervised/reinforcement learning, dataset/labels, probability/statistics/linear algebra, loss/optimization, generalization, bias/variance, and a first model.
**Diagram opportunities:** (1) problem/data/model/evaluation loop; (2) train/validation/test split; (3) loss surface and optimization; (4) bias/variance trade-off; (5) feature-to-prediction pipeline.

### CH02 Data Preparation, Feature Engineering, and Leakage

**Reader outcome:** Build reproducible features and partitions without allowing future or target information to leak into training.
**Coverage:** Missing values, normalization, categorical encoding, labels, imbalance, temporal/group splits, leakage, transforms, lineage, and data quality.
**Diagram opportunities:** (1) raw-to-feature pipeline; (2) leakage across split boundary; (3) temporal split for prediction; (4) fit-transform state reused at inference; (5) feature lineage and quality gates.

### CH03 Regression and Classification

**Reader outcome:** Choose and calibrate predictive models according to target type, error costs, and decision threshold.
**Coverage:** Linear/logistic models, regularization, decision boundaries, multiclass classification, calibration, threshold selection, and business-cost metrics.
**Diagram opportunities:** (1) regression prediction and residuals; (2) classification boundary; (3) regularization effect; (4) threshold versus precision/recall; (5) calibrated probability to business action.

### CH04 Decision Trees and Ensemble Learning

**Reader outcome:** Explain tree splits, ensemble methods, performance, and interpretation limits for structured prediction.
**Coverage:** Split criteria, depth/pruning, bagging, Random Forests, gradient boosting, feature importance, leakage, and tabular-model selection.
**Diagram opportunities:** (1) recursive tree split; (2) bagging across bootstrap samples; (3) boosting residual correction; (4) bias/variance across ensemble sizes; (5) feature-importance caveat.

### CH05 Unsupervised Learning and Representation Reduction

**Reader outcome:** Apply clustering, anomaly detection, and dimensionality reduction when labels are absent or insufficient.
**Coverage:** Distance metrics, clustering, density/anomaly methods, dimensionality reduction, evaluation without labels, and distribution shift.
**Diagram opportunities:** (1) distance metric changes neighborhood; (2) cluster separation and overlap; (3) density-based anomaly; (4) high-dimensional projection; (5) cluster validation without ground truth.

### CH06 Model Evaluation, Validation, and Selection

**Reader outcome:** Estimate generalization and choose models with leakage-safe validation and metrics aligned to consequences.
**Coverage:** Cross-validation, baselines, precision/recall, Receiver Operating Characteristic (ROC) and precision-recall (PR) curves, calibration, confidence intervals, thresholding, and offline/online gaps.
**Diagram opportunities:** (1) nested data-split/evaluation workflow; (2) cross-validation folds; (3) ROC versus PR curve interpretation; (4) calibration plot; (5) offline metric versus production outcome gap.

### CH07 Deep Learning Foundations

**Reader outcome:** Explain neural-network training and diagnose optimization, regularization, and generalization failures.
**Coverage:** Tensors, layers, activations, gradient flow, backpropagation, optimizers, regularization, training loops, accelerators, and over/under-fitting.
**Diagram opportunities:** (1) forward pass and loss; (2) backpropagated gradients; (3) optimizer update; (4) vanishing/exploding gradient path; (5) training/validation curve diagnosis.

### CH08 Convolutional Neural Networks (CNNs)

**Reader outcome:** Design convolutional models for spatial data and evaluate architecture and transfer-learning choices.
**Coverage:** Convolution, filters, receptive fields, pooling, image classification, transfer learning, augmentation, and vision evaluation.
**Diagram opportunities:** (1) convolution kernel over an image; (2) receptive-field growth; (3) pooling and feature-map reduction; (4) transfer-learning layer freeze; (5) augmentation effect on input distribution.

### CH09 Recurrent Neural Networks (RNNs) and Long Short-Term Memory (LSTM)

**Reader outcome:** Explain recurrent state and gated memory for sequences, including why attention-based models changed the design trade-off.
**Coverage:** Hidden state, sequence labeling/generation, vanishing gradients, gates, LSTM memory, training parallelism, and historical transition to attention.
**Diagram opportunities:** (1) recurrent cell unrolled over time; (2) hidden-state flow; (3) LSTM input/forget/output gates; (4) gradient decay over long sequence; (5) sequential versus parallel attention computation.

### CH10 Transformers and Attention

**Reader outcome:** Explain self-attention, positional information, masking, and the computational implications of transformer architectures.
**Coverage:** Query/key/value attention, multi-head attention, positional encoding, encoder/decoder, causal masks, training/inference, context length, and scaling.
**Diagram opportunities:** (1) query-key-value attention path; (2) self-attention matrix; (3) causal mask; (4) encoder/decoder data flow; (5) context-length compute and memory growth.

### CH11 Generative Adversarial Networks (GANs)

**Reader outcome:** Explain adversarial training and identify stability and coverage failure modes in generative models.
**Coverage:** Generator/discriminator objectives, alternating optimization, conditional generation, mode collapse, stability, and use-case fit.
**Diagram opportunities:** (1) generator/discriminator adversarial loop; (2) alternating parameter updates; (3) mode collapse; (4) conditional input-to-generation path; (5) training stability signals.

### CH12 Diffusion Models

**Reader outcome:** Explain forward noising and reverse denoising, and compare sampling quality, latency, and control.
**Coverage:** Noise schedule, denoising objective, sampling steps, guidance, conditioning, latency/quality, and image/audio/video generation applications.
**Diagram opportunities:** (1) forward noise trajectory; (2) reverse denoising chain; (3) sampler steps versus latency; (4) classifier-free guidance; (5) conditioning input influence.

### CH13 Reinforcement Learning

**Reader outcome:** Model agent/environment/reward interaction and evaluate policy learning, exploration, and safety.
**Coverage:** State/action/reward, policy/value, exploration, offline/online learning, reward misspecification, safety constraints, and evaluation.
**Diagram opportunities:** (1) agent/environment feedback loop; (2) policy/value relationship; (3) exploration versus exploitation; (4) reward hacking loop; (5) offline dataset versus online interaction.

### CH14 Reinforcement Learning from Human Feedback (RLHF)

**Reader outcome:** Explain preference-data collection, reward modeling, policy optimization, and evaluation limits for aligning model behavior.
**Coverage:** Preference comparisons, reward model, supervised fine-tuning, policy optimization, direct preference alternatives, labeling cost, reward hacking, and evaluation.
**Diagram opportunities:** (1) preference data to reward model; (2) policy optimization loop; (3) human-labeling and disagreement; (4) reward model mismatch; (5) evaluation/feedback cycle.

## Large Language Models and Generative AI

### CH15 Large Language Model (LLM) Fundamentals and Inference

**Reader outcome:** Explain tokenization, autoregressive prediction, context, decoding, and the boundary between model capability and application behavior.
**Coverage:** Tokenizers, pretraining/post-training, next-token inference, context windows, decoding/sampling, quantization, model families, and limitations.
**Diagram opportunities:** (1) text-to-token sequence; (2) autoregressive next-token loop; (3) context-window budget; (4) decoding strategy comparison; (5) model capability versus system behavior boundary.

### CH16 Embeddings and Semantic Representations

**Reader outcome:** Select and use embedding models while understanding vector geometry, similarity, and representation limits.
**Coverage:** Embedding generation, vector spaces, similarity, multilingual/domain adaptation, chunk/document representations, and retrieval consequences.
**Diagram opportunities:** (1) text-to-embedding pipeline; (2) vector distance and nearest neighbors; (3) document/chunk representation; (4) model/version shift in vector space; (5) embedding quality to retrieval outcome.

### CH17 Prompt Engineering and Structured Outputs

**Reader outcome:** Design prompts and output constraints as testable inputs to a probabilistic model rather than hidden application logic.
**Coverage:** Instructions/context, examples, decomposition, structured formats, prompt injection boundaries, versioning, and empirical evaluation.
**Diagram opportunities:** (1) prompt layers and precedence; (2) context budget allocation; (3) structured-output validation/retry; (4) injection crossing an untrusted-data boundary; (5) prompt experiment and regression suite.

### CH18 Retrieval-Augmented Generation (RAG) Architecture

**Reader outcome:** Explain the ingestion-to-retrieval-to-generation path and its freshness, provenance, and access-control dependencies.
**Coverage:** Ingestion, chunking, embedding, indexing, retrieval, reranking, context assembly, generation, citation, freshness, and request path.
**Diagram opportunities:** (1) offline ingestion and index build; (2) online retrieval/generation path; (3) chunking and provenance trace; (4) retrieval/reranking/context budget; (5) document update and freshness propagation.

### CH19 Retrieval Quality and RAG Evaluation

**Reader outcome:** Measure retrieval and answer quality separately and detect regressions through representative datasets and ablations.
**Coverage:** Recall/precision, ranking metrics, faithfulness, context relevance, golden datasets, retrieval ablations, human review, and regression suites.
**Diagram opportunities:** (1) retrieval candidate/ranking funnel; (2) context relevance versus answer faithfulness; (3) golden-set evaluation loop; (4) retrieval ablation comparison; (5) online feedback to offline test set.

### CH20 Fine-Tuning, Parameter-Efficient Fine-Tuning (PEFT), and Low-Rank Adaptation (LoRA)

**Reader outcome:** Select and evaluate fine-tuning approaches while protecting data quality, capability, and deployment compatibility.
**Coverage:** Supervised fine-tuning, adapters/LoRA, curation, splits, catastrophic forgetting, merging, evaluation, and prompting/RAG alternatives.
**Diagram opportunities:** (1) base-model-to-adapter training; (2) train/validation separation; (3) parameter-efficient update path; (4) capability regression evaluation; (5) fine-tune versus prompt/RAG decision.

### CH21 Agents, Tool Calling, Memory, Planning, and Reasoning

**Reader outcome:** Bound agent loops, tool permissions, memory, retries, and human approval so nondeterministic planning remains operable.
**Coverage:** Tool schemas, orchestration loop, state/memory scope, planning, bounded steps, authorization, retries, human approval, and non-determinism.
**Diagram opportunities:** (1) model/tool/observation loop; (2) permission boundary around tool calls; (3) memory scope and persistence; (4) retry/step-budget state machine; (5) human approval and action audit.

### CH22 Model Context Protocol (MCP)

**Reader outcome:** Integrate model hosts and external tools through MCP while evaluating capability discovery, consent, transport, and security boundaries.
**Coverage:** Client/server roles, tools/resources/prompts, discovery, transport, authorization, consent, host integration, and failure behavior.
**Diagram opportunities:** (1) host/client/server topology; (2) capability discovery and invocation; (3) resource versus tool access; (4) user consent and authorization flow; (5) transport failure and tool fallback.

### CH23 Multimodal Generative AI

**Reader outcome:** Compare multimodal input/output paths and understand alignment, latency, and evaluation differences across modalities.
**Coverage:** Text/image/audio/video, encoders/decoders, modality alignment, real-time interaction, synchronization, and evaluation.
**Diagram opportunities:** (1) modality-specific encoder/decoder path; (2) cross-modal alignment; (3) audio/video streaming timeline; (4) multimodal context assembly; (5) modality-specific quality measures.

### CH24 Generative AI Evaluation, Guardrails, and Hallucinations

**Reader outcome:** Evaluate generated outputs and layer preventive, detective, and human controls around model uncertainty and misuse.
**Coverage:** Task-specific evaluation, groundedness, refusal, prompt-injection testing, content policy, guardrail failure, and human/system controls.
**Diagram opportunities:** (1) input/output evaluation pipeline; (2) grounding and citation check; (3) guardrail layers and bypass paths; (4) refusal/unsafe-output decision; (5) human review escalation.

### CH25 AI Framework Ecosystem

**Reader outcome:** Select orchestration, retrieval, agent, evaluation, and provider SDK frameworks by abstraction and lifecycle cost.
**Coverage:** Framework roles, interfaces, lock-in, observability, extensibility, provider coupling, upgrade risk, and exit strategy.
**Diagram opportunities:** (1) framework stack and abstraction layers; (2) provider adapter boundary; (3) framework dependency graph; (4) observability visibility comparison; (5) migration/exit path.

### CH26 Vector Databases for AI Retrieval

**Reader outcome:** Match AI retrieval needs to vector-store capabilities while treating index, durability, and filtering as database concerns.
**Coverage:** Retrieval workflows, vector-store products, filtering, hybrid search, durability, index updates, and Part 06 CH21 ownership recap.
**Diagram opportunities:** (1) embedding-to-vector-store request path; (2) filtered vector retrieval; (3) hybrid lexical/vector ranking; (4) index update and consistency; (5) product selection against recall/latency/durability.

### CH27 AI Infrastructure and Platform Components

**Reader outcome:** Distinguish inference engines, model servers, orchestration platforms, and ML lifecycle tools by role and operational prerequisite.
**Coverage:** vLLM, Ollama, NVIDIA Triton, Ray, KServe, MLflow, Kubeflow, model loading, accelerators, scheduling, and control-plane/data-plane boundaries.
**Diagram opportunities:** (1) model artifact to serving runtime; (2) inference engine versus platform layering; (3) accelerator scheduling and placement; (4) training/registry/deploy path; (5) platform component dependency map.

### CH28 Inference Optimization and Model Serving

**Reader outcome:** Optimize serving throughput, latency, and cost through batching, caching, quantization, placement, streaming, and capacity control.
**Coverage:** Batching/continuous batching, quantization, key-value (KV) cache, hardware placement, autoscaling, model loading, streaming, and service metrics.
**Diagram opportunities:** (1) request queue and dynamic batching; (2) KV-cache memory growth; (3) quantization quality/throughput trade-off; (4) model load and warm pool; (5) latency/throughput/cost frontier.

### CH29 Machine Learning Operations (MLOps) and Large Language Model Operations (LLMOps)

**Reader outcome:** Govern model and data artifacts through experiment, evaluation, deployment, monitoring, rollback, and retirement.
**Coverage:** Lineage, experiment tracking, registries, deployment gates, drift/quality monitoring, rollback, reproducibility, and lifecycle governance.
**Diagram opportunities:** (1) data-to-model artifact lineage; (2) experiment and model registry state; (3) evaluation gate before deployment; (4) drift detection to retraining; (5) model rollback and retirement.

### CH30 AI Data Governance, Privacy, and Provenance

**Reader outcome:** Track rights, consent, sensitivity, lineage, retention, and provenance across training and retrieval data.
**Coverage:** Licensing, consent, sensitive data, retention, training/retrieval provenance, lineage, auditability, and data/model artifact separation.
**Diagram opportunities:** (1) data source to derived artifact lineage; (2) consent and permitted-use boundary; (3) retrieval authorization at query time; (4) retention/deletion propagation; (5) model/data provenance record.

### CH31 Responsible AI and Safety Governance

**Reader outcome:** Assign accountability and controls for fairness, transparency, misuse, safety testing, human oversight, and incident response.
**Coverage:** Fairness, transparency, accountability, safety tests, misuse, human oversight, incident response, lifecycle governance, and residual risk.
**Diagram opportunities:** (1) responsibility matrix across AI lifecycle; (2) risk assessment and control gates; (3) human oversight/escalation path; (4) safety evaluation and release decision; (5) incident learning and governance update.
