# Chaos Engineering

Part: [13 — DevOps](PART_OVERVIEW.md)

Chaos engineering uses controlled experiments to test whether a system behaves as expected under realistic failures. It begins with a falsifiable hypothesis and a measurable steady state, then introduces a bounded perturbation, observes the result, and converts gaps into remediation. It is not random damage or a substitute for testing. Part 07 owns distributed failure semantics; Part 14 owns observability; this chapter owns the experiment lifecycle and operational controls.

## Hypothesis and Steady State

Start with an operationally meaningful hypothesis: for example, if one availability zone becomes unreachable, request success remains above a target and recovery completes within a bound. Define the steady state using user-visible measures, dependencies, and system capacity. If the baseline is already unstable or unmeasured, a fault experiment cannot distinguish ordinary variation from experiment impact.

```mermaid
flowchart LR
    Question[Unverified resilience assumption] --> Hypothesis[Falsifiable hypothesis]
    Hypothesis --> Steady[Measure steady state]
    Steady --> Design[Choose fault and blast-radius limit]
    Design --> Run[Execute controlled experiment]
    Run --> Observe[Compare actual behavior]
    Observe --> Learning[Remediate or update confidence]
    Learning --> Question
```

Specify the fault, target population, expected response, abort condition, owner, communication plan, and evidence before execution. A useful hypothesis names a stimulus and an outcome: “When a replica is unavailable, the service continues to meet its latency objective for affected requests,” rather than “the system is resilient.”

## Experiment Scope and Fault Selection

Faults can target process termination, dependency latency, network loss, resource exhaustion, zone failure, credential expiry, or queue pressure. Select an experiment from a known risk and increase impact gradually. Test in a representative environment first; production experiments require explicit authorization, safeguards, and on-call readiness. Use game days or manual drills when automated fault injection could exceed safe bounds.

```mermaid
flowchart TD
    Risk[Known resilience risk] --> FaultType{Failure domain}
    FaultType -->|Process| Kill[Terminate one process]
    FaultType -->|Network| Delay[Add bounded latency or loss]
    FaultType -->|Dependency| Unavailable[Block one dependency]
    FaultType -->|Capacity| Exhaust[Constrain one resource]
    FaultType -->|Zone| Isolate[Isolate a bounded zone]
    Kill --> Scope[Select smallest representative target]
    Delay --> Scope
    Unavailable --> Scope
    Exhaust --> Scope
    Isolate --> Scope
```

```mermaid
flowchart TD
    Scope[Experiment target] --> Limit[Blast-radius constraints]
    Limit --> Fault[Inject one bounded fault]
    Fault --> Guard{Abort signal triggered?}
    Guard -->|Yes| Stop[Stop injection and restore]
    Guard -->|No| Observe[Observe steady-state measures]
    Observe --> Complete{Experiment limit reached?}
    Complete -->|No| Fault
    Complete -->|Yes| Restore[Restore normal conditions]
    Stop --> Verify[Verify recovery]
    Restore --> Verify
```

Blast radius may be bounded by tenant, region, percentage of hosts, duration, or rate. Limit the experiment's authority so a targeting error cannot affect the entire fleet. Use independent safety controls where possible: a kill switch outside the experiment process, rate cap, health-based abort, and human stop authority. Test these controls before the experiment.

## Observation, Abort, and Recovery

Observe both the target and nearby dependencies. A process kill may reveal restart behavior but also saturate the remaining fleet; network latency may trigger retries that amplify load; queue backlog may persist after injection stops. Measure user outcomes, saturation, recovery time, error budgets, and unintended effects. Part 14 owns telemetry implementation; experiments must have adequate instrumentation before fault injection begins.

