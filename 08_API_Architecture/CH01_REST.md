# Chapter: REST

Part: [08 — API Architecture](PART_OVERVIEW.md) · Status: Edited (overlap with HTTP resolved)

## 1. Introduction

REST (REpresentational State Transfer) is an architectural style for
networked applications, introduced by Roy Fielding in his 2000 doctoral
dissertation. It is the dominant style for public and internal HTTP APIs
today. This chapter covers REST's constraints, maturity model, and design
practices, and owns REST-specific concepts (resource modeling, HATEOAS, and
the Richardson Maturity Model).

## 2. Historical Evolution

REST emerged alongside HTTP/1.1 as a formalization of the architectural
properties that made the web itself scale — Fielding's dissertation named and
justified constraints (statelessness, uniform interface, cacheability) that
HTTP already exhibited informally. Over the 2000s-2010s, REST became the
default style for public APIs, later joined (not replaced) by GraphQL and
gRPC for specific use cases.

## 3. Why It Exists

Before REST was named, API designers built ad hoc RPC (Remote Procedure Call)
style HTTP APIs with verbs in the URL (`/getUser`, `/deleteOrder`) and
inconsistent status-code usage. REST gave teams a shared vocabulary and a set
of constraints that, when followed, produce APIs that scale, cache well, and
evolve without breaking clients.

## 4. Core Concepts

- **Resources**: nouns, not verbs — `/orders/42`, not `/getOrder?id=42`.
- **HTTP methods as the uniform interface**. A REST API is built entirely on
  top of HTTP's existing request/response model rather than inventing its
  own — see [HTTP § Core Concepts](../05_Networking_and_OS/CH01_HTTP.md#4-core-concepts)
  for the full method semantics (safety, idempotency) and status-code
  taxonomy. REST's contribution is mapping CRUD (Create, Read, Update,
  Delete) operations onto that existing vocabulary consistently: `POST` to
  create under a collection, `GET` to read, `PUT`/`PATCH` to update, `DELETE`
  to remove — with `201 Created` + `Location` on successful creation and
  `204 No Content` on a successful delete.
