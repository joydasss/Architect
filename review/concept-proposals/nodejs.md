# Concept Proposals — Node.js Architecture (03_Software_Engineering_Foundations/CH03_Nodejs.md)

Staged per the Concept Ownership Rule in [STYLE_GUIDE.md](../../STYLE_GUIDE.md).
Suggested ownership for every concept below = this chapter (no existing owner
found in [CORE_CONCEPTS.md](../../CORE_CONCEPTS.md) at draft time).

| Concept | Scope note |
|---|---|
| Event Loop Phases (timers, pending callbacks, poll, check, close) | libuv's fixed-order phase cycle that determines when timer, I/O, `setImmediate`, and close callbacks each run |
| libuv Thread Pool | Background thread pool (default size 4) libuv uses for operations without native async OS primitives (some filesystem ops, `dns.lookup`, some `crypto` functions) |
| Single-Threaded Non-Blocking I/O Model | Node's core concurrency model: one JS thread, all I/O delegated asynchronously, so blocking work stalls the whole process |
| Microtask Queue vs. Macrotask Queue | The distinction between Promise/`process.nextTick` microtasks (drained between every callback) and event-loop-phase macrotasks, and the starvation risk when microtasks recurse unboundedly |
| V8 JIT Compilation Tiers (Ignition/TurboFan) | V8's tiered execution: bytecode interpretation first, adaptive optimizing compilation for hot, stable-shape functions, with deoptimization on broken assumptions |
| V8 Hidden Classes | V8's mechanism for giving dynamically-shaped JS objects fast, fixed-offset property access by sharing "shapes" across same-construction-pattern objects |
| V8 Garbage Collection Generations (Scavenge / Mark-Sweep-Compact) | V8's young/old generation heap split and the two collectors used for each, and its implications for allocation patterns and GC pause behavior |
| `worker_threads` Architecture | Node's true-parallelism primitive: separate V8 isolates/heaps per thread, message-passing via structured clone or `SharedArrayBuffer`/`Atomics` |
| `cluster` Module Architecture | Node's process-level fan-out primitive for scaling across CPU cores with per-worker fault isolation |
| CommonJS vs. ECMAScript Modules (ESM) Loading Semantics | Synchronous, eager `require()` resolution vs. static-graph-then-execute ESM resolution with live bindings |
| Dual-Package Hazard | The failure mode where a package loaded via both CJS and ESM paths resolves to two independent module instances, breaking singleton-holding libraries |
| `node_modules` Resolution Algorithm | The upward directory-walk algorithm Node uses to resolve bare-specifier `require()`/`import` calls |
| Phantom Dependencies (npm/Yarn hoisting) | Dependencies that resolve only due to flat/hoisted `node_modules` layout without being declared, and how pnpm's content-addressable + symlink store prevents this by construction |
| Streams and Backpressure | Node's chunked data-processing abstraction (Readable/Writable/Duplex/Transform) and the `highWaterMark`/`drain`-event protocol that bounds memory for large or unbounded payloads |
| Node.js Lightweight Process Model (Microservices-Friendliness) | Node's comparatively low per-instance memory/startup overhead and its architectural fit for microservices/horizontal scaling patterns |
| Event-Loop Lag as a Health Metric | Node-specific observability signal (measuring scheduling delay of a timer/`setImmediate`) that leading-indicates main-thread CPU blocking before broad latency degradation appears |
