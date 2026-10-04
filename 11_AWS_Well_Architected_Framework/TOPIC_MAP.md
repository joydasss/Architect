# Part 11 AWS Well-Architected Framework Topic Map

This map is the bounded coverage contract for the ten Part 11 chapters. The chapters teach how to apply AWS Well-Architected Framework (WAF) review questions, lenses, workload evidence, and remediation practices. They do not re-teach AWS service mechanics or the handbook's provider-neutral architecture and quality-attribute owners. AWS guidance evolves; chapter authors must state the framework/document revision consulted and verify current pillar questions, tooling, and service references against official AWS documentation.

## Part-wide ownership boundaries

- Part 09 owns AWS products, service behavior, scope, and provider-specific implementation mechanics.
- Part 10 owns provider-neutral workload composition and cross-service architecture decisions.
- Part 11 owns the AWS WAF framework, its pillar structure and review method, AWS-specific questions and lenses, tool workflow, risk interpretation, and remediation lifecycle.
- Parts 07, 14, 15, and 19 own generic reliability objectives, observability practice, security foundations, and performance engineering. Part 11 applies those ideas through AWS review prompts without redefining them.
- Cost and sustainability concepts remain with their provider-neutral owners where established; this part teaches how to assess them through AWS WAF.
- Use AWS Well-Architected Tool, lens, and question terminology accurately for the documented version. Distinguish the official framework from custom organization policy and from architecture approval authority.

## CH01 Framework Foundations and Review Method

**Reader outcome:** Prepare and conduct a constructive AWS workload review, interpret framework questions in context, and turn evidence into decisions and improvement actions.

**Topics to cover:**

- Framework purpose, intended audience, workload scope, six-pillar structure, question model, and relationship between design principles, best practices, lenses, and tool support.
- What “well-architected” means in a particular workload: business outcomes, critical user journeys, risk appetite, operating constraints, objectives, and assumptions.
- Review is a constructive architecture conversation and improvement mechanism, not a certification, compliance audit, security guarantee, or binary pass/fail badge.
- Select review timing: early design, significant architecture change, production readiness, incident follow-up, periodic reassessment, and portfolio review; match evidence depth to lifecycle stage.
- Prepare workload context, stakeholders, diagrams, operational evidence, service inventory, prior risks, decisions, and intended review outcome.
- Interpret questions as prompts to gather evidence and reason about trade-offs, not as instructions to deploy every AWS service or satisfy a universal checklist mechanically.
- Conduct the conversation: ask for workload-specific behavior, assumptions, failure evidence, alternatives, and owner; distinguish fact, estimate, opinion, and unknown.
- Capture answers, risks, strengths, accepted risks, decisions, improvement items, owners, due dates, evidence, and revisit triggers.
- Prioritize improvements without turning a pillar score into a quality ranking; consider business impact, likelihood, cost, dependencies, and implementation readiness.
- Iterate after changes, incidents, demand shifts, new AWS features, organizational changes, or framework revisions.
- Version awareness: identify which WAF document/tool question set was used and how to manage question or lens changes over time.

**Boundaries:** Part 01 owns generic architecture review, ADR, and trade-off methods. Part 10 owns cross-provider review and architecture composition. Part 11 applies those methods to AWS WAF.

**Useful forms:** Review lifecycle diagram, evidence-preparation checklist, sample question-to-evidence trace, and a concise worked review from finding through verified improvement.

## CH02 Operational Excellence Pillar

**Reader outcome:** Evaluate whether an AWS workload can operate, change, learn, and improve safely using the pillar's current questions and workload evidence.

**Topics to cover:**

- Pillar intent and design principles: understand workload and operations, organize teams, adopt observability, automate safely, make frequent/small/reversible changes, anticipate failure, and learn from operations; verify current wording in the AWS source.
- Organization and operating model: workload ownership, platform responsibilities, team capabilities, shared-service dependencies, support boundaries, and decision rights.
- Workload preparation: requirements, architecture decisions, operational readiness, runbooks, service quotas, and deployment/rollback paths.
- Operational telemetry from an AWS review perspective: what evidence demonstrates health and business outcome; recap Part 14 for instrumentation and operational observability mechanics.
- Safe operations and automation: infrastructure as code, change controls, staged rollout, approvals where needed, idempotent procedures, recovery from partial automation, and prevention of drift.
- Deployment and release practices: deployment frequency, small changes, reversible deployments, dependency/schema compatibility, and learning from failed releases.
- Production operation: incident readiness, ownership, escalation, event response, operational procedures, and external provider responsibilities.
- Learning loop: post-incident learning, feedback into architecture and automation, operational metrics, improvement backlog, and accountability without blame.
- Trade-offs among automation, manual control, speed, safety, and operational overhead.
- Evidence: deployment history, incident records, change failure and recovery, runbook exercises, alert response, and ownership/coverage records.

