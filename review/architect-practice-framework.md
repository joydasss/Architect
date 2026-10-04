# Architect Practice Framework

## Purpose

The Architect Practice Framework turns a vague business problem into a
defensible architecture decision. It is not a chapter checklist or a list of
technology names. It is a repeatable way to practise architecture as a
professional discipline.

```text
Business problem
      |
      v
Requirements -> Constraints -> Options -> Trade-offs -> Decision
                                                        |
                                                        v
Implementation slice -> Failure exercise -> Security review
                                                        |
                                                        v
Cost and ROI -> Observability -> ADR -> Hostile review -> Reflection
```

The sequence prevents premature technology selection. Instead of beginning
with "Should we use Kafka?" or "Should we use microservices?", the architect
first establishes the business outcome, constraints, alternatives, risks, and
evidence required to justify a decision.

## 1. Business Problem

Start with the business pain or opportunity, not the proposed technology.

Example:

> A retailer's customer-support team cannot reliably answer where an order is
> or whether it can be cancelled. Agents search three systems manually, taking
> an average of 12 minutes per case.

Define the outcome:

- Reduce average resolution time from 12 minutes to less than 3 minutes.
- Resolve 80 percent of status requests without escalation.
- Preserve order and payment correctness.

This gives the architecture a purpose. Without it, a technically impressive
design can still solve the wrong problem.

## 2. Requirements

Separate functional requirements from non-functional requirements.

Functional requirements:

- Retrieve order status.
- Show payment and shipping state.
- Explain why cancellation is unavailable.
- Request cancellation when the order is eligible.
- Support both customers and support agents.

Non-functional requirements:

- Support 2,000 requests per second at peak.
- Keep status-read p95 latency below 300 milliseconds.
- Make cancellation requests idempotent.
- Audit every cancellation attempt.
- Protect personally identifiable information (PII).

Requirements convert the business objective into observable system behaviour.

## 3. Constraints

Constraints are the real boundaries within which the architecture must work:

- The order database is owned by another team.
- Payment and shipping systems have different availability guarantees.
- Existing clients depend on `/v1/orders`.
- The first release must be delivered in six weeks.
- The organisation cannot operate another large data platform.

Architecture is always a decision under constraints. A design that ignores
delivery time, team capability, operational burden, or existing ownership is
not a realistic architecture.

## 4. Options

List the serious alternatives rather than jumping to the first solution.

| Option | Description |
|---|---|
| A | The API directly calls order, payment, and shipping systems. |
| B | The API serves reads from an event-driven status read model. |
| C | A new service replaces the existing order API. |

The goal is not to invent ten possibilities. The goal is to make the meaningful
choices visible.

## 5. Trade-offs

Option A is quick to start and returns current data, but it inherits the
latency and failure modes of every dependency.

Option B provides fast, resilient reads and independent scaling, but introduces
eventual consistency, event replay, schema evolution, and reconciliation work.

Option C offers a clean long-term boundary, but has the highest migration,
delivery, and organisational risk.

A strong architecture explanation says what each option improves and what it
makes worse. It does not merely label one option as "better."

## 6. Decision

Choose the option explicitly:

> Use an event-driven read model for order-status queries, while keeping
> cancellation as a controlled workflow that validates against authoritative
> order state.

The decision is deliberately hybrid. Eventual consistency is acceptable for a
status display when freshness is visible. It is not sufficient for a financial
or irreversible mutation.

```text
Customer or Support Agent
          |
          v
       Order API
        /     \
       v       v
  Status Read  Cancellation Workflow
     Model              |
       ^                v
       |          Authoritative Order Service
       |
Order, Payment, and Shipping Events
```

## 7. Implementation Slice

Prove the architecture with one vertical slice instead of building the entire
platform:

1. Consume order, payment, and shipping events.
2. Populate a query-optimised order-status model.
3. Implement `GET /v1/orders/{orderId}/status`.
4. Add customer and support-agent authorization.
5. Add contract tests and freshness metadata.
6. Add basic metrics and distributed tracing.

Do not implement recommendations, a chatbot, refunds, analytics, and every
possible workflow in the first slice. The slice should answer whether the
architecture can satisfy the most important requirement.

Example response:

```json
{
  "orderId": "ORD-4821",
  "status": "IN_TRANSIT",
  "lastUpdatedAt": "2026-09-26T10:15:00Z",
  "dataFreshnessSeconds": 3
}
```

## 8. Failure Exercise

Break the design deliberately and define the expected behaviour.

| Failure | Expected behaviour |
|---|---|
| Shipping events are delayed | Show the last known state and freshness timestamp. |
| An event is delivered twice | Apply it once using an idempotency key. |
| The read model is unavailable | Return a controlled error; do not fan out synchronously to every dependency. |
| The order service is unavailable during cancellation | Return `PENDING` or `UNKNOWN`, never a false success. |
| An event has an invalid schema | Send it to a dead-letter queue and alert its owner. |

The key question is not merely whether the request fails. It is whether the
business can determine what happened and recover safely.

## 9. Security Review

Identify trust boundaries and abuse cases:

