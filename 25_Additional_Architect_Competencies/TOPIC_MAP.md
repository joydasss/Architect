# Part 25 — Additional Architect Competencies Topic Map

This map defines coverage for Part 25's six cross-cutting architecture competencies. The part addresses economic, governance, data, machine-learning operations, platform, and business-strategy concerns that complement the core technical parts.

## Part-wide ownership boundaries

- Part 25 owns architect-level framing and cross-team application of these competency areas, not exhaustive implementation manuals.
- Part 09 owns cloud-provider products; Part 16 owns AI and ML concepts; Part 17 owns AI system architecture; Part 18 owns enterprise architecture methods; Part 21 owns architecture documentation; Part 23 owns interpersonal practices.
- Each chapter should connect decisions to measurable outcomes, accountable owners, lifecycle costs, risks, and operational feedback.

## Cross-part stakeholders and scenarios

- Stakeholders include engineering, finance, product, data, security, compliance, platform, operations, and executive leadership.
- Important scenarios include a rising cloud bill, a compliance exception, unreliable data products, an ML model promotion, an overloaded platform team, and a strategy that does not map to funded capabilities.

## Chapters

### CH01 FinOps and Software Engineering Economics (Cost, ROI (Return on Investment))

**Reader outcome:** Compare architecture options using lifecycle economics, transparent assumptions, unit costs, and outcome-based return rather than infrastructure price alone.
**Coverage:** Total cost of ownership, cost allocation, utilization, build/buy, opportunity cost, return on investment, forecasting, cloud unit economics, and optimization governance.
**Diagram opportunities:** (1) service lifecycle cost stack; (2) unit-cost flow from usage to business outcome; (3) build/buy/operate comparison; (4) forecast, actual, and optimization feedback; (5) cost ownership and allocation map.

### CH02 Architecture Governance and Compliance

**Reader outcome:** Establish proportionate architecture controls that connect policy intent to decisions, evidence, exceptions, and continuing assurance.
**Coverage:** Principles, standards, review authority, control mapping, risk acceptance, exceptions, audit evidence, change triggers, and governance effectiveness; Part 18 owns enterprise architecture governance.
**Diagram opportunities:** (1) policy-to-control-to-evidence trace; (2) governance decision and exception lifecycle; (3) review gates in delivery flow; (4) accountability and escalation map; (5) control drift detection and remediation.

### CH03 Data Engineering for Architects

**Reader outcome:** Define data-platform boundaries and quality, lineage, access, and serving requirements in support of reliable data products.
**Coverage:** Source contracts, ingestion, batch and stream, transformations, orchestration, storage zones, catalogs, quality, lineage, privacy, and consumption.
**Diagram opportunities:** (1) source-to-data-product flow; (2) batch and streaming convergence; (3) data quality quarantine and repair; (4) lineage and ownership graph; (5) governed data access path.

### CH04 MLOps (Machine Learning Operations)

**Reader outcome:** Connect data and model changes to reproducible evaluation, controlled deployment, monitoring, rollback, and retirement.
**Coverage:** Training pipelines, datasets, feature management, experiment tracking, model registry, evaluation gates, serving, drift, and retraining triggers; Part 16 owns ML methods and Part 17 owns system architecture.
**Diagram opportunities:** (1) data-to-model-to-serving lifecycle; (2) artifact and dataset lineage; (3) evaluation and promotion gates; (4) drift detection and retraining feedback; (5) canary deployment and model rollback.

### CH05 Platform Engineering

**Reader outcome:** Design an internal platform as a product that improves delivery through supported workflows, clear ownership, and measurable adoption.
**Coverage:** Developer personas, paved paths, self-service APIs, golden paths, platform boundaries, reliability, governance, extensibility, and feedback.
**Diagram opportunities:** (1) developer journey through platform capabilities; (2) platform API and product boundary; (3) paved path with policy checks; (4) platform team and product-team responsibility map; (5) adoption and feedback loop.

### CH06 Business Architecture Strategy

**Reader outcome:** Translate business direction into capabilities, value streams, operating-model implications, and architectural change options.
**Coverage:** Business outcomes, capability maps, value streams, organization and information alignment, strategic options, investment horizons, and traceability; Part 18 owns enterprise architecture framework coverage.
**Diagram opportunities:** (1) strategy-to-capability map; (2) value stream and enabling capabilities; (3) capability heat map; (4) current-to-target operating model; (5) investment roadmap linked to outcomes.