**Boundaries:** Part 13 DevOps owns general delivery mechanics; Part 14 owns observability operations; Part 07 owns reliability objectives. This chapter evaluates their AWS workload application using WAF.

**Useful forms:** Operations-readiness evidence map, change lifecycle, and a scenario contrasting an automated rollback path with an unowned manual recovery.

## CH03 Security Pillar

**Reader outcome:** Review an AWS workload's security posture with WAF questions while preserving the security team's threat model, control ownership, and provider-specific implementation boundaries.

**Topics to cover:**

- Pillar intent and current design principles: strong identity foundation, traceability, defense in depth, security automation, data protection, and incident preparation; verify current framework wording.
- Security foundation and shared responsibility at workload/service scope; recap Part 09 provider responsibilities and Part 15 threat/control fundamentals.
- Identity and access review: workforce/workload principals, temporary credentials, privilege boundaries, resource policies, cross-account access, and access lifecycle. Part 09 IAM owns policy mechanics.
- Detection and traceability: audit sources, application security signals, centralized evidence, alert ownership, and investigation readiness; Part 14 owns generic observability practices.
- Infrastructure protection: network boundaries, public exposure, system integrity, configuration, patching responsibility, and protection of management paths.
- Data protection: classification, encryption, key ownership, secrets, retention, residency, backups, and copy lifecycle; link provider storage/secrets mechanics to Part 09.
- Incident response: preparation, roles, isolation, credential revocation, evidence preservation, recovery, communications, and exercises.
- Application security as review domain: secure design and development evidence, dependency/supply-chain assumptions, authorization boundaries, and testing; detailed mechanics remain with Part 15 and API owners.
- Risks of compliance theater: certifications do not prove correct workload configuration; distinguish evidence from control effectiveness.
- Security trade-offs, accepted risks, compensating controls, owner, expiry, and review trigger.

**Boundaries:** Part 15 Security owns generic security concepts and threat modeling. Part 09 owns AWS IAM, network, secrets, keys, and security-service details. Part 11 asks and interprets WAF workload questions.

**Useful forms:** Threat-to-control evidence table, privileged-access review scenario, and incident-response walkthrough.

## CH04 Reliability Pillar

**Reader outcome:** Assess whether an AWS workload can withstand change and failure, recover within business objectives, and demonstrate reliability through tests and operational evidence.

**Topics to cover:**

- Pillar intent and design principles: reliable foundations, workload architecture, change management, and failure management; verify current AWS WAF framing.
- Reliability requirements: user journeys, availability targets, RTO/RPO, dependency objectives, and business impact; Part 07 owns generic definitions.
- AWS infrastructure foundations and failure domains: account/region/AZ/service scope, quotas, managed-service contracts, and shared dependencies; provider specifics remain Part 09.
- Workload architecture: stateless/stateful boundaries, dependency design, scaling, data authority, message paths, and handling of partial failure.
- Change management: deployment safety, rollback boundaries, data/schema compatibility, configuration changes, and failure introduced by releases.
- Failure management: detection, containment, graceful degradation, retry/queue behavior, failover, recovery, failback, and prevention of split authority.
- Backup and restore evidence, including identity, keys, network, service quota, data validation, and measured end-to-end recovery.
- Testing strategy: fault injection, game days, restore tests, zonal/regional exercises, and evidence appropriate to workload risk.
- Capacity and resilience trade-offs: redundancy, standby capacity, data replication, operational complexity, and cost.
- Risk handling: objective gaps, accepted risk, owner, mitigation and tested closure evidence.

**Boundaries:** Part 07 owns resilience fundamentals and objectives; Part 09 owns AWS service failure and recovery mechanics; Part 10 owns provider-neutral workload recovery architecture. Part 11 applies the Reliability pillar.

**Useful forms:** RTO/RPO evidence trace, failure-domain map, and a review of an untested regional recovery claim.

## CH05 Performance Efficiency Pillar

**Reader outcome:** Use AWS WAF to review whether a workload selects and operates appropriate resources, measures performance, and adapts as demand and technology change.

**Topics to cover:**

