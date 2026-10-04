# Part 05 — Networking and Operating Systems Topic Map

This map backfills the coverage contract for Part 05's 29 networking and operating-system chapters. The part covers protocols and host-level mechanisms that application and platform architects must reason about directly. It does not replace provider service catalogs or the higher-level architecture parts that compose these mechanisms.

## Part-wide ownership boundaries

- Part 05 owns network protocols and host operating-system mechanisms from HTTP through Linux internals, including transport, security protocols, proxies, sockets, memory, storage, scheduling, and containers.
- Part 08 owns API resource design and API product architecture; Part 09 owns cloud networking, security, compute, and storage products; Part 10 owns cloud workload composition; Part 12 owns Kubernetes orchestration and cluster APIs.
- Part 06 owns database internals and storage products. Part 07 owns distributed-systems design; Part 05 supplies the network and operating-system mechanisms those systems use.
- Protocol-specific chapters own wire and runtime mechanics; avoid re-teaching the same mechanism in adjacent chapters. Use explicit links for shared prerequisites such as DNS, TLS, HTTP, TCP, and OS process behavior.
- Validate behavior against current protocol specifications, operating systems, libraries, middleboxes, and deployment environments. Mark legacy protocols and implementation-specific features clearly.

## Cross-part stakeholders and assumptions

- Application architects need to understand latency, retries, connection lifetime, protocol choice, and failure boundaries.
- Platform and security teams need observable network paths, secure identity, enforceable policy, and safe host/runtime operation.
- Site reliability engineers (SREs) need packet, process, memory, I/O, and node evidence that narrows incidents without confusing symptoms across layers.
- Assume a reader understands basic programming and computer systems but may not know the protocol state machines or kernel paths in detail.
- Quality scenarios include a failing request traversing proxies and DNS; a TLS/certificate rotation without outage; port or memory exhaustion under load; a host-level isolation failure; and recovery from a network partition or node pressure event.

## Networking

### CH01 HTTP

**Reader outcome:** Explain HTTP request/response semantics and the browser/client-to-server transaction boundary.
**Coverage and evidence:** Methods, status codes, headers, representations, content negotiation, caching controls, connection reuse, intermediary behavior, and safe retry semantics. Verify with traces, headers, status behavior, and client/server captures.
**Boundaries:** CH04-05 own HTTP/2 and HTTP/3 transport changes; CH06 TLS owns handshake mechanics; Part 08 owns API design.
**Diagram opportunities:** (1) request/response message structure; (2) method and status decision flow; (3) cache freshness and validation; (4) proxy/header transformation path; (5) client retry and idempotency boundary.

### CH02 OSI Model

**Reader outcome:** Use the Open Systems Interconnection (OSI) model as a diagnostic vocabulary without mistaking layers for a literal implementation stack.
**Coverage and evidence:** Seven-layer responsibilities, encapsulation, mapping to TCP/IP, cross-layer dependencies, and layer-oriented troubleshooting. Use packet traces and observed failure location as evidence.
**Boundaries:** CH03 owns TCP/IP mechanisms; later protocol chapters own detailed wire behavior.
**Diagram opportunities:** (1) seven-layer encapsulation; (2) OSI-to-TCP/IP mapping; (3) packet headers added and removed across hosts; (4) symptom-to-layer diagnostic path; (5) cross-layer dependency example.

### CH03 TCP/IP

**Reader outcome:** Explain addressing, transport, connection state, reliability, congestion, and socket identity for Internet Protocol (IP) networks.
**Coverage and evidence:** IPv4/IPv6, subnetting, ports, TCP connection lifecycle, retransmission and flow/congestion control, User Datagram Protocol (UDP), NAT interaction, and ephemeral ports. Validate with packet captures, socket state, and latency/throughput data.
**Boundaries:** CH02 supplies layering vocabulary; CH16 owns socket API and multiplexing mechanics.
**Diagram opportunities:** (1) TCP/IP encapsulation and addressing; (2) TCP handshake and close states; (3) sliding-window and acknowledgment flow; (4) congestion response under loss; (5) four-tuple and ephemeral-port allocation.

### CH04 HTTP/2

**Reader outcome:** Evaluate HTTP/2 framing, multiplexing, and connection-level behavior for modern web traffic.
**Coverage and evidence:** Binary frames, streams, HPACK header compression, flow control, prioritization history, connection coalescing, and head-of-line effects. Measure stream concurrency, latency, and proxy behavior.
**Boundaries:** CH01 owns HTTP semantics; CH06 owns TLS; CH05 owns HTTP/3 and QUIC comparison.
**Diagram opportunities:** (1) frames multiplexed over one connection; (2) stream identifiers and lifecycle; (3) connection-level versus stream-level flow control; (4) header compression state; (5) loss blocking streams on a shared TCP connection.

