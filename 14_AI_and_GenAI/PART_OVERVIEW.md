# Part 14 — Artificial Intelligence, Machine Learning, and Generative AI

Maps to the original catalog's **Part XIII — AI and GenAI**. This module
teaches model families, learning methods, generative techniques, and the
implementation foundations used to build AI capabilities.

## Scope Boundary

Part 14 owns the technical foundations and mechanisms of AI and Machine
Learning (ML): model families, training/inference behavior, embeddings,
retrieval, fine-tuning, agents, evaluation techniques, and AI infrastructure
tools. The supplemental [AI Architecture](../24_AI_Architecture/PART_OVERVIEW.md)
module owns how those capabilities are composed into production solutions,
including system boundaries, model/data/inference placement, operational
controls, and architecture trade-offs. Part 06's Vector Databases chapter
owns vector index and database mechanics; Part 14 covers their AI retrieval
use cases and recaps those storage/index owners.

## Chapters — Machine Learning and Deep Learning

| Chapter | Planned coverage | Status |
|---|---|---|
| Machine Learning Foundations | Problem types, datasets and labels, probability, statistics, linear algebra, optimization, loss functions, generalization, bias/variance, and a first end-to-end model. | Not Started |
| Data Preparation, Feature Engineering, and Leakage | Missing values, normalization, categorical features, label quality, class imbalance, train/validation/test splits, leakage, reproducible transforms, and feature provenance. | Not Started |
| Regression and Classification | Linear/logistic models, decision boundaries, regularization, threshold selection, calibration, multi-class prediction, and choosing metrics from business error costs. | Not Started |
| Decision Trees and Ensemble Learning | Tree splits and pruning, bagging, Random Forests, gradient boosting, feature importance, interpretability limits, and tabular-model selection. | Not Started |
| Unsupervised Learning and Representation Reduction | Clustering, density/anomaly detection, dimensionality reduction, distance metrics, evaluation without labels, and failure modes under changing data distributions. | Not Started |
| Model Evaluation, Validation, and Selection | Cross-validation, leakage-safe evaluation, precision/recall, ROC and PR curves, calibration, thresholding, confidence intervals, baselines, and offline-to-online gaps. | Not Started |
| Deep Learning Foundations | Tensors, layers, activations, loss/gradient flow, backpropagation, optimizers, regularization, training loops, accelerator basics, and diagnosing under/over-fitting. | Not Started |
| Convolutional Neural Networks (CNNs) | Convolution, filters, receptive fields, pooling, image classification, transfer learning, data augmentation, and vision-specific evaluation. | Not Started |
| Recurrent Neural Networks (RNNs) and Long Short-Term Memory (LSTM) | Sequence state, vanishing gradients, gated recurrence, sequence labeling/generation, and the historical shift from recurrence to attention. | Not Started |
| Transformers and Attention | Self-attention, positional information, encoder/decoder patterns, masking, training/inference differences, context cost, and why transformers scale across modalities. | Not Started |
| Generative Adversarial Networks (GANs) | Generator/discriminator objectives, adversarial training stability, mode collapse, conditional generation, and appropriate use cases. | Not Started |
| Diffusion Models | Forward noise processes, denoising objectives, sampling, guidance, latency/quality trade-offs, and image/audio/video generation applications. | Not Started |
| Reinforcement Learning | Agent/environment/reward models, policy and value learning, exploration, offline/online training, reward misspecification, and safe evaluation. | Not Started |
| Reinforcement Learning from Human Feedback (RLHF) | Preference data, reward modeling, policy optimization, direct preference alternatives, human-labeling cost, reward hacking, and evaluation limits. | Not Started |

## Chapters — Large Language Models and Generative AI

| Chapter | Planned coverage | Status |
|---|---|---|
| Large Language Model (LLM) Fundamentals and Inference | Tokenization, autoregressive training, pretraining/post-training, context windows, decoding/sampling, quantization concepts, model families, and capability limits. | Not Started |
| Embeddings and Semantic Representations | Embedding models, vector geometry, similarity, multilingual and domain adaptation, chunk/document representations, and how model choice affects retrieval. | Not Started |
| Prompt Engineering and Structured Outputs | Instruction/context design, few-shot examples, decomposition, constrained formats, prompt injection boundaries, versioning, and empirical prompt evaluation. | Not Started |
| Retrieval-Augmented Generation (RAG) Architecture | Ingestion, chunking, embedding, indexing, retrieval, reranking, context assembly, generation, citations, freshness, and end-to-end request flow. | Not Started |
| Retrieval Quality and RAG Evaluation | Recall/precision, ranking metrics, answer faithfulness, context relevance, golden datasets, retrieval ablations, human review, and regression suites. | Not Started |
| Fine-Tuning, Parameter-Efficient Fine-Tuning (PEFT), and Low-Rank Adaptation (LoRA) | Supervised fine-tuning, adapters/LoRA, data curation, training/evaluation splits, catastrophic forgetting, model merging, and when prompting or RAG is preferable. | Not Started |
| Agents, Tool Calling, Memory, Planning, and Reasoning | Tool schemas, orchestration loops, state/memory scope, planning, bounded steps, authorization boundaries, retries, human approval, and non-determinism. | Not Started |
| Model Context Protocol (MCP) | Client/server roles, tools/resources/prompts, capability discovery, transport/security boundaries, consent, and integration with agent hosts. | Not Started |
| Multimodal Generative AI | Text/image/audio/video inputs and outputs, modality encoders/decoders, alignment, real-time interaction, and evaluation differences. | Not Started |
| Generative AI Evaluation, Guardrails, and Hallucinations | Task-specific evaluation, groundedness, refusal behavior, prompt-injection testing, content policies, guardrail failure modes, and layered human/system controls. | Not Started |
| AI Framework Ecosystem | Compare orchestration, retrieval, agent, evaluation, and provider SDK frameworks by abstraction, observability, lock-in, extensibility, and upgrade risk. | Not Started |
| Vector Databases for AI Retrieval | Explain AI retrieval workflows and product fit across vector stores; recap Part 06 CH21 for index structures, filtering, durability, and database mechanics. | Not Started |
| AI Infrastructure and Platform Components | Inference engines and platforms such as vLLM, Ollama, NVIDIA Triton, Ray, KServe, MLflow, and Kubeflow; distinguish their roles and operational prerequisites. | Not Started |
| Inference Optimization and Model Serving | Batching, continuous batching, quantization, KV cache, hardware placement, autoscaling, model loading, streaming, and throughput/latency/cost decisions. | Not Started |
| Machine Learning Operations (MLOps) and Large Language Model Operations (LLMOps) | Data/model lineage, experiment tracking, registries, deployment, evaluation gates, drift/quality monitoring, rollback, and lifecycle governance. | Not Started |
| AI Data Governance, Privacy, and Provenance | Consent, licensing, retention, sensitive-data controls, training/retrieval provenance, lineage, auditability, and separation of data-plane and model artifacts. | Not Started |
| Responsible AI and Safety Governance | Fairness, transparency, accountability, misuse risk, safety testing, human oversight, incident response, and lifecycle governance across AI use cases. | Not Started |
