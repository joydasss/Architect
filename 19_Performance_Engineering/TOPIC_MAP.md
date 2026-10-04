# Part 19 — Performance Engineering Topic Map

This map defines coverage for Part 19's fourteen performance-engineering chapters. The part connects workload objectives to measurement, bottleneck analysis, optimization, and operational validation. It distinguishes improving a system from merely producing a faster benchmark.

## Part-wide ownership boundaries

- Part 19 owns provider-neutral performance methods, measurement, bottleneck diagnosis, and workload-level optimization.
- Part 05 owns CPU, memory, networking, and OS mechanisms; Part 06 owns database internals; Part 09 owns provider performance products; Part 12 owns Kubernetes resource and autoscaling behavior; Part 14 owns telemetry platforms.
- State workload, environment, SLO, data set, and confidence for every performance claim. Optimize the measured bottleneck, then retest for bottleneck migration and correctness.

## Cross-part stakeholders and scenarios

Application teams need latency/throughput evidence; platform teams need capacity and cost behavior; users need objective-level improvements. Scenarios include a p99 latency regression, memory pressure under a container limit, a pool saturation cascade, a cache stampede, and an optimization that improves throughput but violates fairness or freshness.

## Chapters

### CH01 Caching

**Reader outcome:** Choose cache placement and consistency policy from reuse, latency, freshness, and failure requirements.
**Coverage:** Cache-aside/read-through/write-through/write-behind, eviction, TTL, invalidation, stampedes, and measurement.
**Boundaries:** Part 06 CH09 owns database/application cache patterns; Part 05 CH09 owns CDN behavior.
**Diagram opportunities:** (1) cache-aside request path; (2) invalidation/staleness race; (3) stampede collapse; (4) eviction policy under pressure; (5) cache hit-rate versus freshness trade-off.

### CH02 CDN (Content Delivery Network)

**Reader outcome:** Optimize edge delivery with cache correctness and measurable origin/load-latency trade-offs.
**Coverage:** Edge caching, cache key, freshness, invalidation, shielding, dynamic content, and origin performance.
**Boundaries:** Part 05 CH09 owns CDN protocol mechanics; Part 09 owns provider CDN services.
**Diagram opportunities:** (1) edge-origin path; (2) cache-key decision; (3) TTL/revalidation; (4) shield/origin load; (5) regional latency and cache-hit trade-off.

### CH03 Compression

**Reader outcome:** Select compression methods and thresholds using bandwidth, CPU, latency, and payload characteristics.
**Coverage:** Text/binary compression, codecs, content negotiation, streaming, compression ratio, CPU cost, and security side channels.
**Boundaries:** Part 05 owns HTTP compression negotiation; this chapter owns workload-level performance selection.
**Diagram opportunities:** (1) compress/decompress request path; (2) size-versus-CPU curve; (3) streaming compression; (4) codec selection matrix; (5) compression side-channel boundary.

### CH04 Memory Performance

**Reader outcome:** Diagnose memory allocation, working set, locality, garbage collection, and pressure effects on latency and throughput.
**Coverage:** Allocation rate, heap/working set, locality, garbage collection, paging, memory bandwidth, and container constraints.
**Boundaries:** Part 05 CH25 owns OS memory mechanics; Part 03 owns language runtime details.
**Diagram opportunities:** (1) allocation-to-collection path; (2) working-set pressure; (3) locality/cache hierarchy; (4) memory limit to eviction/OOM; (5) throughput/latency under GC pressure.

### CH05 CPU Performance

**Reader outcome:** Identify CPU bottlenecks and optimize computation, parallelism, scheduling, and instruction-level efficiency.
**Coverage:** CPU utilization, parallelism, contention, context switching, vectorization, profiling, throttling, and capacity.
**Boundaries:** Part 05 CH27 owns OS scheduling; Part 03 owns language runtime concurrency.
**Diagram opportunities:** (1) CPU demand and run queue; (2) parallel speedup/serial fraction; (3) contention and context switching; (4) throttling under quota; (5) CPU bottleneck migration after optimization.

### CH06 Latency

**Reader outcome:** Measure and budget end-to-end latency, including queues, dependencies, tails, and user-visible objectives.
**Coverage:** Percentiles, queueing, Little's Law, critical paths, fan-out, timeouts, tail amplification, and latency budgets.
**Boundaries:** Part 07 owns general distributed failure semantics; Part 14 owns observability platforms.
**Diagram opportunities:** (1) end-to-end latency budget; (2) fan-out tail amplification; (3) queue depth and response time; (4) timeout propagation; (5) percentile distribution and objective breach.