- Pillar intent and current design principles: democratize advanced technology, use global reach, serverless architectures, experiment frequently, and consider mechanical sympathy where applicable; verify current AWS wording.
- Performance objectives and workload profile: throughput, latency distribution, concurrency, data volume, utilization, and representative user journeys; Part 19 owns methods.
- Architecture selection across compute, storage, database, networking, and managed services; Part 09 owns service mechanics and Part 10 owns cross-service placement.
- Workload measurements, baselines, test conditions, production telemetry, bottleneck isolation, and regression detection.
- Resource selection and right-sizing from observed demand, including accelerators and specialized capabilities when justified.
- Scaling and elasticity: horizontal/vertical, warm capacity, concurrency, queueing, quotas, downstream constraints, and performance under failure.
- Data access and transfer: locality, caching, replication, egress, storage access pattern, and trade-offs with consistency/cost.
- Experimentation and evolution: prototypes, load/chaos tests, architectural review triggers, new service evaluation, and controlled migration.
- Sustainability and cost interactions with performance decisions without duplicating CH06/general performance engineering.
- Evidence: workload test results, production metrics, scaling response, capacity assumptions, and decision history.

**Boundaries:** Part 19 owns performance engineering and measurement methods. Part 09 owns AWS service behavior. Part 10 owns general workload placement. Part 11 applies the AWS pillar questions.

**Useful forms:** Performance scenario-to-evidence matrix, bottleneck analysis, and a measured choice between two service configurations.

## CH06 Cost Optimization Pillar

**Reader outcome:** Review whether an AWS workload has financial ownership, visibility, right-sized resources, suitable pricing choices, and a continuous cost-improvement loop.

**Topics to cover:**

- Pillar intent and current design principles: financial ownership, consumption awareness, cost-effective resources, demand/supply management, and optimization over time; verify exact current wording.
- Business value and unit economics: cost per successful workload outcome, quality constraints, and shared-service allocation. Part 09 CH14 owns provider cost tooling and mechanics.
- Organization and governance: workload owner, budgets, allocation tags/accounts, forecast, anomaly response, and approval boundaries.
- Workload demand and consumption visibility: usage sources, billing dimensions, data latency, amortization, credits, and limits of cost estimates.
- Resource lifecycle and utilization: idle/oversized resources, autoscaling, schedule, storage lifecycle, snapshots, and deletion.
- Pricing and purchase models: on-demand, commitment, reserved capacity, spot/interruptible capacity; evaluate utilization, term, scope, and interruption risk.
- Architecture cost drivers: data transfer, request volume, observability, managed-service minimums, support, licenses, resiliency, and environment overhead.
- Forecast and optimize: baseline, sensitivity, experiment, measurement, change ownership, and regression detection.
- Trade-offs among cost, reliability, performance, security, sustainability, and engineering capacity.
- Evidence: cost allocation completeness, utilization, unit economics, forecast variance, commitment use, and verified savings.

**Boundaries:** Part 09 CH14 owns cross-provider cost operations and AWS pricing mechanics. Part 10 CH13 owns cloud cost architecture. Part 11 applies the AWS WAF pillar.

**Useful forms:** Cost-review evidence worksheet, one unit-cost calculation, and an optimization action traced from anomaly to verified outcome.

## CH07 Sustainability Pillar

**Reader outcome:** Evaluate the environmental sustainability of an AWS workload using WAF guidance, workload evidence, lifecycle choices, and explicit uncertainty.

**Topics to cover:**

- Pillar intent, design principles, and current AWS WAF recommendations; verify the current source and measurement tools.
- Shared responsibility and boundaries for provider data versus customer workload decisions.
- Region and service selection across carbon/energy indicators, latency, data residency, availability, and price.
- Demand and utilization: right-sized capacity, idle resources, autoscaling, batching, efficient scheduling, and successful-work normalization.
- Software and architecture efficiency: avoid duplicate work, retries, unnecessary data processing, excessive synchronous dependencies, and wasteful retention.
- Data lifecycle: collection, minimization, storage class, replication, retention, deletion, and egress.
- Hardware and device lifecycle: managed service efficiency, accelerator use, edge equipment, procurement, utilization, refresh, and embodied impacts where evidence exists.
- Measurement boundary, methodology, temporal/geographic variation, uncertainty, and responsible claims.
- Sustainability trade-offs with performance, reliability, security, cost, and data locality.
- Improvement cycle: baseline, change, measure, report, and revisit as workload/provider conditions evolve.

**Boundaries:** Part 10 CH13 owns provider-neutral cost/performance/sustainability architecture; Part 09 owns provider tools and service mechanics. Part 11 teaches the AWS WAF lens and questions.

**Useful forms:** Workload-boundary diagram, normalized impact comparison with caveats, and an optimization example that preserves service objectives.

## CH08 AWS Well-Architected Tool, Lenses, and Workload Evidence

**Reader outcome:** Organize AWS WAF reviews and evidence in the tool and apply relevant official/custom lenses without confusing tool output with architecture assurance.

**Topics to cover:**

