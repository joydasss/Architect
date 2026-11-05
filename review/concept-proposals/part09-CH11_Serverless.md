# Concept proposals: Part 09 CH11 Serverless

Source chapter: [Serverless](../../09_Cloud_Computing/CH11_Serverless.md) (in-depth rewrite).

The chapter's owned concepts already exist in `CORE_CONCEPTS.md` (invocation lifecycle, cold start and warm capacity, concurrency as downstream control, retries and partial batches, function versus workflow versus serverless container). The rewrite teaches three cross-cutting ideas that have no registry row. It applies them only to functions, so the merge step should decide final ownership.

| Concept | Proposed owner | Notes |
|---|---|---|
| Invocation model taxonomy: synchronous request/response, asynchronous invocation through a provider-managed queue, and poll-based event source mapping, with retry ownership per model | [Serverless](../../09_Cloud_Computing/CH11_Serverless.md) | Extends the existing "Serverless function invocation lifecycle" row. Says who acknowledges, who retries, and where failed events land for each model. Messaging (CH12) recaps it for broker-to-function integrations |
| Claim-check pattern (large payload stored externally, reference passed in the event) | Suggest [Messaging](../../09_Cloud_Computing/CH12_Messaging.md) or a Part 07 messaging owner | CH11 applies it to function payload limits and keeping payloads out of logs and DLQs; it recaps the pattern briefly rather than owning it |
| Timeout alignment down a call chain (each layer's timeout shorter than its caller's, so errors propagate instead of leaving orphaned work) | Suggest Part 07 [Non-Functional Requirements](../../07_System_Design_and_Distributed_Systems/CH02_Non_Functional_Requirements.md) or Part 08 [gRPC](../../08_API_Architecture/CH03_gRPC.md) deadline ownership | CH11 Section 7.4 gives a worked function example (client, gateway, function, database, visibility timeout) |
