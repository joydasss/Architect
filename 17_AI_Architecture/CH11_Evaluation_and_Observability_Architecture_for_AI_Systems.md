# Evaluation and Observability Architecture for AI Systems

Part: [17 — AI Architecture](PART_OVERVIEW.md)

AI observability architecture connects a user-visible outcome to the data, model, prompt, retrieval, policy, and runtime decisions that produced it. It must support release evaluation, live diagnosis, and safe feedback while minimizing sensitive-data exposure. Part 14 owns observability platforms and telemetry mechanics; Part 16 owns evaluation methods. This chapter specifies the evidence and correlation contracts between them.

## Connect Offline and Online Evidence

Offline evaluation estimates behavior on a controlled dataset before release. Online signals show what happens under real traffic, evolving populations, and operational dependencies. Neither replaces the other: offline data can be stale or unrepresentative, while online feedback is selective and arrives after users are affected. Use online signals to identify questions and incidents, then update reviewed evaluation cases rather than treating every interaction as ground truth.

```mermaid
flowchart LR
    EvalSet[Versioned evaluation set] --> Offline[Offline quality and risk evaluation]
    Candidate[Candidate release manifest] --> Offline
    Offline --> Gate[Release decision and thresholds]
    Gate --> Release[Controlled deployment]
    Release --> Online[Production outcomes and traces]
    Online --> Signals[Quality, latency, cost, and harm signals]
    Signals --> Review[Human triage and label validation]
    Review --> Cases[Reviewed regression cases]
    Cases --> EvalSet
```

Keep evaluation set lineage, label process, and known gaps. Changes to a judge model, rubric, or sampling method can change measured quality even when the candidate is unchanged. Version the evaluator and record the evidence used for each release decision.

## Trace the Request Across Components

A request trace should link identity context, retrieval or feature access, model endpoint, validation, human review, and downstream action. Use a correlation identifier and span relationships rather than placing full prompts and responses into every telemetry event. Record stable references to sensitive evidence where authorized; enforce retention and access policy on the trace store.

```mermaid
sequenceDiagram
    actor User
    participant App as Application workflow
    participant Data as Data or retrieval service
    participant Model as Model gateway
    participant Review as Human review
    participant Action as Downstream action
    User->>App: Submit task
    App->>App: Assign trace and release-manifest IDs
    App->>Data: Read scoped evidence
    Data-->>App: Evidence references and versions
    App->>Model: Send bounded request
    Model-->>App: Output, model version, provider request ID
    App->>App: Validate and record policy outcome
    App->>Review: Route if required
    Review-->>App: Decision and reason
    App->>Action: Execute approved action
    Action-->>App: Result identifier and status
```

Define a trace schema that remains useful across providers: workload and tenant identifiers, request ID, model and prompt version, index or feature version, policy result, latency stages, token or compute usage where available, validation status, and outcome reference. Do not use raw user text as a high-cardinality metric label. Part 14 owns trace transport and storage decisions.

## Attribute Behavior to Versions

Version attribution needs to travel from release configuration into every request and derived evaluation. A human-readable model name can be reused or redirected; prefer immutable artifact digests or provider version identifiers, and record the adapter and routing policy too. A response may depend on multiple versions, including prompts, retrieval indexes, guardrails, and tool schemas.

```mermaid
flowchart TD
    Registry[Approved release manifest] --> Runtime[Runtime configuration]
    Runtime --> Request[Request context]
    Request --> Retrieval[Feature or index version]
    Request --> Model[Model and adapter version]
    Request --> Prompt[Prompt and tool schema version]
    Request --> Policy[Policy and threshold version]
    Retrieval --> Trace[Correlated trace metadata]
    Model --> Trace
    Prompt --> Trace
    Policy --> Trace
    Trace --> Outcome[User outcome and review result]
```

Fail closed when the runtime cannot report the version required by the release contract. If an external provider changes behavior behind a stable name, record the provider's available deployment identity and schedule a re-evaluation. Version metadata is operational evidence, not a substitute for testing.

