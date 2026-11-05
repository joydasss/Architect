# Part 16 — Artificial Intelligence, Machine Learning, and Generative AI

Maps to the original catalog's **Part XIII — AI and GenAI**. This module
teaches model families, learning methods, generative techniques, and the
implementation foundations used to build AI capabilities.

Topic map: [TOPIC_MAP.md](TOPIC_MAP.md)

## Scope Boundary

Part 16 owns the technical foundations and mechanisms of AI and Machine
Learning (ML): model families, training/inference behavior, embeddings,
retrieval, fine-tuning, agents, evaluation techniques, and AI infrastructure
tools. The supplemental [AI Architecture](../17_AI_Architecture/PART_OVERVIEW.md)
module owns how those capabilities are composed into production solutions,
including system boundaries, model/data/inference placement, operational
controls, and architecture trade-offs. Part 06's Vector Databases chapter
owns vector index and database mechanics; Part 16 covers their AI retrieval
use cases and recaps those storage/index owners.

## Chapters — Machine Learning and Deep Learning

| Chapter | Planned coverage | Status |
|---|---|---|
| Machine Learning Foundations | Problem types, datasets and labels, probability, statistics, linear algebra, optimization, loss functions, generalization, bias/variance, and a first end-to-end model. | Revised (in-depth rewrite) |
| Data Preparation, Feature Engineering, and Leakage | Missing values, normalization, categorical features, label quality, class imbalance, train/validation/test splits, leakage, reproducible transforms, and feature provenance. | Revised (in-depth rewrite) |
| Regression and Classification | Linear/logistic models, decision boundaries, regularization, threshold selection, calibration, multi-class prediction, and choosing metrics from business error costs. | Revised (in-depth rewrite) |
| Decision Trees and Ensemble Learning | Tree splits and pruning, bagging, Random Forests, gradient boosting, feature importance, interpretability limits, and tabular-model selection. | Revised (in-depth rewrite) |
| Unsupervised Learning and Representation Reduction | Clustering, density/anomaly detection, dimensionality reduction, distance metrics, evaluation without labels, and failure modes under changing data distributions. | Revised (in-depth rewrite) |
| Model Evaluation, Validation, and Selection | Cross-validation, leakage-safe evaluation, precision/recall, ROC and PR curves, calibration, thresholding, confidence intervals, baselines, and offline-to-online gaps. | Revised (in-depth rewrite) |
| Deep Learning Foundations | Tensors, layers, activations, loss/gradient flow, backpropagation, optimizers, regularization, training loops, accelerator basics, and diagnosing under/over-fitting. | Revised (in-depth rewrite) |
| Convolutional Neural Networks (CNNs) | Convolution, filters, receptive fields, pooling, image classification, transfer learning, data augmentation, and vision-specific evaluation. | Revised (in-depth rewrite) |
| Recurrent Neural Networks (RNNs) and Long Short-Term Memory (LSTM) | Sequence state, vanishing gradients, gated recurrence, sequence labeling/generation, and the historical shift from recurrence to attention. | Revised (in-depth rewrite) |
| Transformers and Attention | Self-attention, positional information, encoder/decoder patterns, masking, training/inference differences, context cost, and why transformers scale across modalities. | Revised (in-depth rewrite) |
| Generative Adversarial Networks (GANs) | Generator/discriminator objectives, adversarial training stability, mode collapse, conditional generation, and appropriate use cases. | Revised (in-depth rewrite) |
| Diffusion Models | Forward noise processes, denoising objectives, sampling, guidance, latency/quality trade-offs, and image/audio/video generation applications. | Revised (in-depth rewrite) |
| Reinforcement Learning | Agent/environment/reward models, policy and value learning, exploration, offline/online training, reward misspecification, and safe evaluation. | Revised (in-depth rewrite) |
| Reinforcement Learning from Human Feedback (RLHF) | Preference data, reward modeling, policy optimization, direct preference alternatives, human-labeling cost, reward hacking, and evaluation limits. | Revised (in-depth rewrite) |
| Machine Learning Foundations | Problem types and data/label/objective relationships, optimization, generalization, and a first end-to-end model. | Revised (in-depth rewrite) |
| Data Preparation, Feature Engineering, and Leakage | Missingness, transformations, labels, temporal/group splits, leakage, reproducibility, and lineage. | Revised (in-depth rewrite) |
| Regression and Classification | Linear/logistic models, decision boundaries, regularization, thresholding, calibration, metrics, and error costs. | Revised (in-depth rewrite) |
| Decision Trees and Ensemble Learning | Tree splits/pruning, bagging, forests, boosting, feature-importance limits, and model selection. | Revised (in-depth rewrite) |
| Unsupervised Learning and Representation Reduction | Clustering, anomaly detection, dimensionality reduction, distance, evaluation without labels, and drift. | Revised (in-depth rewrite) |
| Model Evaluation, Validation, and Selection | Validation design, metrics, calibration, uncertainty, baselines, and offline/online gaps. | Revised (in-depth rewrite) |
| Deep Learning Foundations | Tensors, layers, gradients, optimization, regularization, training loops, accelerators, and diagnosis. | Revised (in-depth rewrite) |
| Convolutional Neural Networks (CNNs) | Convolution, receptive fields, pooling, transfer learning, augmentation, and vision evaluation. | Revised (in-depth rewrite) |
| Recurrent Neural Networks (RNNs) and Long Short-Term Memory (LSTM) | Recurrent state, gated memory, vanishing gradients, sequence tasks, and attention trade-offs. | Revised (in-depth rewrite) |
| Transformers and Attention | Attention, positional information, masking, architecture patterns, context cost, and inference. | Revised (in-depth rewrite) |
| Generative Adversarial Networks (GANs) | Adversarial objectives, training stability, mode collapse, diversity, and use-case fit. | Revised (in-depth rewrite) |
| Diffusion Models | Noise schedules, denoising, sampling, guidance, quality/latency, and applications. | Revised (in-depth rewrite) |
| Reinforcement Learning | MDPs, policies, value, exploration, offline/online learning, reward risks, and safety. | Revised (in-depth rewrite) |
| Reinforcement Learning from Human Feedback (RLHF) | Preference data, reward modeling, policy optimization, bias, reward hacking, and evaluation. | Revised (in-depth rewrite) |

