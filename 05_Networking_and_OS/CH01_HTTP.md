# Chapter: HTTP

Part: [05 — Networking and Operating Systems](PART_OVERVIEW.md) · Status: Reviewed (no changes required)

## 1. Introduction

HTTP (HyperText Transfer Protocol) is the application-layer protocol that
almost every distributed system a Solution Architect designs ultimately rides
on top of — REST APIs, GraphQL, gRPC-Web, browser traffic, service mesh
sidecars, and CDN (Content Delivery Network) edge caches all speak some
version of HTTP. This chapter is the *owning* chapter for HTTP's core
transport-level vocabulary (methods, status codes, caching headers, and the
TLS (Transport Layer Security) handshake as it applies to HTTPS) — other
chapters in this handbook (starting with [REST](../08_API_Architecture/CH01_REST.md))
must recap and link here rather than re-explaining these concepts, per the
Concept Ownership Rule in [STYLE_GUIDE.md](../STYLE_GUIDE.md).

## 2. Historical Evolution

- **HTTP/0.9 (1991)** — a one-line request, no headers, no status codes;
  the response was raw HTML, connection closed immediately after.
- **HTTP/1.0 (1996)** — introduced headers, status codes, and content types,
  but opened a new TCP (Transmission Control Protocol) connection per request.
- **HTTP/1.1 (1997)** — added persistent connections (`Connection: keep-alive`),
  chunked transfer encoding, host-based virtual hosting (`Host` header), and
  pipelining (rarely used in practice due to head-of-line blocking).
- **HTTP/2 (2015)** — binary framing, multiplexed streams over a single TCP
  connection, header compression (HPACK), and server push (since deprecated
  in most browsers).
- **HTTP/3 (2022)** — replaces TCP with QUIC (built on UDP), eliminating
  transport-level head-of-line blocking and speeding up connection
  establishment by folding the transport and TLS handshakes together.

## 3. Why It Exists

Before HTTP, every application-to-application protocol invented its own
framing, addressing, and content-negotiation scheme. HTTP standardized a
request/response model with a URI (Uniform Resource Identifier) addressing
scheme, a small fixed vocabulary of methods, and extensible headers — letting
browsers, proxies, caches, and servers built by different vendors interoperate
without bespoke integration work.

## 4. Core Concepts

- **Request line**: method, path, HTTP version (e.g. `GET /orders/42 HTTP/1.1`).
- **Methods**: `GET` (safe, idempotent, cacheable), `HEAD` (like GET, no body),
  `POST` (not idempotent — creates or triggers a side effect), `PUT`
  (idempotent — full replace), `PATCH` (not guaranteed idempotent — partial
  update), `DELETE` (idempotent), `OPTIONS` (capability discovery, used for
  CORS preflight).
- **Status codes**: grouped by leading digit —
  - `1xx` Informational (e.g. `100 Continue`)
  - `2xx` Success (`200 OK`, `201 Created`, `204 No Content`)
  - `3xx` Redirection (`301 Moved Permanently`, `304 Not Modified`)
  - `4xx` Client Error (`400 Bad Request`, `401 Unauthorized`, `403 Forbidden`,
    `404 Not Found`, `409 Conflict`, `429 Too Many Requests`)
  - `5xx` Server Error (`500 Internal Server Error`, `502 Bad Gateway`,
    `503 Service Unavailable`, `504 Gateway Timeout`)
- **Headers**: request headers (`Host`, `Accept`, `Authorization`), response
  headers (`Content-Type`, `Content-Length`, `Set-Cookie`), and caching
  headers (`Cache-Control`, `ETag`, `Last-Modified`, `Expires`).
- **Idempotency and safety**: safe methods must not change server state;
  idempotent methods may be retried freely by clients/proxies without
  changing the outcome beyond the first successful call — this distinction
  drives retry logic throughout distributed systems.

## 5. Internal Working

See the request/response sequence diagram:
[diagrams/sequence/http-request-response-flow.md](../diagrams/sequence/http-request-response-flow.md).

For HTTPS, the transport is secured before any HTTP bytes are exchanged. The
TLS handshake (summarized here; owned by this chapter) works as follows for
TLS 1.3:

1. Client sends `ClientHello` (supported cipher suites, a key share, SNI
   (Server Name Indication) hostname).
2. Server responds with `ServerHello` (chosen cipher, its key share), its
   certificate, and a `Finished` message — all encrypted as soon as the key
   share allows, which is why TLS 1.3 needs only one round trip versus two
   for TLS 1.2.
3. Client verifies the certificate chain against a trusted CA (Certificate
   Authority), derives the session keys, and sends its own `Finished` message.
4. Both sides now exchange application data (the actual HTTP request/response)
   under authenticated encryption.

See the ASCII handshake diagram: [diagrams/network/tls-handshake.md](../diagrams/network/tls-handshake.md).

