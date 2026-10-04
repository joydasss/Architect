# Part 14 — Observability Topic Map

This map backfills the coverage contract for Part 14's thirteen chapters. The part defines how systems are measured, diagnosed, and operated through logs, metrics, traces, alerts, objectives, and supporting platforms. It distinguishes the general practice from individual tools and deployments.

## Part-wide ownership boundaries

- Part 14 owns provider-neutral observability design: signal semantics, instrumentation, collection, storage/query, alerting, service-level objectives, and error budgets.
- Part 09 owns provider monitoring products; Part 12 owns Kubernetes-specific telemetry and control-plane visibility; Part 13 owns delivery pipeline instrumentation; Part 15 owns security audit and incident evidence.
- Tool chapters explain product-specific architecture and operations, not a competing definition of metrics/logs/traces or SLO practice.
- Observability data has cost, cardinality, privacy, retention, and tenant-isolation implications. Collection is not useful unless the data is trustworthy, queryable, and tied to an owner and action.

## Cross-part stakeholders and scenarios

- Service owners need actionable evidence about user-visible reliability and dependencies.
- Platform teams need scalable collectors, durable storage, access controls, and clear ownership of shared telemetry.
- Responders need to move from symptom to signal, scope, cause, mitigation, and verification under time pressure.
- Important scenarios include a latency SLO breach with no obvious infrastructure saturation; a telemetry pipeline dropping data; a cardinality explosion; and an alert that pages no owner.

## Signal Foundations

### CH01 Logs

**Reader outcome:** Design structured, contextual, and safely retained logs that support debugging without becoming an unbounded or sensitive data dump.
**Coverage:** Event versus diagnostic logs, structure/correlation IDs, severity, context, sampling, redaction, retention, access, and high-volume handling.
**Boundaries:** Part 12 owns Kubernetes container/node log collection specifics; Part 15 owns audit evidence and security response.
**Diagram opportunities:** (1) application event to collector to backend; (2) trace/correlation context propagation; (3) redaction before export; (4) retention tiers; (5) query-to-incident response flow.

### CH02 Metrics

**Reader outcome:** Instrument measurable service behavior with metrics whose types, labels, aggregation, and cardinality match operational questions.
**Coverage:** Counters, gauges, histograms, rates, dimensions, aggregation, cardinality, sampling, instrumentation libraries, and metric lifecycle.
**Boundaries:** Part 12 owns Kubernetes metric sources; Part 09 owns provider metrics products.
**Diagram opportunities:** (1) metric type and update semantics; (2) label dimensions to time-series cardinality; (3) histogram buckets to latency percentile; (4) scrape/ingest path; (5) metric lifecycle/deprecation.

### CH03 Tracing

**Reader outcome:** Follow a request across services and asynchronous boundaries to locate latency and failure causes.
**Coverage:** Trace/span/context, parent-child relationships, propagation, sampling, baggage, instrumentation, storage, and privacy.
**Boundaries:** Part 05 owns network protocols; Parts 07/08 own distributed flow/API semantics; this chapter owns trace correlation practice.
**Diagram opportunities:** (1) request trace across services; (2) parent-child span timing; (3) context propagation through queue; (4) head/tail sampling; (5) missing-span diagnosis.

### CH04 OpenTelemetry

**Reader outcome:** Use OpenTelemetry APIs, SDKs, semantic conventions, and collectors to produce portable telemetry without confusing standardization with backend neutrality.
**Coverage:** Signals, API/SDK, instrumentation, semantic conventions, context propagation, Collector pipelines, processors/exporters, resource attributes, and migration.
**Boundaries:** CH01-03 own signal meaning; tool-specific backends are covered by CH05-09.
**Diagram opportunities:** (1) instrumentation API-to-SDK pipeline; (2) Collector receiver/processor/exporter graph; (3) context propagation across services; (4) vendor-neutral instrumentation with backend exporters; (5) Collector scaling/failure boundary.

## Metrics and Visualization Tools

### CH05 Prometheus

**Reader outcome:** Operate Prometheus scraping, time-series storage, PromQL, alert rules, and federation with bounded cardinality and retention.
**Coverage:** Pull model, service discovery, scrape configuration, labels, PromQL, recording/alert rules, local TSDB, remote write, federation, and scaling limits.
**Boundaries:** Part 12 owns Kubernetes scrape targets and resource metrics; CH02 owns metric design.
**Diagram opportunities:** (1) target discovery and scrape; (2) label/cardinality path; (3) PromQL range-vector evaluation; (4) alert rule to notification; (5) local TSDB and remote storage.

### CH06 Grafana

