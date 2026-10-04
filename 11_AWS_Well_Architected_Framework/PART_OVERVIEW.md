# Part 11 — AWS Well-Architected Framework

A dedicated module for using the Amazon Web Services (AWS) Well-Architected Framework (WAF) to review, improve, and govern AWS workloads. This is intentionally separate from [Part 09 — Cloud Computing](../09_Cloud_Computing/PART_OVERVIEW.md), which introduces AWS services, and [Part 10 — Cloud Architecture](../10_Cloud_Architecture/PART_OVERVIEW.md), which teaches cross-provider workload architecture.

## Scope boundary

Part 11 owns the AWS framework's six pillars, review process, lenses, workload evidence, risk prioritization, and remediation lifecycle. It does not replace provider-service mechanics, general cloud architecture, or the handbook's separate Security, Performance, Reliability, Cost, and Sustainability concept owners; it applies those concepts using AWS-specific questions and recommendations.

Topic map: [TOPIC_MAP.md](TOPIC_MAP.md)

## Chapters

| Chapter | Focus | Status |
|---|---|---|
| Framework Foundations and Review Method | Framework purpose, workload scope, review preparation, question interpretation, documented answers, risks, improvement plan, and continuous review cadence. | Drafted ([CH01_Framework_Foundations_and_Review_Method.md](CH01_Framework_Foundations_and_Review_Method.md)) |
| Operational Excellence Pillar | Organization, workload observability, safe operations, deployment, learning, runbooks, and continuous improvement from an AWS workload-review perspective. | Drafted ([CH02_Operational_Excellence_Pillar.md](CH02_Operational_Excellence_Pillar.md)) |
| Security Pillar | Identity, detection, infrastructure protection, data protection, incident response, and application security as AWS workload review domains; detailed security mechanics remain with Part 15. | Drafted ([CH03_Security_Pillar.md](CH03_Security_Pillar.md)) |
| Reliability Pillar | Foundations, workload architecture, change management, failure management, recovery objectives, and AWS failure-domain choices. | Drafted ([CH04_Reliability_Pillar.md](CH04_Reliability_Pillar.md)) |
| Performance Efficiency Pillar | Architecture selection, compute/storage/database/network choices, review experiments, monitoring, and adaptation to evolving demand. | Drafted ([CH05_Performance_Efficiency_Pillar.md](CH05_Performance_Efficiency_Pillar.md)) |
| Cost Optimization Pillar | Financial ownership, consumption visibility, resource lifecycle, pricing models, rightsizing, and continual cost improvement. | Drafted ([CH06_Cost_Optimization_Pillar.md](CH06_Cost_Optimization_Pillar.md)) |
| Sustainability Pillar | Region/service selection, utilization, data lifecycle, efficient software, and workload-specific environmental trade-offs. | Drafted ([CH07_Sustainability_Pillar.md](CH07_Sustainability_Pillar.md)) |
| AWS Well-Architected Tool, Lenses, and Workload Evidence | Organize reviews, apply AWS and custom lenses, capture workload context, prioritize high-risk questions, and track improvement items. | Drafted ([CH08_AWS_Well_Architected_Tool_Lenses_and_Workload_Evidence.md](CH08_AWS_Well_Architected_Tool_Lenses_and_Workload_Evidence.md)) |
| Risk Prioritization and Remediation Planning | Convert review findings into severity, owner, due date, architecture decision, measurable remediation, and accepted-risk records. | Drafted ([CH09_Risk_Prioritization_and_Remediation_Planning.md](CH09_Risk_Prioritization_and_Remediation_Planning.md)) |
| Enterprise-Scale Reviews and Case Studies | Apply the framework across portfolios, shared platforms, regulated workloads, and multi-account organizations; distinguish local findings from systemic risks. | Drafted ([CH10_Enterprise_Scale_Reviews_and_Case_Studies.md](CH10_Enterprise_Scale_Reviews_and_Case_Studies.md)) |