HTTP/2 multiplexes many logical streams over one TCP connection using binary
frames (`HEADERS`, `DATA`, `SETTINGS`, `WINDOW_UPDATE`), each tagged with a
stream ID, so the receiver can reassemble concurrent requests without
head-of-line blocking at the HTTP layer (TCP-layer head-of-line blocking can
still occur on packet loss, which HTTP/3 over QUIC addresses).

## 6. Design Principles

- **Statelessness**: each request carries all the context the server needs
  (or a token referencing server-side state); this is what lets any server
  behind a load balancer handle any request.
- **Uniform interface**: a small, fixed vocabulary of methods and status codes
  that every HTTP-aware intermediary (proxy, cache, gateway) can reason about
  without understanding the application's business logic.
- **Layered system**: a client cannot generally tell whether it's talking
  directly to the origin server or through a chain of proxies/CDNs — this
  enables caching and load balancing to be inserted transparently.

## 7. Architecture Patterns

- **Reverse proxy termination**: TLS terminates at a reverse proxy/load
  balancer, which forwards plain HTTP to backend instances over a private
  network — reduces certificate management surface and CPU cost on app
  servers.
- **Edge caching**: `Cache-Control` and `ETag` headers let a CDN serve
  repeated `GET` requests without hitting the origin.
- **API Gateway as HTTP front door**: a single HTTP entry point that handles
  authentication, rate limiting, and routing before requests reach services
  speaking REST, gRPC, or GraphQL internally.

## 8. Production Architecture

```text
Client --HTTPS--> CDN edge (cache) --HTTPS--> Load Balancer (TLS terminate)
                                                     |
                                            HTTP (internal network)
                                                     v
                                          Reverse Proxy / API Gateway
                                                     |
                                     -----------------------------
                                     |             |             |
                                 Service A     Service B     Service C
```

Each hop can add its own headers (`X-Forwarded-For`, `X-Request-Id`) for
traceability — see [Observability](../12_Observability/PART_OVERVIEW.md) for
how these threads through distributed tracing (owned there).

## 9. Implementation

A minimal server must: parse the request line and headers, dispatch to a
handler by method + path, set `Content-Length` (or use chunked encoding), and
close or keep the connection alive per `Connection` semantics. See the code
samples in Section 10.

## 10. Complete Code Examples

- Python: [code/python/http-chapter/simple_http_client.py](../code/python/http-chapter/simple_http_client.py)
- Node.js: [code/node/http-chapter/simple_http_server.js](../code/node/http-chapter/simple_http_server.js)
- Java: [code/java/http-chapter/SimpleHttpClient.java](../code/java/http-chapter/SimpleHttpClient.java)

## 11. Performance

- Persistent connections (HTTP/1.1 keep-alive) avoid a new TCP + TLS handshake
  per request — the single biggest early win over HTTP/1.0.
- HTTP/2 multiplexing removes the need for the "6 connections per host"
  workaround browsers used under HTTP/1.1.
- HPACK header compression matters most for request-heavy, small-payload
  APIs (e.g. mobile apps polling frequently).
- HTTP/3's 0-RTT/1-RTT connection setup materially reduces latency on
  high-latency/lossy networks (mobile) versus TCP+TLS.

## 12. Scalability

Stateless HTTP requests scale horizontally behind a load balancer trivially;
the scaling challenge moves to whatever holds state (databases, caches,
sessions) — see [System Design and Distributed Systems](../07_System_Design_and_Distributed_Systems/PART_OVERVIEW.md).
Connection limits (file descriptors, ephemeral ports on the load balancer) are
the usual first HTTP-layer scaling bottleneck in production.

## 13. Security

- Always terminate HTTPS, never plain HTTP, for anything crossing an
  untrusted network.
- Validate the `Host` header to prevent host-header injection attacks.
- Use `HttpOnly` and `Secure` flags on cookies; set `SameSite` to mitigate
  CSRF (Cross-Site Request Forgery).
- Rate-limit and validate all `Content-Length`/chunked bodies to avoid
  request-smuggling and resource-exhaustion attacks.
- See [Security](../13_Security/PART_OVERVIEW.md) for OWASP (Open Worldwide
  Application Security Project) Top 10 coverage (owned there).

## 14. Observability

Log method, path, status code, latency, and a correlation ID
(`X-Request-Id`) per request at minimum; propagate the correlation ID through
every downstream hop. Full tracing/metrics patterns are owned by
[Observability](../12_Observability/PART_OVERVIEW.md).

## 15. Failure Scenarios

- **504 Gateway Timeout**: upstream service too slow — check whether it's a
  true backend slowdown or a misconfigured proxy timeout shorter than the
  backend's expected latency.
- **502 Bad Gateway**: upstream connection refused/reset — often a backend
  crash or health-check misconfiguration.