```mermaid
sequenceDiagram
    participant Lead as Experiment lead
    participant Guard as Independent safety guard
    participant System as Target system
    participant Telemetry as Observability
    Lead->>Guard: Register hypothesis, scope, limits, and abort rules
    Guard-->>Lead: Confirm prerequisites and stop control
    Lead->>System: Inject bounded fault
    System-->>Telemetry: Health, load, and user outcomes
    Telemetry-->>Guard: Threshold and freshness signals
    alt Abort threshold breached
        Guard->>System: Stop fault and restore baseline
        System-->>Telemetry: Recovery evidence
    else Limits reached safely
        Lead->>System: End experiment
    end
```

Abort immediately when user impact exceeds the agreed threshold, telemetry becomes unavailable, scope is uncertain, or the recovery mechanism fails. The experiment owner should not be the only person capable of stopping it. After injection, verify the fault is removed and the system returns to steady state; a green dashboard without checking residual state is insufficient.

## Governance and Learning

Production experimentation needs change approval appropriate to impact, stakeholder notification, an accountable incident commander or on-call contact, and a maintenance window when relevant. Coordinate with customer commitments and regulatory restrictions. Document experiment IDs so incidents can distinguish injected faults from unrelated changes.

An experiment that passes increases confidence only in the tested conditions. Record limitations, sample scope, dependency versions, and unexpected behavior. Turn findings into owned remediation with priority and retest criteria. Do not reward experiment count; reward reduced uncertainty and verified resilience improvement. Avoid experiments that merely demonstrate a known failure without learning or a decision.

```mermaid
stateDiagram-v2
    [*] --> Proposed
    Proposed --> Reviewed: hypothesis and risk bounded
    Reviewed --> Ready: telemetry, owners, and stop controls verified
    Ready --> Running: authorized window
    Running --> Aborted: safety signal or uncertainty
    Running --> Completed: limits reached
    Aborted --> Restoring
    Completed --> Restoring
    Restoring --> Debrief: baseline verified
    Debrief --> Remediation: actionable gap found
    Debrief --> Revalidated: hypothesis supported
    Remediation --> Revalidated: fix tested
    Revalidated --> [*]
```

## Worked Case: Dependency Zone Loss

A team believes its service can tolerate loss of one dependency zone. It defines steady-state success rate and latency by zone, identifies the affected test tenant, and sets a five-minute duration and strict abort threshold. A separate safety guard observes error rate and dependency saturation. The team blocks new experiment traffic if evidence becomes stale.

The fault increases retries and saturates the remaining zone before user success drops. The guard aborts; the team confirms traffic returns to normal and finds that retry budgets were not coordinated across service layers. The finding becomes a remediation task with a test that reproduces the load amplification. A later experiment verifies behavior after the fix. The experiment did not “prove resilience”; it revealed a concrete failure mechanism and tested the improvement.

## Common Mistakes and Review Checklist

- Running a fault without a falsifiable hypothesis or measurable baseline.
- Targeting too much production capacity or using the same process as the only stop mechanism.
- Continuing when metrics are delayed, missing, or cannot distinguish user impact.
- Injecting several faults at once, making cause and effect unclear.
- Treating a successful run as proof beyond the tested scope.
- Stopping injection without verifying system recovery and cleanup.
- Recording findings without owners, priorities, and retest criteria.

Before execution, verify hypothesis, steady state, target selection, blast-radius limit, dependency impact, authorization, communications, on-call coverage, independent stop control, telemetry freshness, restore procedure, and debrief owner. Afterward, verify return to normal and track remediation to a repeatable validation.

## Questions and Summary

1. Write a falsifiable hypothesis for a dependency latency experiment, including measurable success and abort conditions.
2. Draw the experiment and an independent safety guard; explain how the guard stops injection.
3. Design a staged progression from a test environment to a small production cohort.
4. Which signals indicate that an injected fault has ended but system recovery is still incomplete?
5. Turn an observed retry storm into a remediation and retest plan.

Chaos engineering is a disciplined way to test resilience assumptions under bounded failure. Begin with a measurable steady state, inject one controlled fault, keep independent abort and recovery controls, and use the evidence to reduce uncertainty. The outcome is not a pass badge; it is an owned, testable understanding of system behavior.