### CH05 HTTP/3

**Reader outcome:** Explain HTTP/3's mapping onto QUIC and identify when its connection and stream behavior changes deployment outcomes.
**Coverage and evidence:** HTTP semantics over QUIC, stream mapping, connection migration, TLS 1.3 integration, UDP reachability, proxies, and fallback. Validate handshake, loss, migration, and middlebox behavior in representative networks.
**Boundaries:** CH18 owns QUIC transport internals; CH01 owns HTTP semantics; CH04 owns HTTP/2.
**Diagram opportunities:** (1) HTTP/3-to-QUIC stream mapping; (2) encrypted handshake sequence; (3) independent stream loss recovery; (4) connection migration across network change; (5) HTTP/2/3 negotiation and fallback.

### CH06 TLS

**Reader outcome:** Design Transport Layer Security (TLS) connections with clear trust, negotiation, encryption, and mutual-authentication boundaries.
**Coverage and evidence:** TLS 1.2/1.3 handshake, certificates, cipher negotiation, forward secrecy, Server Name Indication (SNI), Application-Layer Protocol Negotiation (ALPN), termination, and mutual TLS. Verify negotiated parameters, chain validation, and failure behavior.
**Boundaries:** CH15 owns certificate lifecycle and public-key infrastructure; CH07 frames obsolete Secure Sockets Layer (SSL) compatibility.
**Diagram opportunities:** (1) TLS 1.3 handshake messages; (2) trust-chain validation; (3) termination/re-encryption topologies; (4) SNI/ALPN route selection; (5) mutual TLS identity exchange.

### CH07 SSL

**Reader outcome:** Identify obsolete SSL and early TLS risks, explain protocol deprecation, and plan safe migration to supported transport security.
**Coverage and evidence:** SSL history, downgrade and implementation vulnerabilities, compatibility inventory, protocol/cipher scanning, deprecation windows, and isolate-and-bridge migration. Use handshake scans and client telemetry.
**Boundaries:** CH06 owns current TLS mechanics; CH15 owns certificates; Part 15 owns the general vulnerability-management process.
**Diagram opportunities:** (1) SSL-to-TLS evolution timeline; (2) downgrade attack path; (3) legacy-client inventory to migration stages; (4) monitor/block enforcement rollout; (5) compatibility bridge and removal decision.

### CH08 DNS

**Reader outcome:** Explain Domain Name System (DNS) delegation, resolution, caching, and security as an operational dependency of distributed applications.
**Coverage and evidence:** Zones, records, recursive/authoritative resolution, TTL and negative caching, DNSSEC, split-horizon and traffic steering. Diagnose with resolver traces, authoritative answers, and cache state.
**Boundaries:** CH09 owns content delivery; CH10 owns load balancing; application service discovery belongs to the consuming platform.
**Diagram opportunities:** (1) recursive resolution and delegation; (2) positive/negative cache timeline; (3) DNSSEC chain of trust; (4) split-horizon query path; (5) health-aware answer and failover delay.

### CH09 CDN

**Reader outcome:** Design a Content Delivery Network (CDN) path that improves edge latency while preserving cache correctness, security, and origin resilience.
**Coverage and evidence:** Edge/origin topology, cache keys, freshness and invalidation, dynamic versus static content, TLS, shielding, edge compute, and regional routing. Validate hit ratio, origin load, stale behavior, and purge propagation.
**Boundaries:** CH08 owns DNS; CH10 owns load balancing; CH11 owns reverse-proxy mechanics.
**Diagram opportunities:** (1) client-edge-origin request path; (2) cache-key and Vary decision; (3) TTL/revalidation/invalidation timeline; (4) origin shield and regional failover; (5) edge security and request-filtering path.

### CH10 Load Balancer

**Reader outcome:** Select and operate Layer 4/Layer 7 load balancing, health checking, and traffic distribution for an explicit failure and scaling model.
**Coverage and evidence:** Algorithms, target registration, health checks, connection draining, persistence, TLS termination, overload behavior, and global/regional designs. Measure distribution, backend health, and failover convergence.
**Boundaries:** CH11 owns reverse-proxy application-layer behavior; CH08 owns DNS steering; Part 09 owns provider load-balancer products.
**Diagram opportunities:** (1) frontend-to-backend topology; (2) algorithm distribution under uneven requests; (3) health-check state and pool membership; (4) drain and connection lifecycle; (5) zonal/global failover path.

