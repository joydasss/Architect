# Food Delivery Platform

Part: [24 — Real-World Architecture Case Studies](PART_OVERVIEW.md)

This case study coordinates customer ordering, merchant preparation, courier dispatch, delivery tracking, payment, and settlement. The architecture must handle independent actors, changing preparation estimates, perishable timing, cancellation, and partial failure. Assumptions: the service operates within defined delivery regions and supports card or wallet payment through an external provider.

## Frame Domain and Quality Goals

The customer expects accurate menu availability, clear pricing, and timely status. Merchants need control over acceptance and preparation; couriers need fair assignments and safe routing; operations need a way to resolve stuck orders. Measures include checkout completion, merchant acceptance time, pickup delay, delivery estimate error, cancellation rate, payment reconciliation, and support contacts.

```mermaid
flowchart LR
    Customer[Customer app] --> Order[Order service]
    Order --> Merchant[Merchant integration]
    Order --> Payment[Payment authorization]
    Merchant --> Prep[Preparation state]
    Dispatch[Courier dispatch] --> Courier[Courier app]
    Order --> Dispatch
    Courier --> Tracking[Location and delivery status]
    Tracking --> Customer
    Order --> Settlement[Merchant and courier settlement]
```

Keep order state authoritative and represent external participant status as versioned inputs. A merchant acceptance is not the same as courier assignment; a payment authorization is not settlement. The workflow needs explicit semantics for each transition.

## Model the Order Lifecycle

The order crosses customer, merchant, payment, and delivery states. Each transition needs an owner, guard, timeout, and compensation or escalation. Cancellation behavior depends on the stage: before merchant acceptance it may be simple; after preparation or pickup it may incur a fee or require a support decision.

```mermaid
stateDiagram-v2
    [*] --> Cart
    Cart --> Submitted: Customer confirms
    Submitted --> Authorized: Payment authorized
    Submitted --> Rejected: Payment or validation fails
    Authorized --> MerchantPending: Send merchant request
    MerchantPending --> Preparing: Merchant accepts
    MerchantPending --> Canceled: Merchant declines or timeout
    Preparing --> Ready: Merchant marks ready
    Ready --> PickedUp: Courier confirms pickup
    PickedUp --> Delivered: Customer receives order
    Authorized --> Canceled: Cancellation policy permits
    Preparing --> SupportReview: Cancellation or delay exception
    Delivered --> [*]
    Rejected --> [*]
    Canceled --> [*]
```

Do not allow stale callbacks to move an order backward or revive a canceled order. Use transition versions and idempotent event handling. The customer-facing status should reflect the authoritative state and explain when an exception needs support.

## Coordinate Merchant, Courier, and Customer

Merchant preparation time and courier arrival influence pickup wait and food quality. Dispatch can assign a courier after merchant acceptance, just before estimated readiness, or in stages based on distance and uncertainty. Each strategy balances courier idle time, merchant wait, delivery time, and reassignment risk.

```mermaid
sequenceDiagram
    actor Customer
    participant Order as Order service
    participant Merchant
    participant Dispatch
    participant Courier
    Customer->>Order: Place order
    Order->>Merchant: Request acceptance and prep estimate
    Merchant-->>Order: Accept with readiness estimate
    Order->>Dispatch: Request courier near readiness window
    Dispatch->>Courier: Offer delivery with expiry
    Courier-->>Dispatch: Accept
    Dispatch-->>Order: Courier assigned
    Order-->>Customer: Confirm order and current estimate
    Merchant-->>Order: Mark ready
    Courier->>Merchant: Confirm pickup
    Courier-->>Order: Delivery completed
    Order-->>Customer: Final status and receipt
```

Estimates should update from merchant signals and courier progress. Avoid sending frequent contradictory updates; expose confidence or ranges when readiness is uncertain. If no courier accepts, the order service needs a bounded fallback such as widening the eligible area, delaying, or offering cancellation.

## Batch Dispatch With Explicit Constraints

Batching can reduce courier travel and improve utilization, but it can increase delivery time and quality risk. Candidate orders should be grouped only when pickup and drop-off constraints, dietary separation, temperature, and delivery promises remain valid. The dispatch policy should be measurable and explainable to operations.

```mermaid
flowchart TD
    ReadyOrders[Orders ready or near readiness] --> Candidate[Find nearby compatible orders]
    Candidate --> Constraints[Check pickup, route, timing, and handling constraints]
    Constraints --> Value{Efficiency gain without violating promise?}
    Value -->|Yes| Batch[Create courier batch]
    Value -->|No| Single[Dispatch individually]
    Batch --> Courier[Assign courier and sequence stops]
    Single --> Courier
    Courier --> Monitor[Track arrival, wait, and delivery estimate]
    Monitor -->|Promise at risk| Replan[Unbatch, reassign, or notify support]
```

Batching decisions should account for uncertainty in merchant preparation and traffic. A route-efficient batch can still be poor if the first meal waits too long. Track incremental delivery delay and cancellation by batch size, and cap the number of stops based on evidence.

## Handle Events, Cancellation, and Compensation

Use a status-event timeline to correlate changes across participants. Events can arrive late, out of order, or more than once. Reconcile them against the order version and actor identity. Cancellation or failure may require releasing payment authorization, compensating the merchant, reassigning a courier, or issuing a refund; those effects are not one atomic transaction.

```mermaid
flowchart LR
    Cancel[Cancellation request or failure] --> Stage{Current order stage?}
    Stage -->|Before merchant acceptance| Stop[Stop merchant and dispatch requests]
    Stage -->|Preparing| Policy[Apply fee and merchant compensation policy]
    Stage -->|Courier assigned| Release[Cancel or reassign courier]
    Stage -->|Picked up| Support[Support-led resolution]
    Stop --> Payment[Void authorization or refund]
    Policy --> Payment
    Release --> Payment
    Support --> Payment
    Payment --> Reconcile[Reconcile order, payment, and settlement state]
    Reconcile --> Close[Notify customer and close workflow]
```

Define which service owns cancellation authority and what happens when payment status is unknown. Every compensation should be idempotent and linked to the original order. A human support action needs a reason code and audit trail.

## Worked Case: Merchant Delay During Dinner Peak

A restaurant accepts an order with an eight-minute preparation estimate but later reports a delay. Dispatch has already assigned a courier. The system updates the delivery estimate, informs the customer, and evaluates whether the courier can be resequenced without violating another order's promise. If the delay exceeds a threshold, the workflow offers cancellation under policy and reconciles the payment authorization.

Operations monitors merchant delay distribution, courier wait, batch effects, cancellation, and compensation. The platform does not hide merchant uncertainty behind a single precise arrival time. A repeated delay pattern updates the merchant's preparation model and may change dispatch timing for that location.

## Review Questions

1. Which service owns authoritative order state and each transition?
2. How do merchant readiness and courier assignment affect one another?
3. What constraints govern batching and route resequencing?
4. How are late, duplicated, or conflicting status events handled?
5. Which compensations and payment reconciliations follow cancellation?

Food delivery architecture coordinates multiple autonomous actors around one customer promise. Make lifecycle transitions explicit, use preparation and courier estimates as uncertain inputs, constrain batching, and design cancellation and settlement as recoverable workflows.
