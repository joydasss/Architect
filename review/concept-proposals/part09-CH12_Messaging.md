# Concept proposals: Part 09 CH12 Messaging

Source chapter: [Messaging](../../09_Cloud_Computing/CH12_Messaging.md) (in-depth rewrite).

The chapter's owned concepts already exist in `CORE_CONCEPTS.md` (provider messaging taxonomy; producer/consumer acknowledgment and retention configuration; event routing and subscription filters; retry, dead-letter, replay, and quota operations; messaging security and cross-scope access). The rewrite teaches two cross-cutting ideas that have no registry row.

| Concept | Proposed owner | Notes |
|---|---|---|
| Claim-check pattern (payload stored in versioned object storage, a small message carries bucket, key, version, checksum; object lifecycle must outlive message retention plus DLQ retention plus replay window) | [Messaging](../../09_Cloud_Computing/CH12_Messaging.md) Section 12 | Accepts the suggestion in `part09-CH11_Serverless.md`. CH12 teaches the mechanism, ordering of write-then-send, versioning, access, lifecycle, and the chunk-billing cost effect across SQS, SNS, EventBridge, Service Bus, Event Grid, and Pub/Sub. CH11 recaps it for function payload limits |
| Lease-based delivery model across providers (SQS visibility timeout, Service Bus peek-lock, Pub/Sub acknowledgment deadline) with heartbeat extension and a hard ceiling, sized from measured processing percentiles | [Messaging](../../09_Cloud_Computing/CH12_Messaging.md) Sections 3.2 to 3.5 | Could be folded into the existing "Managed broker producer/consumer, acknowledgment, and retention configuration" row instead of a new row. Generic at-least-once semantics stay with Part 07 CH17 |