- **Connection pool exhaustion**: client-side symptom of slow/hanging
  backends; without a request timeout, one slow dependency can starve an
  entire pool.

## 16. Testing

- Contract tests against expected status codes and headers per endpoint.
- Fuzzing malformed headers/bodies to check for request-smuggling and crash
  resilience.
- Load testing with realistic keep-alive/connection-reuse patterns, not just
  raw requests-per-second with fresh connections each time.

## 17. Common Mistakes

- Using `GET` for state-changing operations, breaking caching and retry
  safety assumptions.
- Returning `200 OK` with an error payload in the body instead of the correct
  `4xx`/`5xx` status code, breaking generic HTTP-aware tooling.
- Setting overly aggressive `Cache-Control: no-store` everywhere "to be safe,"
  losing all CDN/browser caching benefit.

## 18. Best Practices

- Use the status code that most specifically matches the outcome, not just
  `200`/`400`/`500`.
- Make every `PUT`/`DELETE` genuinely idempotent at the server, not just by
  convention.
- Set explicit timeouts at every hop (client, proxy, server) rather than
  relying on defaults.

## 19. Anti-Patterns

- **Chatty APIs over HTTP/1.1** without connection reuse, forcing a new
  handshake per call.
- **Ignoring `Retry-After`** on `429`/`503` responses instead of backing off.
- **Overloading a single status code** (e.g. always `200`) to mean multiple
  different outcomes, forcing clients to parse the body to know what happened.

## 20. Trade-off Analysis

| Decision | Benefit | Cost |
|---|---|---|
| Terminate TLS at the edge vs. end-to-end | Simpler cert management, cheaper CPU on app servers | Internal network must be trusted |
| HTTP/2 vs HTTP/1.1 | Multiplexing, header compression | More complex server implementation, some middleboxes mishandle it |
| Aggressive caching | Lower origin load, lower latency | Stale-data risk if invalidation is wrong |

## 21. Comparison Table

| Version | Transport | Multiplexing | Header Compression | Typical Use Today |
|---|---|---|---|---|
| HTTP/1.1 | TCP | No (per-connection) | No | Legacy systems, simple internal services |
| HTTP/2 | TCP | Yes (stream-level) | HPACK | Most modern web/API traffic |
| HTTP/3 | QUIC (UDP) | Yes (no TCP head-of-line blocking) | QPACK | Mobile-heavy, high-latency/lossy networks |

## 22. Real-World Case Study

A CDN-fronted e-commerce product page serving cached HTML/JSON for anonymous
users (`Cache-Control: public, max-age=60`) while routing authenticated
cart/checkout calls (`Cache-Control: no-store`) straight to origin
demonstrates how HTTP's caching headers alone can offload the majority of
traffic from origin servers without any application-level caching layer.

## 23. Interview Questions

1. Why is `PUT` idempotent but `POST` is not, and why does that distinction
   matter for retries?
2. Walk through what changes at the transport level between HTTP/1.1, HTTP/2,
   and HTTP/3.
3. What's the difference between `304 Not Modified` and a `200 OK` served
   from a local browser cache?
4. How does HTTP/2 avoid the "6 connections per host" limitation seen in
   HTTP/1.1?
5. Why does TLS 1.3 need one fewer round trip than TLS 1.2?

## 24. Hands-on Exercises

Using the code samples in Section 10, capture a request/response with a
packet-capture tool (e.g. Wireshark) and identify: the TCP handshake, the TLS
handshake (if HTTPS), the HTTP request line, and the response status line.

## 25. Design Exercises

Design the caching strategy (headers, TTLs (Time To Live), invalidation
approach) for a news site's homepage, article pages, and a logged-in comment
API. Evaluation criteria: correctness of cacheability per endpoint,
invalidation approach, and origin-load reduction estimate.

## 26. Architecture Review Questions

- Does every hop (client, CDN, load balancer, service) have an explicit,
  intentional timeout?
- Are idempotent methods actually implemented idempotently at the server?
- Is TLS enforced everywhere, with no plaintext HTTP fallback reachable
  externally?
- Are cache headers set deliberately per endpoint, not left at framework
  defaults?

## 27. Summary

HTTP's request/response model, method semantics, status code taxonomy, and
caching headers are the shared vocabulary nearly every other protocol and
architecture pattern in this handbook builds on. Understanding *why* GET is
safe and cacheable, why PUT/DELETE must be idempotent, and how the TLS
handshake secures the channel before any of that vocabulary is exchanged, is
foundational — later chapters (REST, GraphQL, API Gateway, CDN) will recap and
link back here rather than re-deriving these fundamentals.

**Further reading**: [REST](../08_API_Architecture/CH01_REST.md) ·
[CDN](PART_OVERVIEW.md) · [API Gateway](../08_API_Architecture/PART_OVERVIEW.md) ·
[Observability](../12_Observability/PART_OVERVIEW.md)
