# SLO (Service Level Objective)

Part: [14 — Observability](PART_OVERVIEW.md)

A Service Level Objective (SLO) is a target for a measured aspect of service reliability over a defined period. The foundational Service Level Indicator (SLI), SLO, Service Level Agreement (SLA), availability, and error-budget vocabulary is owned by [Part 07 Non-Functional Requirements](../07_System_Design_and_Distributed_Systems/CH02_Non_Functional_Requirements.md). This chapter recaps that vocabulary and focuses on operational SLO selection, governance, and use with alerting and delivery decisions rather than re-deriving the definitions.

## From User Journey to Objective

Start with a user journey or service promise, not with whichever metric is easiest to graph. Identify the events that represent successful service, the eligible population, the measurement point, and the time window. A front-end availability target may need to reflect completed transactions rather than healthy hosts. A dependency objective should support a service owner's decision and not obscure the end-to-end user outcome.

```mermaid
flowchart LR
    Journey[Critical user journey] --> Event[Eligible request or transaction]
    Event --> Indicator[Measured reliability indicator]
    Indicator --> Target[Objective target and window]
    Target --> Budget[Allowed unreliability]
    Budget --> Policy[Alert and delivery policy]
    Policy --> Review[Owner review and adjustment]
```

Write an objective statement with an indicator, target, window, population, and owner. State exclusions explicitly, such as planned administrative traffic or client-canceled requests, and ensure exclusions do not hide real user harm. Use a separate indicator for each materially different promise rather than combining incompatible measures into one score.

## Choosing Targets and Windows

Targets should reflect user expectations, product commitments, failure cost, and the team's ability to improve reliability. Higher targets cost more engineering and operational effort and leave less budget for change. A target copied from a competitor or set to “five nines” without a user and cost rationale is not a strategy.

```mermaid
flowchart TD
    Need[User and business need] --> Evidence[Historical reliability and failure impact]
    Evidence --> Alternatives[Candidate target and window]
    Alternatives --> Cost[Engineering and opportunity cost]
    Cost --> Stakeholders[Owner, product, and operations agreement]
    Stakeholders --> Decision{Target is meaningful and measurable?}
    Decision -->|No| Alternatives
    Decision -->|Yes| Publish[Versioned objective and policy]
```

Windows can be rolling or calendar-aligned. Rolling windows provide continuously updated behavior; calendar windows simplify periodic reporting but can hide a severe short incident inside a long interval. Select a window for the decision cadence. Fast operational alerts can use shorter windows than the objective's reporting window, provided they are calibrated to its risk.

```mermaid
flowchart LR
    Requests[Eligible requests in window] --> RequestSLI[Request-based good fraction]
    Events[Eligible events in window] --> WindowSLI[Window-based success condition]
    RequestSLI --> Objective[Objective target and window]
    WindowSLI --> Objective
    Objective --> Reporting[Continuous or calendar reporting]
    Reporting --> Decision[Alert and reliability decision]
```

Request-based and window-based objectives answer different questions. A request-based ratio weights each eligible operation; a window-based objective may classify fixed intervals as good or bad. Choose the model that reflects the service promise and state how low traffic, partial windows, and missing data affect it.

```mermaid
flowchart TD
    Journey[Customer checkout journey] --> Edge[Checkout service objective]
    Edge --> Payment[Payment dependency objective]
    Edge --> Inventory[Inventory dependency objective]
    Edge --> Queue[Order processing objective]
    Payment --> OwnerA[Payment service owner]
    Inventory --> OwnerB[Inventory service owner]
    Queue --> OwnerC[Order platform owner]
    Edge --> ServiceOwner[Checkout owner remains accountable end to end]
```

An objective hierarchy helps identify dependency expectations, but dependency objectives do not replace the user-facing objective. Each lower-level objective needs an owner and a contract that supports the top-level journey.

## Governance and Ownership

Every objective needs a service owner accountable for the indicator and its data quality. Product and operations partners agree on user impact, target, and consequences. Review objectives periodically and after material service changes, but avoid changing a target merely to make a current dashboard green. Version changes with effective date, rationale, affected population, and downstream alert or error-budget policy.

```mermaid
stateDiagram-v2
    [*] --> Proposed
    Proposed --> Validated: indicator and data tested
    Validated --> Approved: stakeholders agree target and consequence
    Approved --> Active
    Active --> ReviewDue: scheduled or change-triggered review
    ReviewDue --> Active: target remains valid
    ReviewDue --> Revision: service contract changed
    Revision --> Validated
    Active --> Retired: service or promise ends
```

Avoid conflicting objectives across a service and its dependencies. A dependency target should leave enough reliability for the end-to-end objective and should not shift accountability away from the user-facing owner. Part 09 owns provider SLO products; Part 12 applies SLO signals to Kubernetes; this chapter owns provider-neutral operational use.

## Operational Use and Alerting

An objective supports decisions when its indicator is timely and trusted. Use it to inform alerting, incident severity, capacity work, and release risk. [CH13 Error Budgets](CH13_Error_Budgets.md) owns the operational policy for remaining reliability allowance; [CH10 Alerting](CH10_Alerting.md) owns generic alert lifecycle. Avoid alerting on every small SLO fluctuation; multi-window burn-rate policies can detect fast and sustained risk.

Missing or delayed data must not count as success. Monitor the SLI pipeline and define how to report periods with incomplete observations. If the measurement boundary changes, assess whether old and new data are comparable before aggregating them.

## Worked Case and Review Checklist

A checkout service adopts a request-based availability objective for eligible customer transactions and a latency objective at the user-facing edge. It excludes health checks but includes dependency timeouts and application errors. The team validates the numerator and denominator against sampled logs and request metrics, selects a rolling window aligned to incident response, and documents the cost and change policy with the target. A later API change triggers review because the definition of an eligible transaction changes.

Review user journey, indicator, eligible event population, target rationale, window, exclusions, owner, data quality, alert policy, downstream dependency budget, versioning, and review trigger. Confirm that changes to instrumentation or service behavior cannot silently redefine success.

## Questions and Summary

1. Recap the relationship between SLI, SLO, and SLA; link each to its foundational owner.
2. Write an objective for a user journey and specify eligible and excluded events.
3. Compare rolling and calendar windows for incident response and reporting.
4. How should an SLO change be versioned when the service's event population changes?
5. Which operational decisions should the objective inform, and who owns each one?

An SLO turns a user-relevant reliability promise into a measurable target with an owner, window, and consequence. Part 07 owns the foundational vocabulary; Part 14 makes objectives operational through validated indicators, alerting, review, and error-budget policy. A target without trustworthy measurement and a response contract is only a number.
