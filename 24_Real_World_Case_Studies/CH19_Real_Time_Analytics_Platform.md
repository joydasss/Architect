# Real-Time Analytics Platform

Part: [24 — Real-World Architecture Case Studies](PART_OVERVIEW.md)

This case study designs a real-time analytics platform that ingests events, computes rolling results, serves dashboards and alerts, and retains history for deeper analysis. The key architecture choices are freshness, event-time correctness, state recovery, replay, and the boundary between serving and historical stores. Part 07 owns stream-processing semantics; Part 06 owns storage mechanics; Part 14 owns observability platforms.

## Define Event Contracts and Latency Goals

Each event should have a schema, producer owner, event identity, event time, ingestion time, and semantic meaning. Define expected volume, burst rate, allowed lateness, ordering scope, and freshness objective. A dashboard that updates “in real time” needs a measurable end-to-end bound and a clear response when the stream falls behind.

```mermaid
flowchart LR
    Producer[Business event producers] --> Contract[Versioned event contract]
    Contract --> Broker[Event ingestion and retention]
    Broker --> Stream[Stream processing]
    Stream --> Serving[(Low-latency serving store)]
    Serving --> Dashboard[Dashboard and alerts]
    Stream --> Historical[(Historical analytical store)]
    Contract --> Governance[Schema and ownership governance]
    Governance --> Broker
```

Separate event-time from processing-time. Producers may send late or out-of-order events due to offline devices, retries, or network delay. Define whether results update, retract, or preserve prior values when late data arrives.

## Process Windows and Late Events

Windowing groups events over time ranges. Fixed windows are simple and align to reporting periods; sliding windows overlap; session windows follow inactivity gaps. Watermarks estimate event-time progress and determine how long the system waits for late events. Larger lateness tolerance improves completeness but delays finalization and consumes state.

```mermaid
flowchart LR
    E1[Event time 10:01] --> Window[Window 10:00-10:05]
    E2[Event time 10:04] --> Window
    E3[Late event time 10:03] -->|Arrives after E2| Window
    Watermark[Watermark advances] --> Close{Window finalization policy}
    Window --> Close
    Close -->|Within lateness bound| Update[Update result and emit revision]
    Close -->|Beyond bound| Side[Send to late-data path or audit]
```

The application contract must define whether a dashboard value is provisional or final. A late event can change a previously emitted aggregate. Downstream consumers need a revision or correction signal. Do not silently mutate historical values without lineage.

## Persist State and Recover

Stream processors maintain state such as counts, balances, or per-key windows. Checkpoints capture progress and state so a worker can recover after failure. Claims of exactly once processing depend on source, processing, and sink semantics; the architecture should state the actual guarantee and how duplicates or partial commits are handled.

```mermaid
sequenceDiagram
    participant Broker
    participant Processor
    participant State as Checkpointed state
    participant Sink as Serving sink
    Broker->>Processor: Read events from offset
    Processor->>State: Update window state
    Processor->>Sink: Emit aggregate with version
    Processor->>State: Commit checkpoint and source offset
    Note over Processor,Sink: Recovery reconciles sink state with checkpoint
    Processor-->>Broker: Resume from committed position
```

Checkpoint frequency trades recovery point and overhead. A checkpoint is useful only if state, offsets, and sink writes recover coherently. Test worker loss during emission, sink outage, and checkpoint corruption before trusting a recovery objective.

## Replay and Deduplicate Safely

Replay supports backfills, bug fixes, and projection rebuilds. It can overload sources and sinks or duplicate external side effects. Use stable event IDs, versioned logic, isolated replay targets, bounded rate, and a promotion gate. Keep replay separate from live processing where possible, or define how both streams reconcile.

```mermaid
flowchart TD
    Source[Retained event log] --> Replay[Replay job with versioned logic]
    Replay --> Dedup[Deduplicate by event identity]
    Dedup --> Candidate[Build candidate projection]
    Candidate --> Validate[Compare counts and invariants]
    Validate --> Gate{Candidate valid and caught up?}
    Gate -->|Yes| Promote[Promote serving projection]
    Gate -->|No| Repair[Fix logic or source gap]
    Repair --> Replay
    Live[Live event stream] --> Current[Current projection]
    Promote --> Current
```

Replay must respect retention and privacy requirements. If upstream events have expired, identify that limitation rather than claiming complete reconstruction. Record code, schema, offsets, and result version for every replay.

## Separate Serving and Historical Boundaries

A low-latency serving store supports current dashboards and alerts; a historical store supports long-range analysis and expensive queries. Define which is authoritative for each metric, how late corrections propagate, and how retention differs. Batch and stream paths can coexist if they share event definitions and reconciliation rules.

```mermaid
flowchart LR
    Events[Governed event stream] --> Processor[Windowed stream computation]
    Processor --> Serving[(Serving store for current metrics)]
    Events --> Archive[(Historical event lake)]
    Archive --> Batch[Batch recalculation]
    Batch --> Reconcile[Compare with streaming projection]
    Serving --> Dashboard[Operational dashboard]
    Reconcile -->|Difference| Correction[Versioned correction or rebuild]
    Correction --> Serving
```

Do not let a dashboard query the event lake directly if its latency and cost contract require the serving store. Conversely, do not use a lossy aggregate as the only history when audit or recalculation requires source events. Document metric definitions and update delay.

## Worked Case: Delivery Operations Dashboard

A delivery platform computes active shipments, late deliveries, and facility backlog from status events. The dashboard needs updates within two minutes; source events include event time and facility ID. The stream processor updates rolling windows, while late carrier scans revise the metric and emit a correction. A historical store retains normalized events under the data-retention policy.

When a processor fails during sink emission, checkpoint recovery replays recent events with stable IDs. A daily batch calculation compares totals against the streaming projection. The platform exposes data freshness and correction status so operators do not treat a temporarily incomplete metric as final. Alerting distinguishes service lag from actual delivery backlog.

## Review Questions

1. What freshness and completeness contract does each dashboard metric require?
2. How are event-time and processing-time distinguished?
3. What happens to results when events arrive after a window closes?
4. How do checkpoint and sink guarantees interact during recovery?
5. How are replay, retention, and privacy handled together?

Real-time analytics is an event-time, state-recovery, and serving-contract problem. Define freshness and lateness, make checkpoints and replay observable, and reconcile stream results with historical evidence without claiming stronger guarantees than the system provides.