### CH11 Reverse Proxy

**Reader outcome:** Use reverse proxies to control routing, TLS, headers, buffering, and backend protection while keeping their ownership distinct from load balancing and API gateways.
**Coverage and evidence:** Proxy termination, host/path routing, header rewriting, buffering, retries, timeouts, caching, upstream pools, and trust headers. Validate request identity, timeout budgets, and retry amplification.
**Boundaries:** CH10 owns load-balancer algorithms; Part 08 owns API gateway policy; CH06 owns TLS negotiation.
**Diagram opportunities:** (1) client-to-proxy-to-upstream request path; (2) routing rule precedence; (3) TLS termination/re-encryption; (4) timeout/retry propagation; (5) trusted versus untrusted forwarded headers.

### CH12 NAT

**Reader outcome:** Explain Network Address Translation (NAT) state, mapping, address exhaustion, and its interaction with routing and security boundaries.
**Coverage and evidence:** SNAT/DNAT, connection tracking, port allocation, hairpin behavior, carrier-grade NAT, NAT gateways, traversal techniques, and failure capacity. Inspect conntrack state and port usage.
**Boundaries:** CH03 owns IP and transport fundamentals; CH14 owns firewall policy; Part 09 owns provider NAT products.
**Diagram opportunities:** (1) source/destination translation; (2) conntrack tuple lifecycle; (3) ephemeral-port exhaustion; (4) inbound port-forward path; (5) NAT traversal and relay fallback.

### CH13 VPN

**Reader outcome:** Choose a Virtual Private Network (VPN) topology and trust model for remote access or site connectivity.
**Coverage and evidence:** Tunnel encapsulation, IPsec/TLS-based approaches, routing, authentication, split/full tunnel, key rotation, MTU, and high availability. Verify routes, negotiated parameters, and failover.
**Boundaries:** CH06 owns TLS; CH12 owns NAT traversal; Part 09 owns cloud VPN services.
**Diagram opportunities:** (1) site-to-site tunnel and route exchange; (2) remote-access identity and traffic path; (3) split versus full tunnel; (4) tunnel failover; (5) encapsulation and MTU overhead.

### CH14 Firewalls

**Reader outcome:** Build stateful and stateless firewall policies that enforce intended trust zones without obscuring traffic ownership.
**Coverage and evidence:** Packet filters, connection state, rule ordering, default-deny, network segmentation, web application filtering, shadowed rules, and policy review. Validate with flow logs and negative-path tests.
**Boundaries:** CH12 owns NAT; CH13 owns VPN; CH06 owns TLS; Part 15 owns security foundations.
**Diagram opportunities:** (1) trust-zone segmentation; (2) stateful connection lifecycle; (3) first-match rule evaluation; (4) shadowed-rule detection; (5) monitor-to-enforce rollout.

### CH15 Certificates

**Reader outcome:** Manage certificate issuance, trust, rotation, and revocation as an operational lifecycle rather than a one-time TLS configuration.
**Coverage and evidence:** X.509 structure, certificate authorities, chain validation, renewal, revocation, OCSP, ACME, private PKI, workload identity, and key custody. Track expiry and test rotation.
**Boundaries:** CH06 owns TLS handshake mechanics; CH08 owns DNS CAA; Part 15 owns security governance.
**Diagram opportunities:** (1) root/intermediate/leaf trust chain; (2) issuance and renewal lifecycle; (3) expiry detection and rotation; (4) revocation/OCSP validation; (5) workload certificate identity issuance.

### CH16 Sockets

**Reader outcome:** Use the socket API and I/O multiplexing models to reason about connection servers, file descriptors, and concurrency limits.
**Coverage and evidence:** Berkeley socket lifecycle, bind/listen/accept, blocking/non-blocking I/O, select/poll/epoll/kqueue, reactor patterns, backlog, reuse options, and descriptor exhaustion. Inspect socket state and event-loop load.
**Boundaries:** CH03 owns TCP/UDP protocol behavior; Part 05 CH24 owns process/thread mechanics; CH17 owns WebSocket framing.
**Diagram opportunities:** (1) socket lifecycle state machine; (2) blocking versus non-blocking server; (3) epoll readiness notification; (4) reactor event dispatch; (5) descriptor/backlog exhaustion path.

### CH17 WebSockets