- **Caching via HTTP headers**. REST resources reuse HTTP's own caching
  mechanism unchanged — see
  [HTTP § Core Concepts](../05_Networking_and_OS/CH01_HTTP.md#4-core-concepts)
  for `Cache-Control`/`ETag`/`Last-Modified` semantics. What's REST-specific
  is that a resource's `ETag` is typically derived from its version or
  content hash, letting a conditional `GET` return a cheap `304 Not Modified`
  and a conditional `PUT` (using `If-Match`) implement optimistic concurrency.
- **Resource modeling**: collections (`/orders`) versus single resources
  (`/orders/42`); nested relationships (`/orders/42/items`); avoiding
  resource sprawl by mapping to the domain's actual aggregates, not every
  possible query shape.
- **HATEOAS (Hypermedia As The Engine Of Application State)**: responses
  include links describing what the client can do next (e.g. a `cancel`
  link on an order resource that's still cancellable), so clients don't need
  to hard-code URL construction rules.
- **Richardson Maturity Model**: Level 0 (single URI, single method — RPC over
  HTTP), Level 1 (multiple resource URIs, still one method), Level 2
  (proper use of HTTP methods and status codes — where most production REST
  APIs sit), Level 3 (HATEOAS).

## 5. Internal Working

A REST client and server exchange plain HTTP messages; there is no
REST-specific wire protocol beyond conventions applied on top of HTTP. The
example below applies HTTP's own conditional-request/caching mechanism (see
[HTTP § Internal Working](../05_Networking_and_OS/CH01_HTTP.md#5-internal-working))
to a REST resource — a typical request/response for fetching an order:

```text
GET /orders/42 HTTP/1.1
Host: api.example.com
Accept: application/json
If-None-Match: "42-v3"

HTTP/1.1 304 Not Modified
```

Because the client's cached copy's `ETag` matched, the server can skip
serializing and sending the full body, saving bandwidth and CPU on both ends.

## 6. Design Principles

- **Client-server separation**: clients and servers evolve independently as
  long as the resource contract holds.
- **Statelessness**: no server-side session tied to a specific server
  instance; any instance behind a load balancer can serve any request.
- **Uniform interface**: consistent use of methods, status codes, and media
  types across all resources in the API.
- **Layered system**: gateways, caches, and proxies can sit transparently
  between client and origin.

## 7. Architecture Patterns

- **API Gateway front door**: centralizes authentication, rate limiting, and
  routing for many REST services.
- **Backend-for-Frontend (BFF)**: a REST facade tailored to one client type
  (mobile vs web) aggregating multiple internal services.
- **Versioning via URI or header**: `/v2/orders/42` vs `Accept:
  application/vnd.example.v2+json`.

## 8. Production Architecture

```text
Client --HTTPS--> API Gateway (auth, rate limit) --> REST Service --> Database
```

## 9. Implementation

A REST endpoint implementation must: parse the path to extract resource
identifiers, validate the request body against the resource schema, set the
correct status code for the outcome, and set `Location` on `201 Created`
responses.

## 10. Complete Code Examples

- Python: [code/python/rest-chapter/orders_api.py](../code/python/rest-chapter/orders_api.py)
- Node.js: [code/node/rest-chapter/orders_api.js](../code/node/rest-chapter/orders_api.js)

## 11. Performance

Conditional `GET` requests using `ETag`/`If-None-Match` avoid re-transferring
unchanged resources. Pagination (`?page=`/`?cursor=`) prevents unbounded
collection responses. Field selection (`?fields=id,name`) reduces payload
size for bandwidth-constrained clients.

## 12. Scalability

Because REST inherits HTTP's statelessness, REST services scale horizontally
behind a load balancer without sticky sessions, the same way any HTTP service
does.

## 13. Security

Use `401` for missing/invalid credentials and `403` for authorization
failures — do not conflate them, since clients behave differently in
response to each. Validate all path/query parameters server-side regardless
of client-side validation.

## 14. Observability

Emit method, path template (not raw path with IDs, to avoid metric
cardinality explosion), and status code as labeled metrics per request.

## 15. Failure Scenarios

A `409 Conflict` on `PUT` typically indicates an optimistic-concurrency
version mismatch — the client should re-fetch the resource and retry with
the current `ETag`.

## 16. Testing

Contract tests per resource: verify `201`+`Location` on create, `200` on
successful `GET`, `404` on missing resource, `409` on version conflict.

## 17. Common Mistakes

Using `POST` for everything instead of the correct verb, and returning `200`
for both success and failure with an `{"error": ...}` body instead of the
right status code.

## 18. Best Practices

Model resources around the domain's aggregates, keep URIs noun-based and
shallow, and always pair a mutation's status code with the correct headers
(`Location`, `ETag`).

## 19. Anti-Patterns

"RPC-in-REST-clothing" APIs (Richardson Level 0/1) that expose a single verb
per action via `POST` regardless of the actual HTTP semantics.

## 20. Trade-off Analysis

| Decision | Benefit | Cost |
|---|---|---|
| Richardson Level 2 vs Level 3 (HATEOAS) | Simpler clients, less link-following overhead | Clients must hard-code URL construction |
| URI versioning vs header versioning | Simple, cache-friendly | URI churn across versions |

## 21. Comparison Table

| Style | Coupling | Caching | Best fit |
|---|---|---|---|
| REST | Low | Native HTTP caching | Public APIs, CRUD-shaped resources |
| GraphQL | Medium | Requires custom caching | Flexible client-driven queries |
| gRPC | Higher (schema/codegen) | Not HTTP-cache-native | Low-latency internal service-to-service calls |

## 22. Real-World Case Study

An order-management REST API using `ETag`-based conditional `GET` and
optimistic-concurrency `PUT` (rejecting stale updates with `409`) avoids both
lost-update bugs and unnecessary payload transfer for polling clients.

## 23. Interview Questions

1. What distinguishes Richardson Maturity Model Level 2 from Level 3?
2. Why should `DELETE` be idempotent, and what does that mean in practice?
3. When would you choose header-based versioning over URI-based versioning?

## 24. Hands-on Exercises

Build a small orders REST API using the code samples in Section 10, and
verify conditional `GET` returns `304` on a repeated request with the correct
`If-None-Match` header.

## 25. Design Exercises

Design the resource model (URIs, methods, status codes) for a library
lending system (books, members, loans). Evaluation criteria: correct verb
usage, sensible resource nesting, and conflict handling for double-booking a
copy.

## 26. Architecture Review Questions

- Are status codes used specifically, not just `200`/`400`/`500`?
- Is every `PUT`/`DELETE` actually idempotent at the server?
- Is caching (`ETag`/`Cache-Control`) used where the resource supports it?

## 27. Summary

REST is a set of architectural constraints layered on top of HTTP's existing
request/response model, method semantics, and status codes. Getting REST
right is largely about disciplined use of HTTP itself, plus REST-specific
resource-modeling and maturity-model judgment calls.

**Further reading**: [HTTP](../05_Networking_and_OS/CH01_HTTP.md) ·
[API Gateway](PART_OVERVIEW.md) · [GraphQL](PART_OVERVIEW.md)
