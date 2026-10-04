# Event, Queue, and Messaging Architecture Concepts

Source: `10_Cloud_Architecture/CH08_Event_Queue_and_Messaging_Architectures_in_Cloud.md`

## Proposed concepts

| Concept | Proposed ownership | Boundary and overlap notes |
|---|---|---|
| Cloud workload messaging composition across queues, topics, event buses, streams, and workflows | CH08 Event, Queue, and Messaging Architectures in Cloud | Workload-level service selection, consumer isolation, retention, replay, and cross-scope topology; Part 09 CH12 owns provider mechanics and Part 07 owns generic messaging semantics. |

## Recap-only concepts

- Delivery guarantees, ordering, idempotency, consumer offsets, and event processing: Part 07.
- Provider broker products, retry configuration, quotas, and access policies: Part 09 CH12.
- Application component boundaries: Part 10 CH07.