- Workload definition: scope, environment, regions/accounts, ownership, business context, criticality, and boundaries; align tool scope with the actual review question.
- Review setup, milestones, question sets, answers, notes, improvement plans, and evidence lifecycle; verify current user interface and features.
- Pillars, AWS-provided lenses, custom lenses, industry lenses, and workload-specific application; distinguish the official framework from internal policy.
- Question interpretation, answer rationale, evidence references, assumptions, and handling not-applicable or partially applicable questions.
- High-risk identification and tool-generated findings: limitations, false positives/negatives, prioritization, and human review.
- Collaboration, permissions, multi-account organization, data sensitivity, reviewer roles, and workload ownership.
- Update/version behavior: what changes when framework questions or lenses change; preserve review history and compare versions carefully.
- Improvement plan tracking, owners, due dates, closure evidence, and feedback into architecture decisions.
- Integration boundaries with AWS Organizations, service inventory, documentation, and issue-tracking systems.
- Tool limitations: a completed review does not prove implementation, compliance, security, or production readiness.

**Boundaries:** AWS WAF tool and lens workflows are owned here; provider service implementation remains Part 09, and generic review methods are Part 10 CH15 / Part 01.

**Useful forms:** Tool workflow map, question/evidence trace, and an example of interpreting a high-risk answer without accepting the score as proof.

## CH09 Risk Prioritization and Remediation Planning

**Reader outcome:** Convert WAF findings into an actionable, risk-informed remediation portfolio with accountable decisions and verifiable closure.

**Topics to cover:**

- Finding, risk, recommendation, improvement item, and accepted risk distinctions.
- Contextual prioritization: business impact, likelihood, exposure, confidence, affected journeys, blast radius, and dependency; avoid blindly sorting by tool severity.
- Risk aggregation and systemic findings across multiple workloads/accounts versus local implementation issues.
- Remediation options: mitigate, avoid, transfer, accept, investigate, or redesign; link to existing risk/ADR owners.
- Define owner, action, success measure, due date, dependency, funding, acceptance authority, expiry/review trigger, and closure evidence.
- Sequence work by prerequisites and risk reduction; avoid treating pillar scores as comparable ordinal risk.
- Accepted-risk governance: rationale, scope, compensating controls, approver, expiry, monitoring, and revalidation.
- Validate remediation through architecture evidence, tests, configuration state, operations exercise, or cost/performance measure.
- Residual risk, risk debt, overdue actions, and escalation/reporting.
- Continuous review after incidents, workload change, new AWS service features, audit findings, and WAF revisions.

**Boundaries:** Part 01 owns general risk/ADR/trade-off reasoning; Part 15 owns risk/threat methods. Part 11 applies prioritization to AWS WAF findings.

**Useful forms:** Risk ledger, prioritization example comparing conflicting pillar findings, and closure evidence chain.

## CH10 Enterprise-Scale Reviews and Case Studies

**Reader outcome:** Apply AWS WAF across portfolios and shared platforms, distinguish local workload issues from systemic risk, and learn through evidence-based case studies.

**Topics to cover:**

- Portfolio scope and segmentation: business criticality, workload class, account/OU, regulated boundaries, ownership, and review cadence.
- Operating model for enterprise reviews: central architecture/security/platform roles, workload teams, partner reviewers, decision authority, and escalation.
- Sampling and review depth: representative patterns, risk-tiered review, change-triggered reassessment, and avoiding checkbox assessments at scale.
- Shared platform and multi-account findings: identity, network, logging, deployment, cost allocation, recovery, and common control dependencies.
- Systemic versus local findings, blast-radius analysis, root-cause patterns, reusable remediation, and policy/platform backlog.
- Portfolio trend metrics: open risk by exposure/age, accepted risk, remediation lead time, recurrence, control evidence, workload coverage, and outcome measures.
- Governance and funding: ownership, remediation capacity, exception lifecycle, executive reporting, and avoiding incentives to game scores.
- Case studies must state workload context, critical requirements, evidence, architecture choices, rejected alternatives, trade-offs, risks, remediation, and observed outcome.
- Examples across a public web/API workload, regulated data platform, serverless/event workload, and enterprise shared platform as appropriate.
- Lessons from incidents, growth, acquisitions, new services, and framework updates; anonymize examples where necessary and distinguish hypothetical scenarios from sourced outcomes.

**Boundaries:** Part 10 owns cross-provider enterprise architecture reviews; Part 11 applies AWS-specific WAF at portfolio scale. Part 09 owns AWS product mechanics; Parts 14/15/19 own specialist methods.

**Useful forms:** Portfolio review operating model, systemic-risk heatmap with explicit caveats, and two case studies traced from question to verified remediation.