**Reader outcome:** Design persistent bidirectional connections with explicit upgrade, authentication, routing, backpressure, reconnection, and scaling behavior.
**Coverage and evidence:** HTTP upgrade, framing, ping/pong, connection state, load-balancer affinity, horizontal scale, fan-out, backpressure, and reconnect storms. Measure active connections, queue depth, and disconnect causes.
**Boundaries:** CH16 owns socket primitives; CH01 owns HTTP semantics; CH10/11 own balancing and proxying.
**Diagram opportunities:** (1) upgrade handshake and connection lifecycle; (2) bidirectional frame exchange; (3) fan-out/backplane topology; (4) reconnect with backoff; (5) slow consumer and backpressure.

### CH18 QUIC

**Reader outcome:** Explain Quick UDP Internet Connections (QUIC) transport and identify its effects on connection setup, loss recovery, migration, and load balancing.
**Coverage and evidence:** UDP-based encrypted transport, integrated TLS 1.3, stream multiplexing, connection IDs, migration, congestion control, 0-RTT, and deployment overhead. Use qlog/packet evidence and handshake metrics.
**Boundaries:** CH05 owns HTTP/3 mapping; CH06 owns TLS primitives; CH03 owns TCP/IP foundations.
**Diagram opportunities:** (1) QUIC connection establishment; (2) independent stream loss recovery; (3) connection-ID migration; (4) 0-RTT replay boundary; (5) connection-aware load-balancer routing.

### CH19 OAuth

**Reader outcome:** Select and implement OAuth authorization grants according to client type, trust, and delegated-access requirements.
**Coverage and evidence:** Roles, authorization code with PKCE, client credentials, scopes, consent, tokens as opaque credentials, refresh-token rotation, threat model, and client types. Validate redirect, audience, scope, and revocation paths.
**Boundaries:** CH20 owns OpenID Connect identity; CH21 owns JSON Web Token format; CH06/15 own TLS/certificates.
**Diagram opportunities:** (1) authorization-code flow with PKCE; (2) client-credentials machine flow; (3) refresh rotation and reuse detection; (4) scope/consent authority boundary; (5) browser/backend-for-frontend token custody.

### CH20 OIDC

**Reader outcome:** Integrate authentication using OpenID Connect (OIDC) while validating issuer, audience, nonce, keys, sessions, and logout behavior.
**Coverage and evidence:** Discovery, ID/access tokens, authorization code, PKCE, claims, JWKS rotation, relying-party sessions, logout, and federation. Verify issuer and claim validation and distinguish identity from authorization.
**Boundaries:** CH19 owns OAuth authorization; CH21 owns JWT encoding/validation mechanics; CH22 owns SAML.
**Diagram opportunities:** (1) authorization-code login and ID-token validation; (2) discovery/JWKS key rotation; (3) identity claim mapping; (4) RP session and logout; (5) federation trust boundary.

### CH21 SAML

**Reader outcome:** Operate Security Assertion Markup Language (SAML) federation and assertion handling for enterprise single sign-on.
**Coverage and evidence:** Identity provider/service provider roles, metadata, signed assertions, bindings, audience/recipient, replay protection, attribute mapping, session behavior, and certificate rollover. Validate trust metadata and clock assumptions.
**Boundaries:** CH19/20 own OAuth/OIDC; CH15 owns certificate lifecycle; Part 15 owns identity security foundations.
**Diagram opportunities:** (1) service-provider initiated SSO; (2) identity-provider initiated flow; (3) assertion signature and validation; (4) attribute mapping into application roles; (5) metadata/certificate rollover.

### CH22 JWT

**Reader outcome:** Validate JSON Web Tokens (JWTs) safely and avoid treating encoded claims as trusted authorization without signature and claim checks.
**Coverage and evidence:** Compact serialization, JWS/JWE distinction, signing algorithms, key discovery, issuer/audience/time claims, token lifetime, revocation, and implementation hazards. Test malformed, stale, wrong-audience, and key-rotation cases.
**Boundaries:** CH19 OAuth and CH20 OIDC own protocol flows; this chapter owns token format and validation mechanics.
**Diagram opportunities:** (1) JWT compact segments; (2) signing and verification; (3) claim validation gates; (4) key rotation and cached keys; (5) token compromise and revocation options.

### CH23 PingFederate

**Reader outcome:** Evaluate PingFederate as an identity-federation hub and understand adapters, attribute mapping, deployment, and migration responsibilities.
**Coverage and evidence:** Federation topology, identity-provider/service-provider connections, adapters, connectors, attribute mapping, clustering, migration abstraction, and operational ownership. Validate failover, mapping consistency, and partner compatibility.
**Boundaries:** CH19-22 own OAuth/OIDC/SAML/JWT fundamentals; Part 09 owns provider identity services; Part 15 owns general security governance.
**Diagram opportunities:** (1) federation hub and relying parties; (2) adapter/connector request path; (3) attribute transformation pipeline; (4) clustered high-availability topology; (5) migration from legacy identity to federated flows.