**Reader outcome:** Build dashboards and alert views that expose operational decisions while controlling data-source, access, and change ownership.
**Coverage:** Dashboard model, data sources, variables, panels, queries, alerting, provisioning, folders/permissions, annotations, and versioning.
**Boundaries:** CH05 owns Prometheus data/queries; generic SLO and alert design remain CH10-13.
**Diagram opportunities:** (1) dashboard query/data-source path; (2) variable-driven dashboard; (3) dashboard annotation timeline; (4) alert evaluation and routing; (5) provisioned dashboard lifecycle.

### CH07 Splunk

**Reader outcome:** Design Splunk ingestion, indexing, search, dashboards, and alert workflows for operational data with explicit cost and tenancy controls.
**Coverage:** Forwarders/collectors, indexing pipeline, sourcetype/schema, search head/indexer roles, query patterns, retention, access, and deployment topology.
**Boundaries:** CH01 owns logging fundamentals; Part 09 owns provider-hosted observability services.
**Diagram opportunities:** (1) forwarder-to-indexer ingestion; (2) index/search-head query path; (3) retention and index lifecycle; (4) role/tenant search boundary; (5) ingest-volume cost control.

### CH08 Jaeger

**Reader outcome:** Operate Jaeger tracing components and storage while preserving trace context and managing sampling, retention, and query load.
**Coverage:** SDK/collector/agent architecture, sampling, ingestion, storage, query service, UI, deployment modes, scaling, and migration.
**Boundaries:** CH03 owns tracing concepts; CH04 owns OpenTelemetry instrumentation and collector standards.
**Diagram opportunities:** (1) application span to Jaeger storage; (2) agent/collector deployment options; (3) sampling and ingestion path; (4) query fan-out/storage; (5) trace retention and scaling boundary.

### CH09 Zipkin

**Reader outcome:** Collect and query distributed traces with Zipkin while understanding instrumentation, propagation, and backend trade-offs.
**Coverage:** Span model, propagation formats, collectors, storage choices, query/UI, sampling, deployment, and comparison with OpenTelemetry/Jaeger.
**Boundaries:** CH03 owns tracing semantics; CH04 owns portable instrumentation and context propagation.
**Diagram opportunities:** (1) Zipkin span collection path; (2) propagation across service calls; (3) storage and query topology; (4) sampling and trace completeness; (5) Jaeger/Zipkin/OTel responsibility comparison.

## Operations and Reliability Practice

### CH10 Alerting

**Reader outcome:** Create actionable alerts with clear ownership, symptom-oriented thresholds, and a tested response path.
**Coverage:** Alert conditions, thresholds/windows, routing, severity, inhibition/grouping, deduplication, escalation, noise, maintenance, and testing.
**Boundaries:** Tool chapters own product configuration; CH11-13 own SLO/error-budget methods.
**Diagram opportunities:** (1) signal-to-alert evaluation; (2) routing/escalation tree; (3) deduplication and grouping; (4) alert lifecycle to resolution; (5) noise and feedback tuning loop.

### CH11 SLO (Service Level Objective)

**Reader outcome:** Define and govern service-level objectives from user journeys and reliability requirements.
**Coverage:** Service-level indicator (SLI), objective, service-level agreement, eligible events, windows, target selection, ownership, and review cadence.
**Boundaries:** Part 07 owns generic requirements; Part 12 applies SLO signals to Kubernetes; Part 09 owns provider SLO offerings.
**Diagram opportunities:** (1) user journey to SLI measurement; (2) SLI window and objective threshold; (3) request-based versus window-based SLI; (4) objective hierarchy across services; (5) SLO review/change lifecycle.

### CH12 SLI (Service Level Indicator)

**Reader outcome:** Select and implement indicators that measure user-visible reliability with explicit numerator, denominator, and data-quality assumptions.
**Coverage:** Availability, latency, correctness, freshness, traffic eligibility, event counting, aggregation, missing data, burn-rate inputs, and instrumentation validation.
**Boundaries:** CH02 owns generic metrics; CH11 owns objective policy; Part 12 owns Kubernetes resource signals.
**Diagram opportunities:** (1) good/total event ratio; (2) latency threshold distribution; (3) event eligibility and exclusion; (4) instrumentation-to-SLI data path; (5) missing-data and partial-outage behavior.

### CH13 Error Budgets

**Reader outcome:** Use remaining error budget to balance reliability investment and product change under an agreed service objective.
**Coverage:** Budget calculation, burn rate, policy, release decisions, risk exceptions, multi-window alerting, resets, and learning.
**Boundaries:** Part 07 owns quality requirements; CH11-12 own SLO/SLI definitions; Part 13 owns delivery controls.
**Diagram opportunities:** (1) SLO target to error budget; (2) burn-rate trajectory; (3) release gate under budget policy; (4) exception/approval path; (5) post-incident budget review.