## Chapters — Large Language Models and Generative AI

| Chapter | Planned coverage | Status |
|---|---|---|
| Large Language Model (LLM) Fundamentals and Inference | Tokenization, autoregressive training, pretraining/post-training, context windows, decoding/sampling, quantization concepts, model families, and capability limits. | Revised (in-depth rewrite) |
| Embeddings and Semantic Representations | Embedding models, vector geometry, similarity, multilingual and domain adaptation, chunk/document representations, and how model choice affects retrieval. | Revised (in-depth rewrite) |
| Prompt Engineering and Structured Outputs | Instruction/context design, few-shot examples, decomposition, constrained formats, prompt injection boundaries, versioning, and empirical prompt evaluation. | Revised (in-depth rewrite) |
| Retrieval-Augmented Generation (RAG) Architecture | Ingestion, chunking, embedding, indexing, retrieval, reranking, context assembly, generation, citations, freshness, and end-to-end request flow. | Revised (in-depth rewrite) |
| Retrieval Quality and RAG Evaluation | Recall/precision, ranking metrics, answer faithfulness, context relevance, golden datasets, retrieval ablations, human review, and regression suites. | Revised (in-depth rewrite) |
| Fine-Tuning, Parameter-Efficient Fine-Tuning (PEFT), and Low-Rank Adaptation (LoRA) | Supervised fine-tuning, adapters/LoRA, data curation, training/evaluation splits, catastrophic forgetting, model merging, and when prompting or RAG is preferable. | Revised (in-depth rewrite) |
| Agents, Tool Calling, Memory, Planning, and Reasoning | Tool schemas, orchestration loops, state/memory scope, planning, bounded steps, authorization boundaries, retries, human approval, and non-determinism. | Revised (in-depth rewrite) |
| Model Context Protocol (MCP) | Client/server roles, tools/resources/prompts, capability discovery, transport/security boundaries, consent, and integration with agent hosts. | Revised (in-depth rewrite) |
| Multimodal Generative AI | Text/image/audio/video inputs and outputs, modality encoders/decoders, alignment, real-time interaction, and evaluation differences. | Revised (in-depth rewrite) |
| Generative AI Evaluation, Guardrails, and Hallucinations | Task-specific evaluation, groundedness, refusal behavior, prompt-injection testing, content policies, guardrail failure modes, and layered human/system controls. | Revised (in-depth rewrite) |
| AI Framework Ecosystem | Compare orchestration, retrieval, agent, evaluation, and provider SDK frameworks by abstraction, observability, lock-in, extensibility, and upgrade risk. | Revised (in-depth rewrite) |
| Vector Databases for AI Retrieval | Explain AI retrieval workflows and product fit across vector stores; recap Part 06 CH21 for index structures, filtering, durability, and database mechanics. | Revised (in-depth rewrite) |
| AI Infrastructure and Platform Components | Inference engines and platforms such as vLLM, Ollama, NVIDIA Triton, Ray, KServe, MLflow, and Kubeflow; distinguish their roles and operational prerequisites. | Revised (in-depth rewrite) |
| Inference Optimization and Model Serving | Batching, continuous batching, quantization, KV cache, hardware placement, autoscaling, model loading, streaming, and throughput/latency/cost decisions. | Revised (in-depth rewrite) |
| Machine Learning Operations (MLOps) and Large Language Model Operations (LLMOps) | Data/model lineage, experiment tracking, registries, deployment, evaluation gates, drift/quality monitoring, rollback, and lifecycle governance. | Revised (in-depth rewrite) |
| AI Data Governance, Privacy, and Provenance | Consent, licensing, retention, sensitive-data controls, training/retrieval provenance, lineage, auditability, and separation of data-plane and model artifacts. | Revised (in-depth rewrite) |
| Responsible AI and Safety Governance | Fairness, transparency, accountability, misuse risk, safety testing, human oversight, incident response, and lifecycle governance across AI use cases. | Revised (in-depth rewrite) |
| Large Language Model (LLM) Fundamentals and Inference | Tokenization, autoregressive prediction, training, context, decoding, quantization, and capability limits. | Revised (in-depth rewrite) |
| Embeddings and Semantic Representations | Embedding geometry, similarity, domain adaptation, document representation, and retrieval consequences. | Revised (in-depth rewrite) |
| Prompt Engineering and Structured Outputs | Prompt composition, context allocation, output schemas, injection boundaries, versioning, and evaluation. | Revised (in-depth rewrite) |
| Retrieval-Augmented Generation (RAG) Architecture | Ingestion, chunking, embedding, retrieval, authorization, context, generation, citations, and freshness. | Revised (in-depth rewrite) |
| Retrieval Quality and RAG Evaluation | Retrieval metrics, grounding, citation quality, datasets, ablations, human review, and regression. | Revised (in-depth rewrite) |
| Fine-Tuning, Parameter-Efficient Fine-Tuning (PEFT), and Low-Rank Adaptation (LoRA) | Fine-tuning and PEFT data, objectives, artifacts, forgetting, evaluation, and alternatives. | Revised (in-depth rewrite) |
| Agents, Tool Calling, Memory, Planning, and Reasoning | Bounded loops, tools, authorization, memory, checkpoints, retries, approval, and evaluation. | Revised (in-depth rewrite) |
| Model Context Protocol (MCP) | Host/client/server roles, capability discovery, consent, authorization, transport, and failures. | Revised (in-depth rewrite) |
| Multimodal Generative AI | Modality encoders/decoders, alignment, streaming, evaluation, privacy, and cost. | Revised (in-depth rewrite) |
| Generative AI Evaluation, Guardrails, and Hallucinations | Task quality, grounding, refusal, guardrails, red teaming, and release gates. | Revised (in-depth rewrite) |
| AI Framework Ecosystem | Framework roles, abstraction, lock-in, operations, versioning, and exit strategy. | Revised (in-depth rewrite) |
| Vector Databases for AI Retrieval | AI retrieval workflows and vector-store fit; Part 06 CH21 owns index and database mechanics. | Revised (in-depth rewrite) |
| AI Infrastructure and Platform Components | Inference engines, model servers, accelerators, scheduling, registries, and operations. | Revised (in-depth rewrite) |
| Inference Optimization and Model Serving | Batching, KV cache, quantization, placement, autoscaling, streaming, and cost/latency. | Revised (in-depth rewrite) |
| Machine Learning Operations (MLOps) and Large Language Model Operations (LLMOps) | Lineage, evaluation, promotion, monitoring, rollback, and retirement. | Revised (in-depth rewrite) |
| AI Data Governance, Privacy, and Provenance | Rights, consent, sensitivity, lineage, retention, deletion, and provenance. | Revised (in-depth rewrite) |
| Responsible AI and Safety Governance | Impact, fairness, accountability, safety, human oversight, and incident governance. | Revised (in-depth rewrite) |