## Curate Feedback Into Evaluation

Feedback can be explicit, such as a correction or complaint, or implicit, such as abandonment, repeated edits, or other behavior. It is biased by who chooses to respond, the interface, and the outcome's visibility. Triage feedback for validity, privacy, representativeness, and causal relevance before adding it to a regression set or training corpus.

```mermaid
flowchart LR
    Feedback[User correction, override, or incident] --> Minimize[Apply privacy and retention controls]
    Minimize --> Triage[Classify feedback and validate evidence]
    Triage -->|Duplicate or invalid| Discard[Discard with bounded metadata]
    Triage -->|Valid behavior gap| Case[Create reviewed test case]
    Case --> Owner[Assign domain and evaluation owner]
    Owner --> Suite[Versioned regression suite]
    Suite --> Candidate[Run on candidate release]
    Candidate --> Decision[Review result and decide]
```

Do not automatically train on user corrections or operator overrides. Verify whether the correction reflects factual error, a policy update, user preference, or a changed source. Apply consent and data-governance rules before retaining feedback; preserve a reason code and label provenance so future reviewers can interpret it.

## Detect Regressions and Investigate Incidents

AI quality signals should be paired with service health and workflow outcomes. Track task-specific quality indicators alongside latency, error rate, saturation, cost, abstention, correction, and escalation. Establish alert thresholds from a baseline and account for sample size and delayed labels. A sudden score change can result from traffic mix, evaluator changes, source freshness, model routing, or a real behavior regression.

```mermaid
flowchart TD
    Signal[Quality, safety, or service signal] --> Threshold{Threshold and sample rules met?}
    Threshold -->|No| Trend[Continue trend analysis]
    Threshold -->|Yes| Alert[Alert accountable owner]
    Alert --> Scope[Scope affected users, versions, and time window]
    Scope --> Trace[Inspect correlated traces and evidence references]
    Trace --> Cause{Likely cause}
    Cause -->|Release behavior| Rollback[Restrict or roll back release]
    Cause -->|Data or retrieval| Repair[Repair source, index, or pipeline]
    Cause -->|Dependency or capacity| Degrade[Apply safe degraded mode]
    Cause -->|Label or evaluator| Recheck[Review measurement validity]
    Rollback --> Review[Incident review and regression case]
    Repair --> Review
    Degrade --> Review
    Recheck --> Review
```

Define who can restrict traffic and what signals justify immediate action. The incident process should preserve the release manifest and sampled evidence needed for investigation while respecting privacy. Close the loop by adding a reviewed regression case or documenting why the signal was not actionable.

## Worked Case: Unsupported Answer Increase

After a prompt and model update, a support assistant's citation-validity signal declines. The observability pipeline correlates the change to the new manifest, identifies which regions and traffic cohorts are affected, and samples traces under approved redaction rules. Reviewers find that the new model often cites a retrieved passage that does not support the claim. The team restricts the canary, returns traffic to the prior manifest, and adds reviewed failure cases to the evaluation suite.

The investigation also checks whether a retrieval-index refresh or evaluator change caused the apparent regression. It compares candidate and prior releases on the same evaluation set and verifies the index version in traces. The incident closes only after the corrected candidate passes the gate and a staged rollout reproduces the improvement without increasing latency or cost beyond agreed limits.

## Review Questions

1. Which version identifiers must be attached to an online outcome?
2. Why should user feedback be reviewed before it becomes a training label?
3. How can traffic-mix change resemble model drift?
4. What evidence does an incident responder need without retaining raw prompts indefinitely?
5. Which signal can trigger restriction or rollback, and who owns that decision?

AI observability is useful when evidence is attributable and can drive a decision. Connect offline gates to production traces, preserve version and policy context, treat feedback as biased evidence, and make incident signals actionable without over-collecting sensitive content.