### CH07 Profiling

**Reader outcome:** Collect representative profiles and use them to locate CPU, memory, I/O, or lock hot spots.
**Coverage:** Sampling/instrumentation, flame graphs, CPU/heap/lock profiles, overhead, production safety, and before/after comparison.
**Boundaries:** Part 05 owns OS tracing primitives; this chapter owns profiling workflow and interpretation.
**Diagram opportunities:** (1) profiler data collection; (2) call-stack flame graph; (3) sampling overhead trade-off; (4) profile-to-code diagnosis; (5) before/after profile comparison.

### CH08 Benchmarking

**Reader outcome:** Design repeatable benchmarks that predict production behavior and expose uncertainty.
**Coverage:** Workload models, warmup, steady state, variance, load generation, saturation, open/closed-loop tests, and statistical comparison.
**Boundaries:** Part 14 owns production telemetry; this chapter owns controlled performance experiments.
**Diagram opportunities:** (1) benchmark lifecycle; (2) open versus closed workload model; (3) warmup/steady-state phases; (4) load-to-saturation curve; (5) confidence interval comparison.

### CH09 GC (Garbage Collector) Tuning

**Reader outcome:** Tune managed runtimes from allocation, pause, throughput, and heap evidence rather than collector folklore.
**Coverage:** Generational/region collectors, allocation, pause goals, heap sizing, concurrent collection, and tuning experiments.
**Boundaries:** Part 03 owns JVM/Python/Go runtime details; Part 05 owns OS memory mechanics.
**Diagram opportunities:** (1) object generations and promotion; (2) mark/sweep/compact lifecycle; (3) pause versus concurrent work; (4) heap sizing and pressure; (5) tuning experiment decision loop.

### CH10 Connection Pools

**Reader outcome:** Size and operate connection pools to balance setup cost, concurrency, queueing, and downstream capacity.
**Coverage:** Pool lifecycle, max/min sizes, timeout, queueing, leak detection, database/client pools, and cascading saturation.
**Boundaries:** Part 06 owns database connection mechanics; Part 08 owns API rate-limit contracts.
**Diagram opportunities:** (1) request-to-pool-to-dependency path; (2) queue saturation; (3) pool size versus downstream capacity; (4) leak/starvation lifecycle; (5) timeout/retry amplification.

### CH11 Thread Pools

**Reader outcome:** Configure worker pools around service time, queue limits, CPU/I/O mix, and overload behavior.
**Coverage:** Fixed/dynamic pools, queue policies, rejection, work stealing, blocking tasks, sizing, and context propagation.
**Boundaries:** Part 05 CH24/27 own thread/scheduler mechanics; Part 03 owns runtime-specific executors.
**Diagram opportunities:** (1) producer-worker-queue; (2) pool saturation and rejection; (3) CPU-bound versus I/O-bound sizing; (4) queue bound and backpressure; (5) cancellation/context propagation.

### CH12 Database Optimization

**Reader outcome:** Improve database-facing performance by locating expensive plans, access paths, contention, and data-shape mismatches.
**Coverage:** Query plans, indexes, statistics, connection behavior, locks, caching, batching, and workload measurement.
**Boundaries:** Part 06 owns deep database/query-engine mechanics; Part 19 owns cross-engine performance method.
**Diagram opportunities:** (1) query request-to-plan-to-storage path; (2) scan versus index plan; (3) N+1 versus batch; (4) lock contention; (5) database bottleneck diagnosis tree.

### CH13 Network Optimization

**Reader outcome:** Reduce network latency and resource cost through protocol, payload, connection, and topology decisions.
**Coverage:** RTT, connection reuse, multiplexing, compression, batching, fan-out, bandwidth, packet loss, and placement.
**Boundaries:** Part 05 owns protocol/network mechanisms; Part 09 owns provider connectivity products.
**Diagram opportunities:** (1) request RTT budget; (2) connection reuse versus handshake; (3) fan-out latency; (4) payload compression trade-off; (5) network bottleneck localization.

### CH14 Frontend Optimization

**Reader outcome:** Improve perceived and measured browser performance across critical rendering, JavaScript execution, assets, and interaction.
**Coverage:** Core Web Vitals, loading/rendering, code splitting, caching, image/font delivery, main-thread work, and measurement.
**Boundaries:** Part 04 owns frontend technologies; Part 05 owns HTTP/CDN protocols.
**Diagram opportunities:** (1) browser critical rendering path; (2) bundle split and lazy load; (3) main-thread task blocking; (4) asset caching/edge delivery; (5) user-centric metric to optimization loop.