## Supplemental Module

[AI Architecture](../17_AI_Architecture/PART_OVERVIEW.md) composes the model,
data, retrieval, agent, inference, and platform capabilities introduced here
into end-to-end systems. This part remains the owner of model families,
algorithms, GenAI techniques, and AI infrastructure implementation details.

## Planned Additional Chapters

These chapters fill gaps found during the in-depth rewrite. No chapter files, topic-map entries, or concept-registry entries exist yet; each will be added when the chapter is drafted. The existing 31 chapters are each at least 23,000 words (excluding diagrams).

| Chapter | Planned coverage | Status |
|---|---|---|
| Time Series Forecasting | Stationarity, decomposition, classical models (ARIMA, exponential smoothing), gradient-boosted and neural forecasters, hierarchical forecasts, backtesting with rolling origins, probabilistic forecasts, and forecast monitoring. | Planned (not yet drafted) |
| Recommender Systems and Ranking | Candidate generation and ranking, collaborative filtering, two-tower models, learning to rank, cold start, feedback loops and bias, exploration, and offline versus online evaluation. | Planned (not yet drafted) |
| Explainability, Interpretability, and Uncertainty | Global and local explanations (permutation importance, SHAP, counterfactuals), interpretable models, limits of explanations, calibration, conformal prediction, and uncertainty for decisions. | Planned (not yet drafted) |
| Distributed Training, Scaling Laws, and Hardware | Data, tensor, pipeline, and expert parallelism, sharded optimizers, communication costs, checkpointing and fault tolerance, scaling laws, compute budgeting, and accelerator memory and interconnect limits. | Planned (not yet drafted) |
| Modern LLM Architectures: Mixture of Experts, Reasoning Models, and State-Space Models | Sparse expert routing, long-context and efficient attention variants, reasoning models and test-time compute, distillation, state-space and hybrid architectures, and the architectural consequences for serving and cost. | Planned (not yet drafted) |