```text
Customer Browser
       |
       v
API Gateway
       |
       v
Order API ----> Status Read Model
       |
       +-------> Order Service
       |
       +-------> Audit Store
```

Controls include:

- Verify that the authenticated customer owns the requested order.
- Use role-based access control (RBAC) for support agents.
- Apply attribute-based access control (ABAC) for region and business-unit restrictions.
- Never trust an `orderId` supplied by the client without an ownership check.
- Encrypt data in transit and at rest.
- Redact addresses and payment data from logs.
- Rate-limit order lookup to prevent enumeration.
- Audit every cancellation attempt.

Artificial intelligence may summarise an order timeline for an agent, but it
must not independently authorize a cancellation or refund without deterministic
policy enforcement and appropriate human approval.

## 10. Cost and Return on Investment

Estimate the cost of the proposed architecture:

| Component | Monthly estimate |
|---|---:|
| Read-model database | $1,200 |
| Event processing | $500 |
| API compute | $800 |
| Observability | $400 |
| Audit storage | $100 |
| **Total** | **$3,000** |

Suppose the current support workload is 100,000 contacts per month, with an
average cost of $4.80 per contact. The current cost is approximately $480,000
per month. If the new system prevents half of those contacts, the estimated
avoided cost is $240,000 per month.

The design is justified by the expected business outcome, not because an
event-driven system is fashionable. The estimate should also include delivery
cost, support effort, incident cost, and the cost of operating at ten times the
current scale.

## 11. Observability

Define how the team will know whether the system is healthy:

- Request rate, errors, and duration.
- p50, p95, and p99 latency.
- Read-model freshness.
- Event-consumer lag.
- Duplicate-event count.
- Dead-letter queue depth.
- Cancellation outcomes.
- Authorization failures.
- Reconciliation backlog.

Example Service Level Objective (SLO):

> 99.9 percent of valid status requests complete successfully within 300
> milliseconds, excluding explicitly declared dependency incidents.

Observability is part of the architecture because an unobservable system is
not reliably operable.

## 12. Architecture Decision Record

```markdown
# ADR-001: Use an Event-Driven Order Status Read Model

## Status

Accepted

## Context

The status API aggregates data owned by order, payment, and shipping systems.
Direct synchronous calls create high latency and expose users to dependency
failures.

## Options Considered

1. Direct synchronous aggregation
2. Event-driven read model
3. Replacement order service

## Decision

Use an event-driven read model for status queries. Keep cancellation as an
authoritative workflow.

## Rationale

This meets the latency and availability goals within the six-week constraint
while preserving authoritative mutation behaviour.

## Consequences

Positive: low-latency reads, independent scaling, and improved resilience.

Negative: eventual consistency, event replay, and reconciliation complexity.

## Risks

The read model can be temporarily stale. Responses therefore include
freshness metadata, and cancellation never relies solely on the read model.
```

An Architecture Decision Record (ADR) preserves the reasoning behind the
choice. It prevents future teams from changing the design without knowing
which trade-offs were deliberately accepted.

## 13. Hostile Architecture Review

Review the design as a sceptical Principal Architect, Site Reliability
Engineer (SRE), security architect, Chief Financial Officer (CFO), and Chief
Technology Officer (CTO):

- What happens when an old event arrives after a newer event?
- How is the read model rebuilt?
- Can a customer read another customer's order by changing the identifier?
- What happens if cancellation succeeds but the response times out?
- How is "shipping event missing" distinguished from "not shipped"?
- What is the cost at ten times the current traffic?
- Why is the read model not the source of truth?
- Who owns reconciliation?
- What evidence proves the SLO?
- What prevents an AI assistant from using the cancellation API without authorization?

The design is incomplete until these questions have explicit answers.

## 14. Reflection

After the design or implementation slice, record what changed in your thinking:

```markdown
## Reflection

Initial assumption:
Direct aggregation would be simpler.

What proved wrong:
Payment and shipping latency made the p95 target impossible.

Important decision:
Separate read optimisation from authoritative mutations.

Failure discovered:
Duplicate shipping events caused state transitions to be applied twice.

What changed:
Added event identifiers and per-order version checks.

New principle:
Eventual consistency is acceptable only when freshness is visible and
business-critical mutations use authoritative state.

Next experiment:
Simulate a delayed cancellation response and validate reconciliation.
```

Reflection turns one exercise into lasting architectural judgement. It records
which assumptions failed, which decision changed, and what should be tested
next.

## How to Apply the Framework

Every handbook chapter or case study can use the same questions:

1. What business problem is this architecture solving?
2. What are the functional and non-functional requirements?
3. What constraints shape the decision?
4. What are the serious alternatives?
5. What does each alternative optimise and sacrifice?
6. Which option wins, and why?
7. What is the smallest implementation slice that can prove it?
8. What happens during partial failure?
9. What are the security boundaries and abuse cases?
10. What does the solution cost, and what value does it create?
11. How will operators know whether it works?
12. Which ADR records the decision?
13. What would a hostile reviewer challenge?
14. What did the exercise teach, and what should happen next?

The central question is not:

> Which technology should we use?

It is:

> Given this problem, these constraints, and these trade-offs, what decision
> is most defensible, what does it cost, what breaks, and how do we prove it?