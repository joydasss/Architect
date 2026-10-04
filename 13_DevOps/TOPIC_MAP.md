# Part 13 — DevOps Topic Map

This map backfills the coverage contract for Part 13's 17 DevOps chapters. The part covers source collaboration, build/test/release automation, infrastructure configuration, deployment strategies, and operational experimentation. It connects engineering changes to production without claiming ownership of cloud products, Kubernetes primitives, or security foundations.

## Part-wide ownership boundaries

- Part 13 owns delivery workflow design and the use of Git, CI/CD systems, infrastructure-as-code tools, configuration management, GitOps, release controls, and chaos engineering.
- Part 09 owns cloud products; Part 12 owns Kubernetes resource semantics; Part 15 owns security foundations; Part 14 owns observability systems; Part 07 owns distributed failure semantics.
- Tool chapters explain their own execution and governance models; general delivery principles belong to the process and deployment chapters.
- Treat the software supply chain, credentials, artifact provenance, rollback, and change approval as end-to-end properties rather than a single pipeline stage.

## Cross-part stakeholders and scenarios

- Developers need fast, reproducible feedback; platform teams need policy and safe deployment primitives; operators need traceable releases and recovery paths.
- Important scenarios include a compromised dependency entering a build; an infrastructure change partially applying; a bad release reaching a subset of users; and a production hotfix diverging from declared source.

## Chapters

### CH01 Git

**Reader outcome:** Use Git history, branches, merges, tags, and review as a reliable collaboration and change-tracking substrate.
**Coverage:** Object model, commits, branches, merge/rebase, conflict resolution, tags, remotes, hooks, review, and recovery.
**Boundaries:** Part 05 owns underlying network protocols; this chapter owns Git workflows.
**Diagram opportunities:** (1) object graph and refs; (2) branch/merge history; (3) rebase versus merge; (4) conflict resolution flow; (5) revert/reset recovery decision.

### CH02 CI/CD (Continuous Integration / Continuous Delivery)

**Reader outcome:** Design an automated path from reviewed change to tested artifact and controlled deployment.
**Coverage:** Build/test stages, artifact promotion, pipeline triggers, environments, approvals, secrets, provenance, caching, failure handling, and deployment feedback.
**Boundaries:** Tool-specific behavior belongs to GitHub Actions/Jenkins/Azure DevOps; Part 15 owns security controls.
**Diagram opportunities:** (1) commit-to-artifact pipeline; (2) artifact promotion across environments; (3) test gates and failure branch; (4) secret/token trust boundary; (5) delivery feedback loop.

### CH03 Docker

**Reader outcome:** Build, package, and run container images with reproducible layers, explicit runtime configuration, and safe distribution.
**Coverage:** Image layers, Dockerfile, build context, cache, registries, tags/digests, container lifecycle, volumes, networking, and security context.
**Boundaries:** Part 05 CH28 owns container/OS internals; Part 09 owns registry products; Part 12 owns Kubernetes deployment.
**Diagram opportunities:** (1) Dockerfile-to-layer build; (2) image push/pull path; (3) container lifecycle; (4) build cache invalidation; (5) image identity and runtime configuration boundary.

### CH04 Kubernetes (deployment perspective)

**Reader outcome:** Deliver Kubernetes changes safely through declarative manifests, rollout controls, and operational verification.
**Coverage:** Manifest review, environment configuration, rollout/rollback, readiness gates, namespace targeting, secrets, ownership, and GitOps transition.
**Boundaries:** Part 12 owns Kubernetes object/controller mechanics; this chapter owns delivery workflow integration.
**Diagram opportunities:** (1) source-to-manifest-to-cluster path; (2) rolling deployment gates; (3) failed rollout rollback; (4) secret injection boundary; (5) imperative-to-declarative ownership transfer.

### CH05 GitHub Actions

**Reader outcome:** Build maintainable GitHub-hosted workflows with controlled triggers, permissions, reusable units, and deployment identity.
**Coverage:** Workflow/job/step model, runners, actions, reusable workflows, environments, secrets, OIDC federation, artifacts, caching, and concurrency.
**Boundaries:** CH02 owns CI/CD workflow theory; Part 15 owns security threat model and supply chain.
**Diagram opportunities:** (1) event-to-job execution graph; (2) runner and job isolation; (3) reusable workflow call graph; (4) OIDC credential exchange; (5) artifact provenance path.

### CH06 Jenkins

**Reader outcome:** Operate Jenkins controllers, agents, pipelines, credentials, plugins, and upgrade boundaries safely.
**Coverage:** Controller/agent topology, declarative pipelines, shared libraries, plugins, credentials, queue/executor capacity, artifact handling, and recovery.
**Boundaries:** CH02 owns pipeline concepts; Part 15 owns security baseline.
**Diagram opportunities:** (1) controller-agent execution; (2) pipeline stage/approval flow; (3) credential use boundary; (4) plugin dependency graph; (5) controller failure and restore.

### CH07 Azure DevOps

**Reader outcome:** Compose Azure DevOps repositories, pipelines, artifacts, environments, and service connections into governed delivery workflows.
**Coverage:** YAML pipelines, agents, stages, environments, approvals, artifacts, service connections, variable groups, and audit.
**Boundaries:** Part 09 owns Azure products; CH02 owns delivery principles; Part 15 owns identity/security principles.
**Diagram opportunities:** (1) pipeline-to-environment promotion; (2) hosted/self-hosted agent boundary; (3) service connection credential flow; (4) artifact provenance and retention; (5) approval and deployment record.

### CH08 Terraform