## Operating Systems

### CH24 Processes and Threads

**Reader outcome:** Explain process/thread execution, scheduling, synchronization, and inter-process communication as the operating-system foundation for services.
**Coverage and evidence:** Process lifecycle, threads, context switching, scheduling, IPC, mutexes/condition variables, races, deadlocks, and priority inversion. Diagnose with process state, thread dumps, and contention evidence.
**Boundaries:** CH16 owns socket multiplexing; CH25 owns memory; Part 03 owns language-runtime concurrency applications.
**Diagram opportunities:** (1) process/thread address-space relationships; (2) lifecycle and scheduling states; (3) IPC mechanism comparison; (4) lock-order deadlock; (5) context-switch and contention path.

### CH25 Memory Management

**Reader outcome:** Diagnose virtual memory, paging, caching, allocation, and memory pressure across process and container boundaries.
**Coverage and evidence:** Address spaces, page tables, TLBs, page faults, page cache, swapping, OOM handling, cgroups, copy-on-write, fragmentation, and NUMA. Correlate process and cgroup counters with latency and kill events.
**Boundaries:** CH26 owns filesystem persistence; CH28 owns virtualization/cgroups and container isolation in broader context; Part 12 owns Pod resource API semantics.
**Diagram opportunities:** (1) virtual-to-physical address translation; (2) page fault and reclaim path; (3) page cache and filesystem read; (4) cgroup memory limit to OOM action; (5) NUMA placement and access latency.

### CH26 File Systems

**Reader outcome:** Explain file-system namespaces, durability, caching, and storage semantics that affect application correctness and operations.
**Coverage and evidence:** Files, directories, metadata, page cache, writeback, fsync/rename durability, mounts, NFS, inode/block allocation, and failure modes. Validate persistence guarantees and mount behavior under node loss.
**Boundaries:** CH25 owns virtual memory/page cache mechanics; Part 06 owns database storage engines; CH28 owns mount namespaces and container filesystems.
**Diagram opportunities:** (1) pathname lookup and inode mapping; (2) write-buffer/fsync durability sequence; (3) page-cache read/write path; (4) network file-system consistency; (5) mount namespace and container path view.

### CH27 I/O and Scheduling

**Reader outcome:** Analyze CPU scheduling, asynchronous I/O, block-device queues, and resource controls as latency and throughput decisions.
**Coverage and evidence:** I/O stack, synchronous/asynchronous models, io_uring, CPU scheduler behavior, affinity, real-time scheduling, cgroup CPU/I/O limits, and saturation metrics. Use queue depth, utilization, throttling, and wait time.
**Boundaries:** CH24 owns process/thread synchronization; CH16 owns network socket multiplexing; CH25 owns memory pressure.
**Diagram opportunities:** (1) application-to-device I/O stack; (2) synchronous versus asynchronous completion; (3) CPU run queue and preemption; (4) cgroup throttling/noisy-neighbor effect; (5) queue depth and latency response.

### CH28 Virtualization and Container Fundamentals

**Reader outcome:** Compare virtual machines and containers by isolation boundary, resource control, image construction, and operational lifecycle.
**Coverage and evidence:** Hypervisors, namespaces, cgroups, container images/layers, runtimes, Linux capabilities, filesystem mounts, and orchestration boundary. Validate host-kernel exposure and runtime assumptions.
**Boundaries:** CH25/26 own detailed memory/filesystem mechanics; Part 12 owns Kubernetes orchestration; Part 09 owns provider container products.
**Diagram opportunities:** (1) VM versus container isolation stack; (2) namespace/cgroup resource boundary; (3) image layers and writable container layer; (4) container runtime lifecycle; (5) host-kernel compromise boundary.

### CH29 Linux Internals for Architects

**Reader outcome:** Use Linux process, memory, I/O, networking, and observability evidence to diagnose production behavior across service and container boundaries.
**Coverage and evidence:** Kernel/user boundary, `/proc` and `/sys`, cgroups, scheduler/resource pressure, system calls, file descriptors, namespaces, tracing tools, and incident triage. Correlate host counters with application symptoms.

**Boundaries:** CH24-28 own detailed process, memory, filesystem, scheduling, and container mechanics; CH29 synthesizes them for architecture-level diagnosis.

**Diagram opportunities:** (1) user/kernel request path; (2) symptom-to-subsystem diagnostic tree; (3) process/cgroup/node resource correlation; (4) tracing/metrics/log evidence chain; (5) container-to-host boundary investigation.