**Reader outcome:** Manage infrastructure declaratively through Terraform configuration, state, plans, providers, and controlled apply workflows.
**Coverage:** HCL, providers/resources/data, state and locking, modules, plan review, drift, imports, secrets, remote backends, and lifecycle.
**Boundaries:** Part 09 owns provider resource mechanics; this chapter owns Terraform behavior and workflow.
**Diagram opportunities:** (1) configuration-to-provider graph; (2) plan and apply state transition; (3) remote state/lock boundary; (4) module dependency graph; (5) drift detection and import/reconciliation.

### CH09 Pulumi

**Reader outcome:** Use general-purpose languages for infrastructure definitions while understanding evaluation, state, providers, and reproducibility risks.
**Coverage:** Program execution, resource graph, outputs/inputs, providers, stacks/config, state, secrets, previews, updates, and testing.
**Boundaries:** Part 09 owns cloud service resources; CH08 owns Terraform comparison and infrastructure-as-code fundamentals.
**Diagram opportunities:** (1) program evaluation to resource graph; (2) dependency/output propagation; (3) stack state and update; (4) secret/config flow; (5) Pulumi-versus-declarative HCL decision.

### CH10 Ansible

**Reader outcome:** Automate host and application configuration with idempotent plays, inventory, roles, and controlled privilege boundaries.
**Coverage:** Inventory, playbooks, modules, handlers, roles, variables, idempotency, facts, vault, check mode, and drift.
**Boundaries:** Part 05 owns OS configuration internals; CH08-09 own infrastructure provisioning.
**Diagram opportunities:** (1) inventory-to-host execution; (2) play/task/handler flow; (3) idempotent convergence; (4) privilege and secret boundary; (5) provisioning versus configuration-management sequence.

### CH11 Helm

**Reader outcome:** Package Kubernetes deployments with charts, values, templates, release history, and controlled upgrades.
**Coverage:** Chart structure, templating, values, dependencies, hooks, release state, rollback limits, signing, and OCI distribution.
**Boundaries:** Part 12 CH11 owns Helm in depth; this deployment perspective links to it and avoids duplicating its mechanics.
**Diagram opportunities:** (1) chart-to-rendered-manifest path; (2) values precedence; (3) release lifecycle; (4) dependency/artifact trust; (5) Helm versus GitOps ownership.

### CH12 GitOps

**Reader outcome:** Operate pull-based reconciliation from version-controlled desired state with clear ownership, drift, and emergency-change procedures.
**Coverage:** Repository as source of truth, controller reconciliation, sync, drift, prune, secrets, promotion, bootstrap, break-glass, and recovery.
**Boundaries:** Part 12 CH12 owns Argo CD; Part 13 owns general GitOps operating principles.
**Diagram opportunities:** (1) Git-to-controller-to-cluster loop; (2) drift/self-heal/prune decisions; (3) environment promotion; (4) break-glass change and reconciliation; (5) multi-cluster fleet ownership.

### CH13 Progressive Delivery

**Reader outcome:** Shift releases through controlled cohorts using measured health and explicit promotion/abort decisions.
**Coverage:** Progressive exposure, analysis windows, automated/manual gates, rollback, traffic shifting, experiment linkage, and risk.
**Boundaries:** Part 12 owns Kubernetes mechanisms; Part 14 owns telemetry; this chapter owns delivery policy.
**Diagram opportunities:** (1) release cohort progression; (2) metric gate and analysis window; (3) abort/rollback flow; (4) traffic shift and capacity; (5) canary-to-full-promotion evidence.

### CH14 Feature Flags

**Reader outcome:** Use runtime flags to decouple deployment from exposure while managing evaluation, ownership, cleanup, and failure behavior.
**Coverage:** Release/experiment/ops/permissioning flags, targeting, evaluation service, caching, kill switches, audit, flag debt, and privacy.
**Boundaries:** CH13 owns progressive release; Part 15 owns authorization and security controls.
**Diagram opportunities:** (1) flag evaluation request path; (2) deploy-versus-release separation; (3) targeting cohort; (4) kill-switch outage behavior; (5) flag lifecycle and cleanup.

### CH15 Blue-Green Deployment

**Reader outcome:** Operate two production-capable environments and shift traffic with explicit state and rollback constraints.
**Coverage:** Environment parity, routing switch, database compatibility, warm-up, capacity cost, smoke tests, rollback, and cleanup.
**Boundaries:** CH13 owns broader progressive delivery; Part 09 owns provider traffic services.
**Diagram opportunities:** (1) blue/green topology; (2) traffic switch sequence; (3) database expand/contract compatibility; (4) rollback before/after migration; (5) cost/capacity trade-off.

### CH16 Canary Deployment

**Reader outcome:** Expose a small traffic or user cohort to a release and promote or abort based on pre-defined evidence.
**Coverage:** Cohort selection, traffic splitting, metrics, analysis windows, sample bias, automated gates, rollback, and progressive ramp.
**Boundaries:** CH13 owns progressive delivery governance; Part 14 owns measurement/alerting; Part 12 owns Kubernetes traffic mechanics.
**Diagram opportunities:** (1) traffic cohort ramp; (2) metric comparison; (3) canary analysis window; (4) abort and rollback path; (5) biased cohort detection.

### CH17 Chaos Engineering

**Reader outcome:** Run controlled experiments that test resilience assumptions while bounding blast radius and preserving a recovery path.
**Coverage:** Hypothesis, steady state, experiment design, fault injection, scope, abort criteria, observation, learning, and governance.
**Boundaries:** Part 07 owns distributed failure semantics; Part 14 owns observability; this chapter owns experiment lifecycle.
**Diagram opportunities:** (1) hypothesis-to-experiment loop; (2) blast-radius boundary; (3) steady-state measurement; (4) abort/rollback mechanism; (5) experiment result to remediation.
